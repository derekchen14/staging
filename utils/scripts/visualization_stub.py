# Agent class for the old agent
    pred_intent = "report"
    pred_dacts = ["visualize"]
    aggregation = "all orders"
    operations = ["filter month is June", "filter year is 2023", "group by channel", "sort by price"]
    thought = "The user is asking for a visualization of price by channel for a specific month and year. I will need the orders table, which contains the price, channel, month, and year columns."
    dialogue_state = DialogueState(tables=["orders"],
                          columns={"orders": ["price", "channel", "month", "year"]},
                          dacts=pred_dacts,
                          dax="00A",
                          thought=thought,
                          aggregation=aggregation,
                          operations=operations)

sql_query = "SELECT channel, SUM(price) AS total_price FROM orders WHERE month = 6 AND year = 2023 GROUP BY channel ORDER BY total_price DESC;"
db_output = self.database.db.execute(sql_query)



last_action = context.last_action("agent")
if len(last_action) > 0 and last_action["action"] == "CLARIFY":
  agent_clarify_question = context.last_utt("agent")["text"]
  user_clarify_answer = context.last_utt("user")["text"]
  # recent_utterances = self.recent  # also not used at the moment
  prompt = edit_state_prompt.format(agent_question=agent_clarify_question, 
                                    dialogue_state=dialogue_state, 
                                    user_answer=user_clarify_answer)
  state_string = self.api.execute(prompt)
  dialogue_state = DialogueState.from_string(state_string, context.tables)