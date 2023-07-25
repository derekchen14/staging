import os, pdb, sys
import json 
import openai
import backoff

import random
import numpy as np
from collections import defaultdict
from db_utils.for_annotation import *
from tqdm import tqdm as progress_bar

DESIRED_DACTS = ["filter + group", "group + sort", "filter + sort", "clean", "delete", 
  "filter + group + sort", "filter", "group", "sort", "visualize"]


desc = {
  "describe": "occurs when the user wants to know more about the available columns or other meta-data",
  "filter": "means to limit the rows returned to match a criteria or range of values",
  "group": "is segmenting or grouping the data in some fashion, including pivot tables",
  "sort": "refers to sorting a column to establish order or ranking, frequently to find top values",
  "plan": "means projecting into possible futures that are not strictly based on information inside the table",
  "analyze": "is to perform exploratory analysis where table details are not well specified",
  "clean": "is changing, updating or creating data, either from a direct command or based on values from other cells through a formula",
  "delete": "is removing or hiding rows or columns, often based on some criteria",
  "format": "means styling the contents of the table, such as resizing column width, converting strings to numbers, or centering text",
  "visualize": "means creating a figure, chart or diagram from the data",
  "style": "is any design or formatting elements to update an existing figure or chart",
  "explain": "is to write out any text, such as summarizing information presented within a figure",
  "chat": "is talking about non-data related subjects.  Answers may be based on opinion and may change from one person to another.  Also includes backchanneling, such as acknowledging progress or expressing dissatisfaction. ",
  "help": "is getting a better understanding of what the service entails, answering questions found in a FAQ.  Unlike 'chat', the answers to 'help' questions are broadly applicable to all customers.",
  "inquire": "is asking for clarification about what the agent said or did. These utterances always include a target entity for inquiry.",
}

label_prompt = """Given an utterance spoken by a marketing manager, generate the response from the data analyst and the follow-up from the manager.
Analyst responses typically short.  They should not repeat what the manager said and should NOT mimic the same pattern.
Real chats are short and conversational, including co-reference, clarification and sentence fragments. Do not talk about trend lines.

For example,
{preamble}"""

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def completions_with_backoff(messages):
  completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.6,
  )
  raw_generation = completion.choices[0].message.content
  pred_output = raw_generation.strip()
  return pred_output

def valid_operation(op):
  return (op.startswith("filter")) or (op.startswith("group")) or (op.startswith("sort"))

def derived_table(dact):
  return ("filter" in dact) or ("group" in dact) or ("sort" in dact)

def construct_prompt(text, exemplars):
  sections = []
  for exemplar in exemplars:
    try:
      texts_only = [x['text'] for x in exemplar['turns']]
    except(TypeError):
      print(exemplar)
      pdb.set_trace()

    section = "#############\n"
    section += insert_speakers(texts_only)
    sections.append(section)
  
  preamble = "\n\n".join(sections)
  preamble += "\n\n#############\n"
  preamble += f"Manager: {text}"
  prompt = label_prompt.format(preamble=preamble)
  return prompt

def insert_speakers(convo):
  converted = []
  speakers = ["Manager", "Analyst", "Manager"]
  for i in range(3):
    speaker = speakers[i]
    text = convo[i]
    converted.append(f"{speaker}: {text}")
  return "\n".join(converted)

def parse_output(generated_output, seed_text):
  parsed_examples = []

  sections = generated_output.split("#############")
  sec_id = 0
  for section in sections:
    new_convo = []
    if sec_id == 0:
      new_convo.append(seed_text)

    try:
      for line in section.split("\n"):
        line.strip()
        speaker, text = line.split(": ")
        new_convo.append(text.strip())
    except(ValueError):
      print(section)
      break

    if len(new_convo) == 3:
      parsed_examples.append(new_convo)
    sec_id += 1

  return parsed_examples

def talk_together(conversations, samples):
  print("Starting annotation ...")

  for idx, sample in enumerate(samples):
    dact, text = sample["dact"], sample["text"]
    exemplars = random.sample(conversations, 7)
    prompt = construct_prompt(text, exemplars)

    messages = [{"role": "system", "content": "We are witnessing a conversation between a marketing manager and a data analyst cleaning and analyzing data within a shared spreadsheet.\nRemember that real conversations are concise."},
      {"role": "user", "content": prompt}]
    generated_output = completions_with_backoff(messages)
    parsed_examples = parse_output(generated_output, text)

    print(f">>>>>>>>>>>>> {idx+1} of {len(samples)} >>>>>>>>>>>>")
    for convo in parsed_examples:
      converted = insert_speakers(convo)
      print(converted)
      decision = input("Accept: ")
      if decision in ["y", "yes", "j"]:
        conversations.append(convo)
  return conversations  

def sample_dacts(conversations, data, count):
  existing = []
  for convo in conversations:
    for turn in convo["turns"]:
      if turn['speaker'] == 'User':
        existing.append(turn['text'])

  if len(DESIRED_DACTS) > 0:
    samples = []
    while len(samples) < count:
      candidates = np.random.choice(data, 5, replace=False)
      for cand in candidates:
        if cand["text"] in existing:
          continue
        if cand["dact"] in DESIRED_DACTS:
          samples.append(cand)
  else:
    samples = np.random.choice(data, count, replace=False)
 
  return samples


if __name__ == "__main__":
  data = json.load(open('annotations/utterances.json', 'r'))
  convos = json.load(open('annotations/conversations.json', 'r'))
  starting_size = len(convos)
  samples = sample_dacts(convos, data, 8)
  all_convos = talk_together(convos, samples)

  new_size = len(all_convos)
  size = new_size - starting_size
  json.dump(all_convos, open('annotations/convo_texts.json', 'w'), indent=4)
  print(f"Done! You added {size} new conversations, for a total of {new_size}.")