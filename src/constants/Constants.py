from enum import Enum, auto, IntEnum

DATE_FORMAT = '%m/%d/%Y'
TWELVE_HOUR_TIME_FORMAT = '%I:%M:%S %p'
DATE_WITH_TWELVE_HOUR_TIME_FORMAT = DATE_FORMAT + " " + TWELVE_HOUR_TIME_FORMAT
CANCEL_EMOJI ='\U0000274C'
GREEN_CHECKMARK_EMOJI ='\U00002705'
A_EMOJI = '\U0001F170'
B_EMOJI = '\U0001F171'
OK_EMOJI = '\U0001F197'
NO_EMOJI = '\U0001F6AB'
ACCEPT_TRADE ='accept trade'
CANCEL_TRADE = 'cancel trade'
CANCEL_ACTION = 'cancel action'
DELETE_ACTION = 'delete'


BOT_COMMANDER_ROLE = 'Bot Commander'
WRITER_ROLE = 'Writer'
GUIDE_ROLE = 'Guide'
FULL_TICKET_ROLE = 'Full Ticket'
STAFF_ROLE = 'Staff'

SUBMIT_RESEARCH = 'Submit Research'
CANCEL_RESEARCH = 'Cancel'
DELETE_BUTTON_TEXT = 'DELETE'


class TradeResponse(Enum):
    pending = auto()
    accepted = auto()
    cancel = auto()

    def __str__(self):
        return self.name


class Status(Enum):
    open = auto()
    closed = auto()
    close = closed

    @staticmethod
    def parse(argument: str):
        try:
            return Status[argument.lower()]
        except KeyError:
            raise KeyError('Unknown Status type \'%s\' given.' % argument.lower())

    @staticmethod
    def to_list(separator: str = '|'):
        return separator.join(str(element[0]) for element in Status.__members__.items())

    def __str__(self):
        return self.name


class ActionType(IntEnum):
    brew = auto()
    build = auto()
    cook = auto()
    consume = auto()
    do = auto()
    farm = auto()
    forage = auto()
    hunt = auto()
    inject = auto()
    salvage = auto()
    smoke = auto()
    spend = auto()
    trailblaze = auto()
    upgrade = auto()
    use = auto()
    repair = auto()

    def __str__(self):
        return self.name

    @staticmethod
    def to_list(separator: str = '|'):
        return separator.join(str(element[0]) for element in ActionType.__members__.items())

    @staticmethod
    def parse(input_string: str):
        if input_string is None or len(input_string) <= 0:
            raise KeyError('An empty string was given')

        try:
            return ActionType[input_string.lower()]
        except KeyError:
            raise KeyError('Unknown skill type \'%s\' given.' % input_string)


class LockedActionType(IntEnum):
    brew = ActionType.brew
    build = ActionType.build
    cook = ActionType.cook
    farm = ActionType.farm
    forage = ActionType.forage
    hunt = ActionType.hunt
    salvage = ActionType.salvage
    trailblaze = ActionType.trailblaze
    upgrade = ActionType.upgrade

    def __str__(self):
        return self.name

    @staticmethod
    def to_list(separator: str = '|'):
        return separator.join(str(element[0]) for element in LockedActionType.__members__.items())

    @staticmethod
    def is_locked_action(actionType: ActionType):
        result = False

        for element in ActionType.__members__.values():
            if actionType == element:
                result = True
                break

        return result
