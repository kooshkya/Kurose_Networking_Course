import socket
import threading
import re
import select

PORT = 2001

connection_count = 0
connection_count_lock = threading.Lock()

user_ids = {}
user_ids_lock = threading.Lock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", PORT))
server_socket.listen(5)
print(f"Waiting for connections at port {PORT}")


def dissect_message(msg):
    parts = msg.split()
    user_id = parts[0][1:]
    message = " ".join(parts[1:])
    return int(user_id), message
    

def serve_connection(conn, addr):
    global connection_count
    connection_id = 0
    with connection_count_lock:
        connection_count += 1
        connection_id = connection_count
        with user_ids_lock:
            user_ids.update({connection_id: []})
    print(f"{connection_id}: Connection established with {addr}")

    bc = conn.send(f"Your id is {connection_id}\n".encode())    
    if bc:
        while True:
            with user_ids_lock:
                if (messages := user_ids.get(connection_id, [])):
                    while messages:
                        message = messages[0]
                        bc = conn.send((message + "\n").encode())
                        if not bc:
                            print(f"{connection_id}: Connection was broken by client")
                            break
                        messages.remove(message)
                            
            read_ready, _, _ = select.select([conn], [], [], 3.0)
            if read_ready:
                data = conn.recv(200)
                if not data:
                    print(f"{connection_id}: Connection was broken by client")
                    break
                
                data = data.decode()
                if not re.match(r"@\d+\s.*", data):
                    bc = conn.send(f"Invalid\n".encode())
                    if bc == 0:
                        print(f"{connection_id}: Connection was broken by client")
                        break
                else:
                    user_id, message = dissect_message(data)
                    with user_ids_lock:
                        if not user_id in user_ids.keys():
                            bc = conn.send(f"Contact Offline\n".encode())
                            if bc == 0:
                                print(f"{connection_id}: Connection was broken by client")
                                break
                        else:
                            user_ids[user_id].append(f"from {connection_id}: {message}")
                            bc = conn.send(f"Sent\n".encode())
                            if bc == 0:
                                print(f"{connection_id}: Connection was broken by client")
                                break
        
    with user_ids_lock:
        user_ids.pop(connection_id)
    conn.close()
    print(f"{connection_id}: Connection closed")


try:
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=serve_connection, args=(conn, addr))    
        thread.start()
finally:
    server_socket.close()