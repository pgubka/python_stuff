import json

class StatsAnalyzer:
    def __init__(self, result_file):
        self._result_file = result_file
        with open(self._result_file) as fd:
            self._results = json.load(fd)
        self._prize_mapping = {52:1, 51:2, 50:3, 42:4, 41:5, 40:6, 32:7, 31:8, 22:9, 30:10, 12:11, 21:12}

    def get_result_by_date(self, date):
        return self._results[date]

    def get_results(self):
        return self._results

    def check_combination(self, balls, euros):
        winnings = []
        for date in self._results.keys():
            match = self._check(balls, euros, date)
            if match > 0:
                winnings.append((date, match))
        return winnings 

    def _check(self, balls, euros, date):
        numbers = self._results[date]
        match = 0;
        for ball in balls:
            if ball in numbers[0]:
                match += 10
        for euro in euros:
            if euro in numbers[1]:
                match += 1
        return match
