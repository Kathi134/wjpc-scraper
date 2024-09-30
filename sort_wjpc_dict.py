import string

def sort_dict(dict):
    final_output = {}
    for name, results in dict.items():
        rearranged_results = {}
        for q in list(string.ascii_uppercase[0:6]):
            key = f'{q}_result'
            if key in results:    
                rearranged_results[key] = results[key]
                rearranged_results[f'{q}_relative_time'] = results[f'{q}_relative_time']
                break
        for s in ['S1', 'S2']:
            key = f'{s}_result'
            if key in results:    
                rearranged_results[key] = results[key]
                rearranged_results[f'{s}_relative_time'] = results[f'{s}_relative_time']
                break
        key = f'final_result'
        if key in results:    
            rearranged_results[key] = results[key]
            rearranged_results[f'final_relative_time'] = results[f'final_relative_time']
        rearranged_results["actual_rank"] = results["actual_rank"]
        order = ["avg_placement","avg_placement_rank", "avg_time","avg_time_rank",
                "score_before_final", "score_before_final_rank", "overall_score", "overall_score_rank", "score_on_unreleased", "score_on_unreleased_rank", 
                'improvement_against_prelims']
        for key in order:
            rearranged_results[key] = results[key]
        final_output[name] = rearranged_results
    return final_output
