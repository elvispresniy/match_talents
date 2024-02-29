import json
import requests
import datetime
import pickle

from copy import deepcopy

import torch

from transformers import AutoTokenizer, AutoModel

from config import models, keys_to_embed, invoke_url, headers, prompt

model_id = 1
device = 'cuda' if torch.cuda.is_available() else 'cpu'

#Load AutoModel from huggingface model repository
tokenizer = AutoTokenizer.from_pretrained(models[model_id])
model = AutoModel.from_pretrained(models[model_id]).to(device)

#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def get_embeddings(sentences):
  #Tokenize sentences
  encoded_input = tokenizer(sentences, padding=True, truncation=True, max_length=24, return_tensors='pt')

  encoded_input['input_ids'] = encoded_input['input_ids'].to(device)
  encoded_input['token_type_ids'] = encoded_input['token_type_ids'].to(device)
  encoded_input['attention_mask'] = encoded_input['attention_mask'].to(device)

  #Compute token embeddings
  with torch.no_grad():
      model_output = model(**encoded_input)

  #Perform pooling. In this case, mean pooling
  sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

  return sentence_embeddings


# Extract extra features from description of the vacancy
def get_extra_features(description: str) -> str:

    # Format the prompt
    formated_prompt = f"{prompt}{description}\noutput:\n"

    payload = {
        "messages": [
        {
            "content": formated_prompt,
            "role": "user"
        }
        ],
        "temperature": 1.0,
        "top_p": 0.7,
        "max_tokens": 256,
        "seed": 42,
        "stream": True
    }

    # Use API to inference LLM
    response = requests.post(invoke_url, headers=headers, json=payload, stream=True)

    features = ""

    for line in response.iter_lines():
        if line:
            try:
                result = json.loads(line.decode("utf-8")[6:])['choices'][0]['delta']['content']
                features += result
            except:
                break

    # Format and return the output
    try:
        start = features.index('{')
        end = features.index('}') + 1

        features.replace('\n', '')

        features_dict = json.loads(features[start:end])

        return features_dict
    except:
        return dict()


# Get the embeddings of some values in resume
def resume_with_embeddings(resume: dict) -> dict:
    resume = deepcopy(resume)

    if 'about' in resume and resume['about'] is not None:
        about_embed = get_embeddings(resume['about']).tolist()[0]
        resume['about_embedded'] = about_embed

    if 'key_skills' in resume and resume['key_skills'] is not None:
        key_skills_embed = get_embeddings(resume['key_skills']).tolist()[0]
        resume['key_skills_embedded'] = key_skills_embed

    if 'experienceItem' in resume and resume['experienceItem'] is not None:
        for item in resume['experienceItem']:
            if 'position' in item and item['position'] is not None:
                position_embed = get_embeddings(item['position']).tolist()[0]
                item['position_embedded'] = position_embed
            if 'description' in item and item['description'] is not None:
                description_embed = get_embeddings(item['description']).tolist()[0]
                item['description_embedded'] = description_embed
            
            if 'starts' in item and 'ends' in item and 'starts' is not None:
                try:
                    start = datetime.datetime.strptime(item['starts'], "%Y-%m-%d")
                    end = datetime.datetime.strptime(item['ends'], "%Y-%d-%m") if item['ends'] is not None else datetime.datetime.now()
                    years = round((end - start).days / 365)
                    item['years_at_work'] = years
                except:
                    item['years_at_work'] = None
                    pass

    return resume


# Get the embeddings of some values in vacancy
def vacancy_with_embeddings(vacancy: dict) -> dict:
    vacancy = deepcopy(vacancy)

    for key in keys_to_embed[1]:
        if key in vacancy and vacancy[key] is not None:
            key_embed = get_embeddings(vacancy[key]).tolist()[0]
            new_key = f"{key}_embedded"
            vacancy[new_key] = key_embed

    if 'description' in vacancy and vacancy['description'] is not None:
        extra_features = get_extra_features(vacancy['description'])
        vacancy['extra_features'] = extra_features

    return vacancy

def format_to_json(uuid_scores: list[tuple]) -> list[dict]:
    output = []

    for id, score in uuid_scores:
        output.append({"_id": str(id), "balance": round(score, 4)})

    return output

    # output_path = "output.json"

    # with open(output_path, "w") as outfile:
    #     json.dump(output, outfile)