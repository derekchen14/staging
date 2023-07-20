

def process_joint_data(args, data, tokenizer, ontology):
  datasets = {}
  ont_mapping = {label: idx for idx, label in enumerate(dialogue_acts)}
  for split in ['train', 'dev', 'test']:
    split_data = data[split]
    examples = []

    for utterance in progress_bar(split_data, total=len(split_data)):
      dacts = utterance['dact']
      dact_ids = [ont_mapping[dact] for dact in dacts.split(" + ")]
      dact_vector = [1 if pos in dact_ids else 0 for pos in range(16)]

      exp = {'uid': utterance['utt_id'], 
            'text': utterance['utterance'],
            ' dax': dacts2dax(dacts),
          'target': dacts,
        'label_id': dact_vector}
      examples.append(exp)

    datasets[split] = ClassifyDataset(args, examples, tokenizer, dialogue_acts, split)
    print(f"Running with {len(datasets[split])} {split} examples")
  return datasets

def run_joint_eval(args, model, dact_models, dataset, exp_logger, split='dev'):
  tokenizer, ontology = dataset.tokenizer, dataset.ontology
  dataloader = get_dataloader(args, dataset, split)
  num_batches = debug_break if args.debug else len(dataloader)
  exp_logger.start_eval(num_batches)
  model.eval()
  intent_ont = ["query", "manipulate", "report", "converse"]

  for intent, dact_model in dact_models.items():
    dact_model.eval()

  '''goes through model generation without backprop, rather than classification '''
  all_inputs, all_outputs, all_targets  = [], [], []
  for inputs, targets in progress_bar(dataloader, total=len(dataloader)):
    inputs = inputs.to(device)
    input_strings = tokenizer.batch_decode(inputs['input_ids'], skip_special_tokens=True)

    with torch.no_grad():
      # defaults to greedy sampling, for param details see https://huggingface.co/docs/transformers/
      #        v4.15.0/en/main_classes/model#transformers.generation_utils.GenerationMixin.generate
      outputs, _ = model(**inputs)
      intent_preds = outputs.argmax(dim=1).tolist()

      query_preds, _ = dact_models["query"](**inputs)
      manipulate_preds, _ = dact_models["manipulate"](**inputs)
      report_preds, _ = dact_models["report"](**inputs)
      converse_preds, _ = dact_models["converse"](**inputs)

      output_preds = []
      for idx, intent in enumerate(intent_preds):
        if intent == 0:
          output_preds.append(query_preds[idx])
        elif intent == 1:
          output_preds.append(manipulate_preds[idx])
        elif intent == 2:
          output_preds.append(report_preds[idx])
        elif intent == 3:
          output_preds.append(converse_preds[idx])

    all_inputs.extend(input_strings)
    all_outputs.extend(output_preds)
    # all_intent_preds.extend(intent_preds)
    all_targets.extend(targets)
    exp_logger.eval_step += 1

  inputs = postprocess_inputs(args, all_inputs)
  # predictions = [intent_ont[pred] for pred in all_intent_preds]
  outputs = postprocess_outputs(args, all_outputs, ontology)
  targets = postprocess_targets(args, all_targets, ontology)

  eval_qualify(args.task, inputs, outputs, targets)
  # identify_errors(args.task, inputs, outputs, targets)
  results = eval_quantify(args, outputs, targets, exp_logger)
  return results


def load_dact_models(args, tokenizer, ontology):
  dact_models = {}
  for intent in ["manipulate", "converse", "report", "query"]:
    args.task = f"dact_{intent}"
    load_dir = os.path.join("modeling", args.output_dir, args.model, f"dact_{intent}", "standard")
    ckpt_path = find_best_model_path(load_dir, is_directory=False)
    print(f'Attempting to load {ckpt_path} as best model for {intent}')
    dm = load_model(args, tokenizer, dialogue_acts, ckpt_path)
    full_model_path = os.path.join(load_dir, ckpt_path)
    checkpoint = torch.load(full_model_path, map_location='cpu')
    dm.load_state_dict(checkpoint)
    dact_models[intent] = dm.to(device)
  return dact_models

def load_intent_model(args, exp_logger, tokenizer, ontology):
  load_dir = os.path.join("modeling", args.output_dir, args.model, "intent", "standard")
  print(f'Loading best finetuned model from {load_dir} ...')
  model = IntentClassifier(args, ["query", "manipulate", "report", "converse"])
  model.base_model.config.pad_token = tokenizer.pad_token
  model.base_model.config.pad_token_id = tokenizer.pad_token_id
  model.base_model.resize_token_embeddings(len(tokenizer))  # transformer_check

  ckpt_path = "acc935_lr1e-05_epoch7.pt"
  full_model_path = os.path.join(load_dir, ckpt_path)
  checkpoint = torch.load(full_model_path, map_location='cpu')
  model.load_state_dict(checkpoint)
  model.to(device)
  return model




class InContextPolicy(Object):

	def __init__(self, args):
		self.prompt = "Given the user utterance, decide if the request is ambiguous or can be answered by the database"
		self.exemplars = load_policy_exemplars()
		self.model = GPT4Engine(args)
		self.convo_history = []

		self.is_converse = """Is the user engaging in small talk, back channeling or other chit chat?
		Back-channeling examples include 'uh-oh', 'ok', 'yeah'
		Small talk examples include discussions about the weather or Soleda"""


	def decide(self, nlu_output, result=None):
		for mod_type in self.module_types:
			pred, score = self.nlu.get_pred_and_score(mod_type)
			self.store_predictions(mod_type, pred, score)

		if result is None:
			active_prompt = self.prompt
		else:
			active_prompt = self.fill_prompt(result)
		action, state = self.model(active_prompt)
		action = guardrails.verify(action, "action")

		return action, state


	def query(self, nlu_output):
		query_prompt = """
		Given the tables, columns, and user request, generate a SQL query that works with the data schema from the system prompt.
		Note: Do NOT add new lines in the SQL query action input.
		When selecting columns that exist in multiple tables after a join, don't forget to include the table name in the SELECT.
		Make sure not to group by ID columns because ID is usually unique.

		Remember, you are querying from a sqlite database.

		Input:
		"""
		query, tool = self.model(query_prompt + self.exemplars)
		# tools can be 'sql' or 'python'
		query = guardrails.verify(sql_query, tool)

	def ask(self, nlu_output):
		clarify_prompt = """
		Given the ambiguous question and the list of tables, columns, and user request from that initial question, 
		generate a clarifying question to resolve the ambiguity."""
		question = self.model(clarify_prompt + self.exemplars)
		return question

	def visualize(self, nlu_output):
		viz_prompt = """
		Given the request from the user, generate the plotly express code to create the visualization or diagram
		Remember that the code should be valid python that can be executed
		"""
		code = self.model(viz_prompt + self.exemplars)
		result = "visual"
		return code, result

	def format(self, nlu_output):
		format_prompt = """
		You are SpreadsheetBot, a machine who formats tables within Google Sheets.  Your code is always syntactically correct.
		Given the description of the updated table, generate the JSON to send to the Google Sheets REST API code to format the table
		"""
		code = self.model(clarify_prompt + self.exemplars)
		result = "format"
		return code, result