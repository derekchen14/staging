import os, pdb, sys
import json 
import openai
import backoff
import time

from argparse import Namespace
import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm as progress_bar

from database.db_utils.for_annotation import fake_tab_col
from backend.components.helpers import StorageDB, APICaller
from backend.components.context import Context
from backend.modules.nlu import NatLangUnderstanding
from backend.prompts.for_nlu import operations_prompt

DESIRED_DACTS = ["filter + group", "group + sort", "filter + sort", "clean", "delete", 
  "filter + group + sort", "filter", "group", "sort", "visualize"]

def state_to_string(tables, columns, aggregation, operations):
  representation = short_rep(tables, columns)
  pred_operations = ", ".join(operations)
  pred_agg = aggregation if len(aggregation) > 0 else "None"
  pred_ops = ", ".join(operations) if len(operations) > 0 else "None"
  return f"{representation}\n* Aggregation: {pred_agg}\n* Operations: {pred_ops}"

def short_rep(tables, columns):
  pred_tables = ", ".join(tables)
  columns_strings = []
  for table, cols in columns.items():
    col_str = ", ".join(cols) + f" in {table}"
    columns_strings.append(col_str)
  pred_columns = "; ".join(columns_strings)
  return f"* Tables: {pred_tables}\n* Columns: {pred_columns}"

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def completions_with_backoff(messages):
  completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.2,
  )
  raw_generation = completion.choices[0].message.content
  pred_output = raw_generation.strip()
  return pred_output

def construct_prompt(convo):
  speakers = ["Manager", "Analyst"]
  converted = []
  for i in range(2):
    speaker = speakers[i]
    text = convo['turns'][i]['text']
    converted.append(f"{speaker}: {text}")

  chat_string = "\n".join(converted)
  prompt = fake_tab_col.format(chat=chat_string)
  return prompt

def get_table_and_columns(convo):
  # given the 3-turn conversation, return a list of tables and a dict of columns
  prompt = construct_prompt(convo)
  messages = [{"role": "user", "content": prompt}]
  generated_output = completions_with_backoff(messages)
  prediction = generated_output.split(':')[1]

  tables = set()
  columns = defaultdict(list)

  for pred in prediction.strip().split(';'):
    try:
      col, table = pred.split('in')
      table, col = table.strip(), col.strip()
    except(ValueError):
      col, table = 'error', 'error'

    tables.add(table)
    columns[table].append(col)

  return list(tables), columns

def get_label(convo, turn_counter):
  if turn_counter == 1:  # first turn
    results = label_single_turn(convo[0])
  elif turn_counter == 3:
    results = label_multi_turn(convo)
  return results

def build_state_string(user_turn, agent_text, tables, columns):
  aggregation = user_turn['aggregation']
  operations = user_turn['operations']
  last_state = state_to_string(tables, columns, aggregation, operations)
  prev_state_str = f"Previous state:\n{last_state}\n* Agent utterance: {agent_text}"
  return prev_state_str

def annotate_conversations(convos, nlu, context):
  conversations = []
  speakers = ['User', 'Agent', 'User']

  for cid, convo in progress_bar(enumerate(convos), total=len(convos)):
    time.sleep(3)
    turns = []
    turn_counter = 1
    prev_state = "Previous state: None"
    fake_table, fake_columns = '', ''

    for text, speaker in zip(convo, speakers):
      if turn_counter == 2:
        tab_col = get_table_and_columns(convo)
        prev_state = build_state_string(new_turn, text, *tab_col)

      new_turn = {
        'utt_id': turn_counter,
        'speaker': speaker,
        'text': text
      }
      if speaker == 'User':
        intent, dact_string, agg, ops = nlu.external_predict(text, prev_state, context)
        new_turn['intent'] = intent
        new_turn['dact'] = dact_string
        new_turn['aggregation'] = agg
        new_turn['operations'] = ops
        """
        print(new_turn['speaker'], ":", new_turn['text'])
        for key, value in new_turn.items():
          if key in ["aggregation", "operations"]:
            if len(value) > 0:
              print(f"{key}: {value}")
          elif key in ["intent", "dact"]:
            print(f"{key}: {value}")"""

      turns.append(new_turn)
      turn_counter += 1

    conversation = {
      'convo_id': cid+1,
      'turns': turns
    }
    conversations.append(conversation)

    if len(conversations) > 2 and len(conversations) % 50 == 0:
      json.dump(conversations, open('database/annotations/conversations.json', 'w'), indent=4)

  return conversations

def repair_conversation(convo):
  time.sleep(3)

  for turn in convo['turns']:
    if turn['utt_id'] == 1:
      prev_state = "Previous state: None"
    elif turn['utt_id'] == 2:
      continue
    elif turn['utt_id'] == 3:
      table, columns = get_table_and_columns(convo)
      prev_state = build_state_string(turn, convo['turns'][1]['text'], table, columns)

    prompt = operations_prompt.format(previous_state=prev_state, utterance=turn['text'])
    messages = [{"role": "user", "content": prompt}]
    generated_output = completions_with_backoff(messages)
    carry_pred, agg_pred, op_pred = generated_output.split('\n')

    carry = carry_pred.strip().lower().startswith("t")
    agg_pred = agg_pred.split(':')[1]
    aggregation = agg_pred.strip()

    op_preds = op_pred.split(': ')[1]
    op_list = [op.strip() for op in op_preds.split(",")]
    operations = [op for op in op_list if NatLangUnderstanding.valid_operation(op)]
    turn['aggregation'] = aggregation
    turn['operations'] = operations
  return convo

def revise_conversations(trimmed, convos):
  all_convos = []
  for convo in progress_bar(convos, total=len(convos)):
    cid = convo['convo_id']

    match = False
    for t_conv in trimmed:
      tid = t_conv['convo_id']
      if cid == tid:
        match = True

    if match:
      repaired = repair_conversation(convo)
      all_convos.append(repaired)
    else:
      all_convos.append(convo)
  return all_convos

def filter_for_last_campaign(convos):
  trimmed = []
  for convo in convos:
    active = False
    for turn in convo['turns']:
      if turn['speaker'] == 'Agent':
        continue
      if len(turn['operations']) > 0 and turn['operations'][0] == "filter for last campaign":
        active = True
    if active:
      trimmed.append(convo)
  return trimmed  # 135 out of 160 are broken!

if __name__ == '__main__':
  args = Namespace(api_version='gpt-4', temperature=0.1, threshold=0.6, drop_rate=0.1, level='cosine', verbose=False)
  # api = APICaller(args)
  # storage = StorageDB(args)
  # context = Context(args)
  # nlu = NatLangUnderstanding(args, api, storage)

  convos = json.load(open('database/annotations/conversations.json', 'r'))
  trimmed = filter_for_last_campaign(convos)
  annotated = revise_conversations(trimmed, convos)
  # annotated = annotate_conversations(trimmed, nlu, context)

  json.dump(annotated, open('database/annotations/conversations2.json', 'w'), indent=4)
  print(f"Done! Annotated {len(annotated)} conversations.")