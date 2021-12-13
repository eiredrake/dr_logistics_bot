from enum import Enum, auto, IntEnum

DATE_FORMAT = '%m/%d/%Y'
TWELVE_HOUR_TIME_FORMAT = '%I:%M:%S %p'
DATE_WITH_TWELVE_HOUR_TIME_FORMAT = DATE_FORMAT + " " + TWELVE_HOUR_TIME_FORMAT

class SkillLevel(IntEnum):
    basic = auto()
    proficient = auto()
    master = auto()

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class SkillCategory(IntEnum):
    anomaly = 1
    wasteland = 2
    civilized = 3
    combat = 4

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class Strain(IntEnum):
    Elitariat = auto()
    Digitarian = auto()
    Solestros = auto()
    Pure_Blood = auto()
    Baywalker = auto()
    Yorker = auto()
    Vegasian = auto()
    Diesel_Jock = auto()
    Rover = auto()
    Saltwise = auto()
    Full_Dead = auto()
    Semper_Mort = auto()
    Lascarian = auto()
    Remnant = auto()
    Retrograde = auto()
    Tainted = auto()
    Merican = auto()
    Natural_One = auto()
    Quiet_Folk = auto()
    Accensorite = auto()
    Red_Star = auto()
    Unborn = auto()
    Iron = auto()
    Reclaimer = auto()
    Unstable = auto()

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


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
