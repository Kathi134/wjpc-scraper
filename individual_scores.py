import json
from util import hour_stamp_to_sec 
from datetime import timedelta
from sort_wjpc_dict import sort_dict

WORST_VALUE = 5

data_dir = 'scraped_data'
with open(f"{data_dir}/individuals_averages.json" ,"r") as file:
    averages = json.load(file)
with open(f"{data_dir}/individuals_results.json", "r", encoding="utf-8") as file:
    results = json.load(file)

# add results and relative results
output = {}
for item in results:
    competition, name, country, result, placement = item.values()
    key = f"{name}"
    if key not in output:
        output[key] = {}

    comp_key = competition.replace('individual_','')
    round_key = 'quarterfinal' if len(comp_key) == 1 else ('semifinal' if len(comp_key) == 2 else 'final')
    output[key] = output[key] | {
        f'{comp_key}_result': result,
        f'{comp_key}_placement': placement,
        f'{comp_key}_relative_time': hour_stamp_to_sec(result, 'individual') / averages[comp_key]['avg_seconds']
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
    times = [hour_stamp_to_sec(val, 'individual') for key, val in participant.items() if ('result' in key)]
    seconds = sum(times) / len(times)
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
        'score_on_unreleased': score_rounds(value, 's','f'),
    }
    for key, value in output.items()
}

# add rankings
sorting_lambdas_on_scores = {
    'avg_time_rank': lambda item,_: item['avg_time'],
    'avg_placement_rank': lambda item,_: item['avg_placement'],
    'overall_score_rank': lambda item,_: item['overall_score'],
    'score_before_final_rank': lambda item,_: item['score_before_final'],
    'score_on_unreleased_rank': lambda item,_: item['score_on_unreleased'],
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
        'improvement_against_prelims': value['score_before_final_rank'] - value.get('final_placement', 181)
    }
    for key, value in output.items()
}

# provide clean output
output = sort_dict(output)
target_dir = 'scores'
with open(f"{target_dir}/individual_scores.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(dict(sorted(output.items(), key=lambda item: item[1]['actual_rank']))))
        
        
    
