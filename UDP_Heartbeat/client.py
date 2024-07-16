import datetime
import socket
import threading
import time


class Heartbeat:
    def __init__(self, seq_no, network_delay=0.0, dispatch_time=None):
        self.seq_no = seq_no
        self.dispatch_time = dispatch_time
        self.network_delay = network_delay

    def __str__(self):
        return f"heartbeat {self.seq_no} {self.dispatch_time}"

    def set_time(self):
        if not self.dispatch_time:
            self.dispatch_time = datetime.datetime.now().timestamp()

    @classmethod
    def get_heartbeat_list(cls, start=1, end=11):
        return [cls(x) for x in range(start, end)]


class Wait:
    def __init__(self, duration=1.0):
        self.duration = duration


class Client:
    def __init__(self, server_ip, server_port, dispatch_schedule: list, port=3000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.port = port
        self.clientSocket = None
        self.dispatch_schedule = dispatch_schedule

    def connect(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind(("", self.port))

    def start(self):
        for x in self.dispatch_schedule:
            if type(x) is Wait:
                print(f"sleeping for {x.duration} seconds")
                time.sleep(x.duration)
            elif type(x) is Heartbeat:
                x.set_time()
                self.clientSocket.sendto(str(x).encode(), (self.server_ip, self.server_port))


if __name__ == "__main__":
    client = Client(server_ip="localhost", server_port=2000,
                    dispatch_schedule=[Heartbeat(1),
                                       Heartbeat(2),
                                       Wait(4),
                                       *Heartbeat.get_heartbeat_list(5, 11),
                                       Wait(6),
                                       *Heartbeat.get_heartbeat_list(1, 6),
                                       Wait(5),
                                       Heartbeat(9),
                                       Wait(5),
                                       Heartbeat(1, 5.0),
                                       *Heartbeat.get_heartbeat_list(2, 11),
                                       ], )
    client.connect()
    client.start()
