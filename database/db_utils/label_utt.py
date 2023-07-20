import os, pdb, sys
import json 
import openai
import backoff

import numpy as np
from collections import defaultdict
from db_utils.for_annotation import *
from tqdm import tqdm as progress_bar

DESIRED_DACTS = ["plan", "format", "inquire", "describe"]

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

sys_prompt = """You are a DataAnalystBot named Dana that is able to answer questions about a shoe store from a DuckDB database. 

You are given the below tables:
Orders table contains columns: order_id, product_id, customer_id, size, channel, price, month, day, year. Primary key is order_id. Channels are methods of placing an order (search engine, email, social media) with values such as search_google, email_existing, email_new_user or social_fb. Month is in digits from 1 to 12. Day is in digits from 1 to 31. Year is either 2021, 2022, or 2023.",
Customers table contains columns: customer_id, first, last, city, state, member. Primary key is customer_id.",
Products table contains columns: product_id, sku, type, brand, style, cost. Primary key is product_id. sku stands for stock keeping unit. Type values are either Kids, Men, or Women. Styles are types of shoes with values such as casual, fashion, streetwear or running."

When asked for anything related to time, note that today is Saturday, May 20, 2023". Therefore, if a year is not specified, you can assume the user is referring to 2023."""

label_prompt = """You are working in the context of a data analyst operating with spreadsheet tables.
Given the description of an intent, come up with ten utterances that express that intent.  Note that the intent may contain multiple parts.

The intent is: {intent}
{description}

Examples:
{exemplars}
"""

aggregation_options = ["sum", "average", "count", "max", "min", "top", "bottom",
                        "median", "mode", "std_dev", "percentile", "all"]
prompts = {
  "report" : report_dact,
  "manipulate" : manipulate_dact,
  "converse" : converse_dact,
  "query" : query_dact,
}

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

def valid_operation(op):
  return (op.startswith("filter")) or (op.startswith("group")) or (op.startswith("sort"))

def derived_table(dact):
  return ("filter" in dact) or ("group" in dact) or ("sort" in dact)

def label_operations(utterance):
  prev_state = "Previous state: None"
  prompt = operations_prompt.format(previous_state=prev_state, utterance=utterance)
  messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]

  pred_output = completions_with_backoff(messages)
  carry_pred, agg_pred, op_pred = pred_output.split('\n')
  agg_pred = agg_pred.split(':')[1]
  aggregation = agg_pred.strip()

  valid_agg = False
  for agg in aggregation_options:
    if aggregation.startswith(agg):
      valid_agg = True
  if not valid_agg:
    raise(ValueError(f'"{aggregation}" is not a valid aggregation'))

  try:
    op_preds = op_pred.split(': ')[1]
    op_list = [op.strip() for op in op_preds.split(",")]
    operations = [op for op in op_list if valid_operation(op)]
  except(IndexError):
    raise(ValueError(f'"{op_pred}" is not a valid operations list'))

  return aggregation, operations

def build_reverse_index(data):
  inverted = defaultdict(list)
  for example in data:
    dact = example["dact"]
    inverted[dact].append(example)
  return inverted

def construct_prompt(dact, exemplars):
  if " + " in dact:
    relevant = dact.split(" + ")
  else:
    relevant = [dact]

  exp_text = "\n".join([f"{i+1}) {exemplars[i]['utterance']}" for i in range(len(exemplars))])
  description = "\n".join([f"{part} {desc[part]}" for part in relevant])
  prompt = label_prompt.format(intent=dact, description=description, exemplars=exp_text)
  return prompt

def parse_output(generated_output):
  parsed_examples = []
  for line in generated_output.split("\n"):
    example = line.split(") ")[1]
    parsed_examples.append(example.strip())

  return parsed_examples

def annotate(data, inverted, samples):
  print("Starting annotation ...")
  new_labels = []
  last_count = data[-1]["utt_id"]

  for idx, sample in enumerate(samples):
    dact = sample["dact"]
    options = inverted[dact]
    exemplars = np.random.choice(options, min(4, len(options)), replace=False)

    prompt = construct_prompt(dact, exemplars)
    messages = [{"role": "user", "content": prompt}]
    generated_output = completions_with_backoff(messages)
    parsed_examples = parse_output(generated_output)

    print(f">>>>>>>>>>>>> {idx+1} of {len(samples)} >>>>>>>>>>>>")
    print(f'{dact}: {sample["utterance"]}')

    for utt in parsed_examples:
      print(utt)
      if derived_table(dact):
        try:
          aggregation, operations = label_operations(utt)
          print("Aggregation:", aggregation)
          print("Operations:", operations)
        except Exception as err:
          print(f"< Skipped due to label operations error: {err} >")
          continue
      else:
        aggregation, operations = sample["aggregation"], sample["operations"]

      decision = input("Accept: ")
      result = {
        "utterance": utt,
        "intent": sample["intent"],
        "dact": dact,
        "aggregation": aggregation,
        "operations": operations,
      }

      if decision in ["y", "yes", "j"]:
        result["utt_id"] = last_count + 1
        new_labels.append(result)
        last_count += 1
      elif decision in desc.keys():
        result["utt_id"] = last_count + 1
        result["dact"] = decision
        new_labels.append(result)
        last_count += 1

  return new_labels  

def sample_dacts(data, count):
  if len(DESIRED_DACTS) > 0:
    samples = []
    while len(samples) < count:
      candidates = np.random.choice(data, 5, replace=False)
      for cand in candidates:
        if cand["dact"] in DESIRED_DACTS:
          samples.append(cand)
  else:
    samples = np.random.choice(data, count, replace=False)
 
  return samples


if __name__ == "__main__":
  data = json.load(open('annotations/utterances.json', 'r'))
  inverted = build_reverse_index(data)
  samples = sample_dacts(data, 8)
  new_labels = annotate(data, inverted, samples)

  size = len(new_labels)
  data.extend(new_labels)
  json.dump(data, open('annotations/utterances.json', 'w'), indent=4)
  print(f"Done! You added {size} new labels.")