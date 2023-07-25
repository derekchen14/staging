import pdb, os, sys
import json
from sentence_transformers import SentenceTransformer, util
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from tqdm import tqdm as progress_bar
from tables import UserItem, AgentItem, UtteranceItem

def insert_data():
  engine = create_engine('postgresql://local_user:secret_postgres_password@localhost/soleda_db')
  Session = sessionmaker(bind=engine)
  session = Session()
  
  model = SentenceTransformer('all-MiniLM-L12-v2') # 'all-MiniLM-L12-v2'
  intent_map = {"query": 1, "manipulate": 2, "report": 3, "converse": 4}
  full_dact_list = ["describe", "filter", "group", "sort", "analyze", "plan", "clean", "delete",
         "format", "visualize", "style", "explain", "chat", "help", "inquire", "filter + group",
         "filter + sort", "group + sort", "filter + group + sort", "describe + analyze + visualize",
         "group + analyze", "analyze + clean", "analyze + explain", "analyze + style", "clean + plan",
         "clean + delete", "visualize + style", "visualize + explain", "delete + chat", "clean + chat"]
  dact_map = {dact: i+1 for i, dact in enumerate(full_dact_list)}

  # data = []
  # with open(f'database/db_utils/batch.txt', 'r') as f:
  #   for line in f:
  #     data.append(line.strip())
  data = json.load(open('annotations/utterances.json', 'r'))

  for example in progress_bar(data, total=len(data)):    
    speaker = "User"
    text = example["utterance"]
    history = f"{speaker}: {text}"
    vector = model.encode(history)

    intent_id = intent_map[example["intent"]]
    dact_id = dact_map[example["dact"]]
    aggregation = "None" if example["aggregation"] is None else example["aggregation"]
    operations = ",".join(example["operations"]) if len(example["operations"]) > 0 else "None"

    utt = UtteranceItem(speaker=speaker, text=text, short_embed=vector,
              intent_id=intent_id, dact_id=dact_id, aggregation=aggregation, operations=operations)
    session.add(utt)
    session.commit()
  print("Done!")

# Last added is "Are there any columns with date or time data?" at line 5450, which is 701 examples

if __name__ == "__main__":
  insert_data()