import pickle

from sklearn.metrics.pairwise import cosine_similarity

import datetime

def simillarity_scores(resume: dict, vacancy: dict) -> dict:
    scores = {
        'description_about': 0.0,
        'keywords_key_skills': 0.0,
        'description_description': 0.0,
        'name_position': 0.0,
        'age_fits': 0.0,
        'experience_fits': 0.0,
        'country_fits': 0.0,
        'language_fits': 0.0,
        'education_fits': 0.0,
    }
    
    # Check description-about pair
    if 'description_embedded' in vacancy and 'about_embedded' in resume:
        scores['description_about'] = cosine_similarity([vacancy['description_embedded']], [resume['about_embedded']])[0][0]
    
    # Check keywords-key_skills pair
    if 'keywords_embedded' in vacancy and 'key_skills_embedded' in resume:
        scores['keywords_key_skills'] = cosine_similarity([vacancy['keywords_embedded']], [resume['key_skills_embedded']])[0][0]
    
    # Iterate over experienceItem
    if 'experienceItem' in resume and resume['experienceItem']:
        max_des_des_sim_score = -2
        max_name_pos_sim_score = -2
        total_experience = 0

        for experience in resume['experienceItem']:
            # Calculate maximal simillarity for description-description pair
            if 'description_embedded' in vacancy and 'description_embedded' in experience:
                sim_score = cosine_similarity([vacancy['description_embedded']], [experience['description_embedded']])[0][0]
                max_des_des_sim_score = max(max_des_des_sim_score, sim_score)
            
            # Calculate maximal simillarity for name-position pair
            if 'name_embedded' in vacancy and 'position_embedded' in experience:
                sim_score = cosine_similarity([vacancy['name_embedded']], [experience['position_embedded']])[0][0]
                max_name_pos_sim_score = max(max_name_pos_sim_score, sim_score)

            # Accumulate years of experience
            if 'years_at_work' in experience and experience['years_at_work'] is not None:
                total_experience += experience['years_at_work']

        # Similarities
        scores['description_description'] = max_des_des_sim_score if max_des_des_sim_score != -2 else 0
        scores['name_position'] = max_name_pos_sim_score if max_name_pos_sim_score != -2 else 0

        # Experience
        if vacancy['extra_features']['experience'] is not None:
            scores['experience_fits'] = float(total_experience >= vacancy['extra_features']['experience'])
        else:
            scores['experience_fits'] = 1

    # Calculate if candidates age is appropriate
    if resume['birth_date'] is not None:
        min_age = vacancy['extra_features']['min age'] if vacancy['extra_features']['min age'] is not None else 18
        max_age = vacancy['extra_features']['max age'] if vacancy['extra_features']['max age'] is not None else 99

        age = (datetime.datetime.now() - datetime.datetime.strptime(resume['birth_date'], "%Y-%m-%d")).days // 365

        scores['age_fits'] = float(min_age <= age <= max_age)

    # Check if the country is matching
    resumes_country = resume['country']

    if vacancy['extra_features']['country'] is not None:
        scores['country_fits'] = 1.0 if resumes_country in vacancy['extra_features']['country'] else 0.0

    # Check if the languages are matching
    if 'languageItems' in resume:
        if vacancy['extra_features']['languages'] is None or len(vacancy['extra_features']['languages']) == 0:
            scores['language_fits'] = 1.0
        else:
            for language in resume['languageItems']:
               if language in vacancy['extra_features']['languages']:
                    scores['language_fits'] = 1.0
                    break
    elif vacancy['extra_features']['languages'] is not None and 'Русский' in vacancy['extra_features']['languages']:
        scores['language_fits'] = 1.0
    else:
        scores['language_fits'] = 0.0

    # Check if the education matches
    if vacancy['extra_features']['education level'] is not None:
        if 'educationItem' in resume:
            for education in resume['educationItem']:
                education_level = education['education_level']
                if education_level == 'Высшее' or education_level == 'Бакалавр' or education_level == 'Магистр':
                    scores['education_fits'] = 1.0
                    break
    else:
        scores['education_fits'] = 1.0

        
    return scores


def get_total_score(raw_scores: dict) -> float:
    scores_weights = {
      'description_about': 0.63205,
      'keywords_key_skills': 0.947156,
      'description_description': 0.862351,
      'name_position': 0.782359,
      'age_fits': 0.626857,
      'experience_fits': 0.68093,
      'country_fits': 0.23586,
      'language_fits': 0.758273,
      'education_fits': 0.41525,
    }

    total = 0

    for key in scores_weights:
        total += scores_weights[key] * raw_scores[key]

    return total / sum(scores_weights.values())


def uuid_scores(resumes: list, vacancy: dict) -> list[tuple]:
    uuid_score_pairs = []

    for resume in resumes:
        scores_raw = simillarity_scores(resume, vacancy)
        total_score = get_total_score(scores_raw)
        uuid_score_pairs.append((resume['uuid'], total_score))

    return sorted(uuid_score_pairs, key=lambda x: -x[-1])