from growwapi import GrowwAPI

from utils import Utils


class PutSpreadTrade:
    def __init__(self, groww: GrowwAPI):
        self.utils = Utils(groww)

    def put_spread(self):
        print("PUT Spread")