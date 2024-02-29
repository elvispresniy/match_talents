import functions
from functions import *

import scores
from scores import *

import json
import pickle


if __name__ == "__main__":
    # Load the vacancy
    path_vacancy = r"data\case_2_reference_without_resume_sorted.json"

    with open(path_vacancy, 'r', encoding="utf-8") as file:
        vacancy_json = json.load(file)

    vacancy = vacancy_with_embeddings(vacancy_json['vacancy'])

    # Load the dataset of resumes
    path_resumes = r"data_pickle\resumes.pickle"

    with open(path_resumes, 'rb') as file:
        resumes = pickle.load(file)

    resulting_scores = uuid_scores(resumes, vacancy)

    format_to_json(resulting_scores)

    print(resulting_scores)