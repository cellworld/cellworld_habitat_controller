from tcp_messages import MessageClient, Message
from pi_messages import *

class PiClient(MessageClient):
    def __init__(self):
        MessageClient.__init__(self)

    def subscribe(self):
        return self.send_request(Message("!subscribe"), 0).body == "success"

    def connect(self, ip: str = "127.0.0.1") -> str:
        if ip == "192.168.137.101":
            port_num = 4610
        else:
            port_num = 4620
        return MessageClient.connect(self, ip, port_num)

    def open_door(self, door_num: int) -> str:
        return self.send_request(Message("open_door", door_num), 5000).get_body(str)

    def close_door(self, door_num: int) -> str:
        return self.send_request(Message("close_door", door_num), 5000).get_body(str)

    # def calibrate_door(self, door_num: int) -> str:
    #     return self.send_request(Message("calibrate_door", door_num), 5000).get_body(str)

    def save_calibration(self) -> str:
        return self.send_request(Message("save_calibration"), 5000).get_body(str)

    def status(self) -> str:
        return self.send_request(Message("status"), 5000).get_body(StatusResponse)

    def give_reward(self, feeder_num: int) -> str:
        return self.send_request(Message("give_reward", feeder_num), 5000).get_body(str)

    def enable_feeder(self, feeder_num: int) -> str:
        return self.send_request(Message("enable_feeder", feeder_num), 5000).get_body(str)

    def feeder_reached(self, feeder_num: int) -> str:
        return self.send_request(Message("feeder_reached", feeder_num), 5000).get_body(str)

    def test_feeder(self, feeder_num: int, feedtime: int, repetition: int, wait_time: int ) -> str:
        parameters = TestFeederResponse(feeder_num=feeder_num, feedtime=feedtime, repetition=repetition, wait_time=wait_time)
        return self.send_request(Message("test_feeder", parameters), 5000).get_body(str)

    def test_door(self, door_num: int, repetition: int) -> str:
        parameters = TestDoorResponse(door_num=door_num, repetition=repetition)
        return self.send_request(Message("test_door", parameters), 5000).get_body(str)