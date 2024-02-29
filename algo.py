import functions
from functions import *

import scores
from scores import *

import json
import pickle

# Load the input file
with open('input.json', 'r') as input_file:
    data = json.load(input_file)

vacancy = vacancy_with_embeddings(data['vacancy'])

# Load the dataset of resumes
path_resumes = r"data_pickle\resumes.pickle"

with open(path_resumes, 'rb') as file:
    resumes = pickle.load(file)

# Process the data
resulting_scores = uuid_scores(resumes, vacancy)

processed_data = format_to_json(resulting_scores)

with open('output.json', 'w') as output_file:
    json.dump(processed_data, output_file)