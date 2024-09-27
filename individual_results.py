# requested data:
# average time in each individual round
# ind. person ID, name, lastname, country, city
    # relative score on performance in individuals
    # player_time / avg_time -> the less the better 
# pairs + teams made up of individuals
    # sum up or average the score 

from pathlib import Path
from datetime import timedelta
from typing import Any
import scrapy
from scrapy.http import Response
import json
import string
from util import hour_stamp_to_sec 


class IndividualTimesSpider(scrapy.Spider):
    name = 'individual_results'
    start_urls = list(map(lambda round: f'https://www.worldjigsawpuzzle.org/wjpc/2024/individual/{round}', 
                          list(string.ascii_uppercase[0:6]) + ['S1', 'S2', 'final']))
    avg_results = {}
    individual_results = []

    def parse(self, response: Response, **kwargs: Any) -> Any:
        self.logger.info("A response from %s just arrived!", response.url)
        round = response.url.split('/')[-1]
        self.parse_average(round, response)
        self.parse_results(round, response)

    def parse_average(self, round, response):
        res = list(map(lambda t: hour_stamp_to_sec(t.strip(), 'individual'), response.css('div.tiempo::text').getall()))
        res = [x for x in res if x is not None]
        avg = int(sum(res) / len(res))
        self.avg_results[round] = {
            'avg_seconds': avg, 
            'avg_time': str(timedelta(seconds=avg))
        }

    def parse_results(self, round, response):
        list(map(lambda n: self.individual_results.append({
            'competition': f'individual_{round}',
            'name': n.css('td[valign="middle"] > div:nth-child(2)::text').get().strip(),
            'country': n.css('td[valign="middle"] > div.ver_movil.pais_movil::text').get().strip(),
            'result': n.css('td[valign="middle"] .tiempo::text')[0].get().strip()
        }), response.css('tr[idresultado]')))        

    def closed(self, reason):
        avg_file = "individual_averages.json"
        open(avg_file, "w").close()
        with open(avg_file, 'w') as file:
            file.write(json.dumps(self.avg_results))
        results_file = "individual_results.json"
        open(results_file, "w").close()
        with open(results_file, 'w') as file:
            file.write(json.dumps(self.individual_results))
