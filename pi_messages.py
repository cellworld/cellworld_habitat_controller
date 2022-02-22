from json_cpp import JsonObject, JsonList


class TestFeederResponse(JsonObject):
    def __init__(self, feeder_num: int = 0, feedtime: int = 0, repetition: int = 0, wait_time: int = 0):
        self.feeder_num = feeder_num
        self.feedtime = feedtime
        self.repetition = repetition
        self.wait_time = wait_time


class TestDoorResponse(JsonObject):
    def __init__(self, door_num: int = 0, repetition: int = 0):
        self.door_num = door_num
        self.repetition = repetition


class DoorInfo(JsonObject):
    def __init__(self, num: int = 0, state: str = ''):
        self.num = num
        self.state = state


class DoorInfoList(JsonList):
    def __init__(self):
        JsonList.__init__(self, list_type=DoorInfo)


class StatusResponse(JsonObject):
    def __init__(self, ID: str = '', door_state: DoorInfoList = None, feeder_state: str = ''):
        self.ID = ID
        if not door_state:
            door_state = DoorInfoList()
        self.door_state = door_state
        self.feeder_state = feeder_state
