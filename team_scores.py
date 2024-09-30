# todo: overallscore on unreleasedis off

from datetime import timedelta
import json
import string
from sort_wjpc_dict import sort_dict
from util import hour_stamp_to_sec 

WORST_VALUE = 5

division = 'team'

data_dir = 'scraped_data'
with open(f"{data_dir}/{division}_averages.json" ,"r") as file:
    averages = json.load(file)
with open("scores/individual_scores.json" ,"r", encoding="utf-8") as file:
    ind_scores = json.load(file)
with open(f"{data_dir}/{division}_results.json", "r", encoding="utf-8") as file:
    results = json.load(file)

# add results and relative results
output = {}
for item in results:
    competition, name, country, result, placement = item.values() 
    key = f"{name}"
    if key not in output:
        try:
            scores = []
            names = name.split('/')
            for n in names:
                n = n.strip()
                if n in ind_scores:
                    scores += [ind_scores[n]['score_on_unreleased']]
        except: 
            print(name)
            continue
        if(len(scores) == 0):
            avg_score = WORST_VALUE
        else: 
            avg_score = sum(scores) / len(scores)
        output[key] = {
            "individual_combined_score": avg_score
        }

    comp_key = competition.replace(f'{division}_','')
    round_key = 'semifinal' if len(comp_key) == 1 else 'final'
    output[key] = output[key] | {
        f'{comp_key}_result': result,
        f'{comp_key}_placement': placement,
        f'{comp_key}_relative_time': hour_stamp_to_sec(result, division) / averages[comp_key]['avg_seconds']
    }

# add scores that combine performances of multiple rounds
def filter_scores(array, *keys):
    relevant_fields = {key.replace('_relative_time', ''): val for key, val in array.items() if 'relative_time' in key}
    result = []
    if 'q' in keys:
        result += [val for key, val in relevant_fields.items() if len(str(key)) == 1]
    if 's' in keys:
        result += [val for key, val in relevant_fields.items() if len(str(key)) == 2 and key[0] == 'S']
    if 'f' in keys: 
        result += [val for key, val in relevant_fields.items() if 'final' in key]
    return result

def score_rounds(participant, *round_keys):
    scores = filter_scores(participant, *round_keys)
    if len(scores) == 0:
        return WORST_VALUE
    return sum(scores) / len(scores)

def average_time(participant):
    times = [hour_stamp_to_sec(val, division) for key, val in participant.items() if ('result' in key)]
    if len(times) == 0:
        raise ValueError
    seconds = sum(times) / (len(times)*2) # we want the average for a single 1000 piece puzzle
    return str(timedelta(seconds=int(round(seconds,0))))

def average_placement(participant):
    placements = [val for key, val in participant.items() if ('placement' in key)]
    return sum(placements) / len(placements)

output = { 
    key: {
        **value, 
        'avg_time': average_time(value),
        'avg_placement': average_placement(value),
        'overall_score': score_rounds(value, 'q','s','f'), 
        'score_before_final': score_rounds(value, 'q','s'),
    }
    for key, value in output.items()
}
   
# add rankings
sorting_lambdas_on_scores = {
    'individual_combined_score_rank': lambda item,_: item['individual_combined_score'],
    'avg_time_rank': lambda item,_: item['avg_time'],
    'avg_placement_rank': lambda item,_: item['avg_placement'],
    'overall_score_rank': lambda item,_: item['overall_score'],
    'score_before_final_rank': lambda item,_: item['score_before_final']
}

for rank_field_name, sorting_fun in sorting_lambdas_on_scores.items():
    sorted_items = sorted(output.items(), key=lambda item: sorting_fun(item[1], output))
    for rank, (name, values) in enumerate(sorted_items, start=1):
        values[rank_field_name] = rank


# calculate improvement
output = { 
    key: {
        **value, 
        'actual_rank': value.get('final_placement',200),
        'improvement_against_individual_performances': value['individual_combined_score_rank'] - value.get('final_placement',200),
        'improvement_against_prelims': value['score_before_final_rank'] - value.get('final_placement',200),
    }
    for key, value in output.items()
}

# sort the dict
output = sort_dict(output, division)
target_dir = 'scores'
with open(f"{target_dir}/{division}_scores.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(dict(sorted(output.items(), key=lambda item: item[1]['actual_rank']))))

        
        