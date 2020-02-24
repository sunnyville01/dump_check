import os
import json
import time
import requests
from os import path
import urllib.request
from operator import itemgetter

from datetime import datetime
from bittrex import bittrex
from playsound import playsound


class DumpCheck:
    bittrex_api = bittrex('#####', '#####') # bittrex api key and secret

    def __init__(self):

        self.bittrex_change_check = -20
        self.binance_change_check = -20
        self.exchanges = ['binance', 'bittrex']
        self.final_results = []
        self.bittrex_results = []
        self.binance_results = []
        self.now = int(datetime.timestamp(datetime.now()))

        try:
            for exchange in self.exchanges:
                self.get_results(exchange)
        except Exception as e:
            print(e)
        else:
            self.handle_results()


    def handle_results(self):

        # Clear Screen
        os.system('cls')

        # Get results from File
        with open('results.txt', 'r') as results_file:
            saved_results = json.load(results_file)
        # Find new results
        current_results = self.bittrex_results + self.binance_results

        # Find new results
        new_results = []
        for current_result in current_results:
            coin = current_result["Coin"]
            exchange = current_result["Exchange"]
            change = current_result["Change"]

            if any(d['Coin'] == coin and d["Exchange"] == exchange for d in saved_results):
                saved_item = [d for d in saved_results if d['Coin'] == coin and d["Exchange"] == exchange]
                saved_item_change = saved_item[0]["Change"]
                if change > 1.5 * saved_item_change:
                    new_results.append(current_result)
                    # Deleting the old result from saved results
                    for i in range(len(saved_results)):
                        if saved_results[i]["Coin"] == current_result["Coin"] and saved_results[i]["Exchange"] == current_result["Exchange"]:
                            del saved_results[i]
                            break
            else:
                new_results.append(current_result)

        #  Play sound if new results
        if len(new_results):
            playsound('dumping.mp3')

        # Final results
        final_results = saved_results + new_results
        final_results = sorted(final_results, key=itemgetter('Time'))

        # Save Results ti file
        with open('results.txt', 'w') as results_file:
            json.dump(final_results, results_file)

        # Display Results
        print("Results")
        for result in final_results:
            time = self.pretty_date(result["Time"])
            print(time, result["Coin"], result["Exchange"], result["Change"])


    # Find common coins
    def get_results(self, exchange):
        if exchange == 'bittrex':
            self.bittrex_data()
        elif exchange == 'binance':
            self.binance_data()

    ##
    # Check Prices Individuals
    ##
    def bittrex_data(self):
        summary = self.bittrex_api.getmarketsummaries()
        for item in summary:
            market = item['MarketName']
            if market.startswith('BTC-'):
                coin = market[4:]
                try:
                    high = item['High']
                    last = item['Last']
                    change = ((last - high) / high) * 100
                    if change < self.bittrex_change_check:
                        result = {"Coin": coin, "Exchange": 'Bittrex', "Change": change, 'Time': self.now}
                        self.bittrex_results.append(result)
                except Exception as e:
                    print(coin, e)

    def binance_data(self):
        url = "https://api.binance.com/api/v1/ticker/24hr"
        summary = requests.get(url).json()
        for item in summary:
            symbol = item["symbol"]
            if symbol.endswith("BTC"):
                coin = symbol[:-3]
                change = float(item["priceChangePercent"])
                if change < self.binance_change_check:
                    result = {"Coin": coin, "Exchange": 'Binance', "Change": change, 'Time': self.now}
                    self.binance_results.append(result)

    def pretty_date(self, time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.now()
        if type(time) is int:
            diff = now - datetime.fromtimestamp(time)
        elif isinstance(time,datetime):
            diff = now - time
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(round(second_diff, 1)) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(round(second_diff / 60, 1)) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(round(second_diff / 3600, 1)) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(round(day_diff, 1)) + " days ago"
        if day_diff < 31:
            return str(round(day_diff / 7, 1)) + " weeks ago"
        if day_diff < 365:
            return str(round(day_diff / 30, 1)) + " months ago"
        return str(round(day_diff / 365, 1)) + " years ago"


if __name__ == '__main__':

    while True:
        i = DumpCheck()
        print("\r\n")
        print('Restarting in 120 seconds...')
        time.sleep(120)

