from datetime import timedelta
from typing import Any
import scrapy
from scrapy.http import Response
import json
import string
from util import hour_stamp_to_sec 


class PairTimesSpider(scrapy.Spider):
    name = 'pair_results'
    start_urls = list(map(lambda round: f'https://www.worldjigsawpuzzle.org/wjpc/2024/pairs/{round}', 
                          list(string.ascii_uppercase[0:4]) + ['S1', 'S2', 'final']))
    avg_results = {}
    pair_results = []

    def parse(self, response: Response, **kwargs: Any) -> Any:
        self.logger.info("A response from %s just arrived!", response.url)
        round = response.url.split('/')[-1]
        self.parse_average(round, response)
        self.parse_results(round, response)

    def parse_average(self, round, response):
        calc_key = 'pair_final' if round == 'final' else 'pair'
        res = list(map(lambda t: hour_stamp_to_sec(t.strip(), calc_key), response.css('div.tiempo::text').getall()))
        res = [x for x in res if x is not None]
        avg = int(sum(res) / len(res))
        self.avg_results[round] = {
            'avg_seconds': avg, 
            'avg_time': str(timedelta(seconds=avg))
        }

    def parse_results(self, round, response):
        list(map(lambda n: self.pair_results.append({
            'competition': f'pair_{round}',
            'name': ' / '.join([item.strip() for item in n.css('td[valign="middle"] > div:nth-child(2)::text').getall()]),
            'result': n.css('td[valign="middle"] .tiempo::text')[0].get().strip()
        }), response.css('tr[idresultado]')))        

    def closed(self, reason):
        avg_file = "pair_averages.json"
        open(avg_file, "w").close()
        with open(avg_file, 'w') as file:
            file.write(json.dumps(self.avg_results))
        results_file = "pair_results.json"
        open(results_file, "w").close()
        with open(results_file, 'w') as file:
            file.write(json.dumps(self.pair_results))
