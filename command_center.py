# -*- coding: utf-8 -*-

import time
import requests

from pokemongo_bot.base_task import BaseTask
from pokemongo_bot.worker_result import WorkerResult
from pokemongo_bot.cell_workers.utils import distance

class CommandCenter(BaseTask):
    SUPPORTED_TASK_API_VERSION = 1
    def __init__(self, bot, config):
        super(CommandCenter, self).__init__(bot, config)
        self.cc_url = self.config.get("url")
        self.last_report = 0
        self.report_interval = 10

    def work(self):
        now = time.time()
        if now - self.last_report > self.report_interval:
            self.report_status()
        return WorkerResult.SUCCESS

    def report_status(self):
        self.last_report = time.time()
        lat = self.bot.api._position_lat
        lng = self.bot.api._position_lng
        alt = 0
        location = self.bot.position[0:2]
        cells = self.bot.find_close_cells(*location)

        inventory_req = self.bot.get_inventory()
        inventory_dict = inventory_req['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']

        self.bot.cell['catchable_pokemons'].sort(
            key=
            lambda x: distance(self.bot.position[0], self.bot.position[1], x['latitude'], x['longitude'])
        )
        catchable_pokemons = []
        if len(self.bot.cell['catchable_pokemons'])>0:
            catchable_pokemons = self.bot.cell['catchable_pokemons']

        data = {
            'username': self.bot.config.username,
            'location': {
                    'lat': lat,
                    'lng': lng,
                    'alt': alt,
                    'cells': cells
            },
            'inventory': inventory_dict,
            'catchable_pokemons': catchable_pokemons
        }
        try:
            response = requests.post(
                self.cc_url + '/report', json=data)

            response.raise_for_status()
        except requests.exceptions.HTTPError:
            pass
        except requests.exceptions.ConnectionError:
            pass