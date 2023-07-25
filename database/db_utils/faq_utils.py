import pdb, os, sys
import json
import numpy as np
import torch

from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm as progress_bar

def embed_faq(model, questions): 
  q_texts = [q["text"] for q in questions]
  embeddings = model.encode(q_texts, convert_to_tensor=True, show_progress_bar=True)
  torch.save(embeddings, 'annotations/faq_tensors.pt')
  return embeddings

def search_faq(model, questions, answers, embeddings):
  new_q = input("Ask a question: ")
  if new_q in ["exit", "done", "quit"]:
    return "exit"

  q_tensor = model.encode(new_q, convert_to_tensor=True)
  # Find nearest neighbors with basic cosine similarity. We do not use FAISS
  # or other libraries since we will never have > 1 million FAQs to process (by design)
  cos_scores = util.cos_sim(q_tensor, embeddings)[0]  
  # Sort the questions based on their cosine similarity score
  top_results = torch.topk(cos_scores, k=2)

  selected = set()
  for score, idx in zip(top_results[0], top_results[1]):
    answer_ids = questions[idx]["answers"]
    for aid in answer_ids:
      selected.add(answers[aid])
    print("Score: {:.3f} \n".format(score))

  for answer in selected:
    print(answer)

if __name__ == '__main__':
  questions = json.load(open('annotations/faq_questions.json', 'r'))
  answers = json.load(open('annotations/faq_answers.json', 'r'))
  model = SentenceTransformer('all-MiniLM-L12-v2')

  if not os.path.exists('annotations/faq_tensors.pt'):
    embeddings = embed_faq(model, questions)
  else:
    embeddings = torch.load('annotations/faq_tensors.pt') # .to('cuda')

  situation = "Go!"
  while situation != "exit":
    situation = search_faq(model, questions, answers, embeddings)