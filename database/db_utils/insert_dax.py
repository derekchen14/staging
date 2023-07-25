import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from tqdm import tqdm as progress_bar
from tables import UserItem, DialogueActItem, UtteranceItem

dialogue_acts = ["clarify", "describe", "filter", "group", "sort", "analyze", "plan", "clean",
                "delete", "format", "visualize", "style", "explain", "chat", "help", "inquire"]

dact_options = {
  "clarify": "when the user has not provided enough information to answer the question",
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
  "chat": "is talking about non-data related subjects, so the response does not need to query the table.  Answers may be based on opinion, and can change for one person to another.",
  "help": "is getting a better understanding of what the service entails, answering questions found in a FAQ.  Unlike 'chat', the answers to 'help' questions are broadly applicable to all customers.",
  "inquire": "represents when the user is asking about how the agent derived an answer or recommendation",
  "filter + group": "query with filtering and grouping: 'Show total dress shoes sold per month'",
  "filter + sort": "query with filtering and sorting: 'What are the most expensive basketball shoes?'",
  "group + sort": "query with grouping and sorting: 'Who are the top sales reps in each region?'",
  "filter + group + sort": "filter, group and sort together: 'Find the top selling running shoes for each city'",
  "describe + analyze + visualize": "general questions about the data: 'Any interesting insights in these tables?'",
  "group + analyze": "making and modifying pivot tables",
  "analyze + clean": "performing exploratory analysis for the purpose of identifying noisy example, such as outliers",
  "analyze + explain": "writing an explanation of the analysis performed rather than a diagram",
  "analyze + style": "adding a trendline or other visual analysis to a plot or diagram",
  "clean + plan": "performing the same analysis on the next item: 'OK, how about the next one'",
  "clean + delete": "going back to the last step: 'Nevermind, undo that'",
  "clean + chat": "backchanneling which acknowledges progress or expresses joy: 'Great, thanks!'",
  "delete + chat": "backchanneling which expresses dissatisfaction or confusion: 'I don't know what to do next'",
  "visualize + style": "creating and managing dashboard, such as automatic updates",
  "visualize + explain": "creating and managing reports, such as weekly recurring generation",
}

def dact2dax(dact:str):
  dacts = dact.split(" + ")
  positions = [i for i, dialog_act in enumerate(dialogue_acts) if dialog_act in dacts]
  dax_string = ''.join(format(pos, 'X') for pos in positions)
  return dax_string.zfill(3)

def insert_data():
  engine = create_engine('postgresql://local_user:secret_postgres_password@localhost/soleda_db')
  Session = sessionmaker(bind=engine)
  session = Session()

  for dop, desc in progress_bar(dact_options.items(), total=len(dact_options)):
    dax = dact2dax(dop)
    dact_item = DialogueActItem(dact=dop, dax=dax, description=desc, agent_id=1)
    session.add(dact_item)
    session.commit()
  print("Done!")

if __name__ == '__main__':
  insert_data()