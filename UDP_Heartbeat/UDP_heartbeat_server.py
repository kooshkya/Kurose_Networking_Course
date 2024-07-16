import socket
import datetime
import threading


class MonitoredClient:
    def __init__(self, address: tuple, timeout: float = 10.0):
        self.address = address
        self.timeout = timeout
        self.frame_start = None
        self.frame_heartbeats_lock = threading.Lock()
        self.frame_heartbeats = []

    def start_monitoring(self, frame_start=None):
        self.frame_start = frame_start or datetime.datetime.now().timestamp()
        self.frame_heartbeats = []
        timer = threading.Timer(self.timeout, self.check_heartbeat)
        timer.start()

    def check_heartbeat(self):
        with self.frame_heartbeats_lock:
            frame_heartbeats = self.frame_heartbeats[:]
        if not frame_heartbeats:
            print(f"Client {self.address} has no heartbeats!")
        else:
            frame_start = self.frame_start
            self.process_stats(frame_heartbeats, frame_start)
        self.start_monitoring()

    def process_stats(self, heartbeats: list, frame_start: float):
        frame_end = frame_start + self.timeout
        range_count = 5
        interval = (frame_end - frame_start) / range_count
        ranges = [(frame_start + x * interval, frame_start + (x + 1) * interval) for x in range(range_count)]
        range_dispatches = []
        range_arrivals = []
        for r in ranges:
            range_dispatches.append([])
            range_arrivals.append([])
            for heartbeat in heartbeats:
                if r[0] <= heartbeat.dispatch_time < r[1]:
                    range_dispatches[-1].append(str(heartbeat.seq_num))
                if r[0] <= heartbeat.arrival_time < r[1]:
                    range_arrivals[-1].append(str(heartbeat.seq_num))
        print(f"total heartbeats received: {len(heartbeats)}")
        print(f"arrivals:")
        for batch in range_arrivals:
            print(", ".join(batch) or "None", end="")
            print(f"\t\t", end="")
        print()
        print(f"dispatches:")
        for batch in range_dispatches:
            print(", ".join(batch) or "None", end="")
            print(f"\t\t", end="")
        print()

    def add_heartbeat(self, seq_num, dispatch_time):
        with self.frame_heartbeats_lock:
            self.frame_heartbeats.append(Heartbeat(self, seq_num, dispatch_time, datetime.datetime.now().timestamp()))

    def validate_heartbeat(self, dispatch_time):
        # Checks if the heartbeat belongs to the current frame
        result = dispatch_time >= self.frame_start
        return result


class Heartbeat:
    def __init__(self, client: MonitoredClient, seq_num: int, dispatch_time, arrival_time):
        self.client = client
        self.seq_num = seq_num
        self.dispatch_time = dispatch_time
        self.arrival_time = arrival_time


def extract_fields_from_data(data_str: str):
    data_parts = data_str.split()
    seq_num = int(data_parts[1])
    dispatch_time = float(data_parts[2])
    return seq_num, dispatch_time


class Server:
    PORT = 2000

    def __init__(self):
        self.clients = dict()
        self.serverSocket = None

    def connect(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(("", self.PORT))
        print(f"Server is now connected to {self.serverSocket.getsockname()}")

    def disconnect(self):
        if self.serverSocket:
            self.serverSocket.close()
        self.serverSocket = None
        print(f"Server is now disconnected")

    def run(self):
        try:
            print(f"Server is now listening on port {self.PORT}")
            while True:
                data, source = self.serverSocket.recvfrom(1024)
                seq_num, dispatch_time = extract_fields_from_data(data)
                if source not in self.clients:
                    client = MonitoredClient(source, 10)
                    self.clients[source] = client
                    client.start_monitoring(dispatch_time)
                    client.add_heartbeat(seq_num, dispatch_time)
                    print(f"now monitoring {source}")
                else:
                    client = self.clients[source]
                    if client.validate_heartbeat(dispatch_time):
                        client.add_heartbeat(seq_num, dispatch_time)
                    else:
                        print(f"heartbeat {seq_num} NOT accepted for for {source}")
        except Exception as e:
            print(f"error: {e}")
        finally:
            self.disconnect()


if __name__ == "__main__":
    server = Server()
    server.connect()
    server.run()
    server.disconnect()
