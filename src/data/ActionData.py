from logistics.models import ActionRecord


class ActionData(object):
    def __init__(self):
        self.action_user = None
        self.action_type = None
        self.items = None
        self.origin_message = None
        self.timer = None
        self.quantity = 1
        self.mind_cost = 5
        self.time_cost = 20
        self.resolve_cost = 0
        self.commentary = None
        self.materials = None
        self.start_time = None
        self.time_of_completion = None
        self.action_accept_message = None

    def get_time_cost_in_seconds(self):
        return self.time_cost * 60

    def get_time_cost_in_minutes(self):
        return self.time_cost

    def to_action_record(self):
        result = ActionRecord()
        result.action_start = self.start_time
        result.interrupted = True
        result.actor_discord_id = self.action_user.id
        result.actor_display_name = self.action_user.display_name
        result.action_type = int(self.action_type)
        result.items = self.items
        result.quantity = self.quantity
        result.mind_cost = self.mind_cost
        result.time_cost = self.time_cost
        result.resolve_cost = self.resolve_cost
        result.materials = self.materials
        result.commentary = self.commentary

        return result

