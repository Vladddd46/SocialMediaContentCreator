from typing import List


class Schedule:

    def __init__(self, every_days: int, time: List[str]):
        self.every_days = every_days
        self.time = time

    def __repr__(self):
        return f"Schedule(every_days={self.every_days}, time={self.time})"

    def __str__(self):
        times = ', '.join(self.time)
        return f"Schedule: Every {self.every_days} days at times [{times}]"