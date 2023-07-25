import json 
import numpy as np
from tqdm import tqdm as progress_bar
from collections import Counter

data = json.load(open(f'annotations/utterances.json', 'r'))
dact_count = Counter()

matches = []
holder = set()
# count the number of occurences of each dact
for example in progress_bar(data, total=len(data)):

  dact = example["dact"]
  if " + " in dact:
    parts = dact.split(" + ")
    for part in parts:
      dact_count[part] += 1
  else:
    dact_count[dact] += 1

  raw_utt = example["utterance"]
  utt = raw_utt.replace("?", " ").replace(",", " ").replace(".", " ")
  tokens = [t.lower().strip() for t in utt.split(" ")]
  canonical = " ".join(tokens)
  
  if canonical in holder:
    matches.append((utt, example["utt_id"]))

  holder.add(canonical)

if len(matches) > 0:
  print("Duplicates:")
  remove_ids = []
  for utt, uid in matches:
    print(utt)
    remove_ids.append(uid)
  # Use list comprehension to create a new list with only the utterances you want to keep
  filtered = []
  count = 1
  activated = False
  for example in data:
    if example["utt_id"] in remove_ids:
      activated = True
    else:
      if activated:
        example["utt_id"] = count
      filtered.append(example)
      count += 1

  print(f"Removed {len(matches)} duplicates")
  print(f"New length: {len(filtered)}")
  json.dump(filtered, open(f'annotations/utterances.json', 'w'), indent=2)

ordered = ["describe", "filter", "group", "sort", "analyze", "plan", "clean", "delete",
           "format", "visualize", "style", "explain", "chat", "help", "inquire"]

for key, value in dact_count.items():
  if key not in ordered:
    print("Key Error:", key)

num = 1
for dact in ordered:
  count = dact_count[dact]
  print(f"{num}) {dact}: {count}")
  num += 1

