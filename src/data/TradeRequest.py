from src.constants.Constants import TradeResponse


class TradeRequest(object):
    def __init__(self):
        self.items = None
        self.timeout_in_minutes = 3
        self.player_a = None
        self.player_b = None
        self.player_a_name = None
        self.player_b_name = None
        self.player_a_dm_message = None
        self.player_b_dm_message = None
        self.player_a_response = TradeResponse.pending
        self.player_b_response = TradeResponse.pending
        self.expire_time = None
        self.request_start = None
        self.origin_message = None
        self.comments = None

    def timeout_in_seconds(self):
        return self.timeout_in_minutes * 60
