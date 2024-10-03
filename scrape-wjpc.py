from abc import abstractmethod
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import timedelta
from typing import Any
import scrapy
from scrapy.http import Response
import json
import string
from util import hour_stamp_to_sec 


class WjpcSpider(scrapy.Spider):
    base_url = 'https://www.worldjigsawpuzzle.org/wjpc/2024'

    def __init__(self, division, rounds, division_options_key, parse_results):
        self.division = division
        self.rounds = rounds
        self.division_options_key = division_options_key
        self.name = f'{division}_results_spider'
        self.parse_results = parse_results

        self.avg_results = {}
        self.results = []

    def start_requests(self):
        # needs plural to land on the results page x.x
        urls = [f'{self.base_url}/{self.division}s/{r}' for r in self.rounds]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        round = response.url.split('/')[-1]
        self.parse_average(round, response)
        self.results += self.parse_results(round, response)

    def parse_average(self, round, response):
        times = response.css('div.tiempo::text').getall()
        times = [t.strip() for t in times if t.strip()]

        res = list(map(lambda t: hour_stamp_to_sec(t, self.division_options_key(round)), times))
        res = [x for x in res if x is not None]
        avg = int(sum(res) / len(res))

        finishers = list(filter(lambda t: ':' in t, times))
        
        self.avg_results[round] = {
            'avg_seconds': avg, 
            'avg_time': str(timedelta(seconds=avg)),
            'finished': len(finishers) / len(times)
        }

    def closed(self, _):
        target_dir = 'scraped_data'
        avg_file = f"{target_dir}/{self.division}_averages.json"
        open(avg_file, "w").close()
        with open(avg_file, 'w') as file:
            file.write(json.dumps(self.avg_results))
        results_file =  f"{target_dir}/{self.division}_results.json"
        open(results_file, "w").close()
        with open(results_file, 'w') as file:
            file.write(json.dumps(self.results))
        self.avg_results = {}
        self.results = []


def parse_individual_results(round, response):
    return [{
        'competition': f'individual_{round}',
        'name': node.css('td[valign="middle"] > div:nth-child(2)::text').get().strip(),
        'country': node.css('td[valign="middle"] > div.ver_movil.pais_movil::text').get().strip(),
        'result': node.css('td[valign="middle"] .tiempo::text')[0].get().strip(),
        'placement': int(node.css('div.puesto::text').get()),
    } for node in response.css('tr[idresultado]')]

def parse_pair_results(round, response):
    return [{
        'competition': f'pair_{round}',
        'name': ' / '.join([item.strip() for item in node.css('td[valign="middle"] > div:nth-child(2)::text').getall()]),
        'country': node.css('td[valign="middle"] > div.ver_movil.pais_movil::text').get().strip(),
        'result': node.css('td[valign="middle"] .tiempo::text')[0].get().strip(),
        'placement': int(node.css('div.puesto::text').get()),
    } for node in response.css('tr[idresultado]')]    

def parse_team_results(round, response):
    names_selector = lambda x : x.css('td[valign="middle"] > div:nth-child(2) > div:nth-child(2) div::text').getall()[0]
    return [{
        'competition': f'team_{round}',
        'name': ' / '.join([x.strip() for x in names_selector(node).split('/')]),
        'country': node.css('td[valign="middle"] > div.ver_movil.pais_movil::text').get().strip(),
        'result': node.css('td[valign="middle"] .tiempo::text')[0].get().strip(),
        'placement': int(node.css('div.puesto::text').get()),
    } for node in response.css('tr[idresultado]')]        


def main():
    process = CrawlerProcess(get_project_settings())
    process.crawl(WjpcSpider,
        division='individual',
        rounds=list(string.ascii_uppercase[0:6]) + ['S1', 'S2', 'final'],
        division_options_key = lambda r: 'individual_final' if r == 'final' else 'individual',
        parse_results=parse_individual_results
    )
    process.crawl(WjpcSpider,
        division='pair',
        rounds=list(string.ascii_uppercase[0:4]) + ['S1', 'S2', 'final'],
        division_options_key = lambda r: 'pair_final' if r == 'final' else 'pair',
        parse_results=parse_pair_results
    )
    process.crawl(WjpcSpider,
        division='team',
        rounds=list(string.ascii_uppercase[0:3]) + ['final'],
        division_options_key = lambda _: 'team',
        parse_results=parse_team_results
    )
    process.start()

if __name__ == '__main__':
    main()