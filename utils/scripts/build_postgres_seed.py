import pdb, os, sys
import json

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from tqdm import tqdm as progress_bar
from database.tables import UserItem, AgentItem, IntentItem, DialogueActItem, UtteranceItem

# Move this script into the root directory before running to get the paths correct
load_dotenv('./database/.env')  # comment out if running in production

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

model = SentenceTransformer('all-MiniLM-L12-v2')
data = json.load(open('database/storage/seed_data.json', 'r'))
utterances = json.load(open('database/annotations/utterances.json', 'r'))
intent_map = {"query": 1, "manipulate": 2, "report": 3, "converse": 4}
dact_map = {dd["dact"]: idx for idx, dd in enumerate(data["Dacts"])}
            
def make_session():
  engine_name = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
  print("engine name: ", engine_name)

  engine = create_engine(engine_name)
  Session = sessionmaker(bind=engine)
  session = Session()
  return session

def build_new_dacts(example):
  dact, dax = example["dact"], example["dax"]
  description = example["description"]
  intent_id = intent_map[example["intent_id"]]
  return DialogueActItem(dact=dact, dax=dax, description=description, intent_id=intent_id, agent_id=1)

def populate_tables(session):
  for category, examples in data.items():
    for example in examples:
      if category == "Users":
        new_item = UserItem(**example)
      elif category == "Agents":
        new_item = AgentItem(**example)
      elif category == "Intents":
        new_item = IntentItem(**example)
      elif category == "Dacts":
        new_item = build_new_dacts(example)
      session.add(new_item)
      session.commit()
    print(f"Completed {category} with {len(examples)}")

def populate_conversations(session):
  for utterance in progress_bar(utterances, total = len(utterances)):
    speaker, text = "user", utterance["text"]
    intent, dact_list = utterance["intent"], utterance["dact"]
    agg, ops = utterance["aggregation"], utterance["operations"]
    table, table_cols = "unknown", ["price in orders"]
    if(utterance["dact"] == "analyze + explain"):
      print(text)
      pdb.set_trace()
    dact_id = dact_map[dact_list]
    history = f"{speaker}: {text}"
    vector = model.encode(history)

    utt = UtteranceItem(speaker=speaker, text=text, short_embed=vector, 
                          aggregation=agg, operations=ops, dact_id=dact_id)
    session.add(utt)
    session.commit()

if __name__ == "__main__":
  session = make_session()
  populate_tables(session)
  populate_conversations(session)


"""
results = session.scalars(select(UtteranceItem).order_by(
      UtteranceItem.short_embed.cosine_distance(query_vector)
    ).limit(2))
search_query = select(UtteranceItem).order_by(
      UtteranceItem.short_embed.cosine_distance(query_vector)
    ).limit(3)
results = session.scalars(search_query).all()
"""