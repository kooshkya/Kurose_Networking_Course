# Simple Message Server With Python

### Short Description:
This project creates and implements a simple messagin application-layer protocol on a multi-threaded python server.

### Tools Used:
- The Python socket module
- The Python threads module
- TCP Socket programming knowledge

### How to run:
- install python
- run `python3 server.py`
- on a different terminal, run `nc localhost 2001`
- repeat the before step to create as many clients as you wish
- use the nc tools to communicate with the server

### Description:
I did this exercize instead of the webserver task. Implementing http manually didn't seem that educative, so I decided to create my own simple text-based (and amazingly useless) messaging protocol. Such is the protocol:
- when a client connects through TCP, the server sends them a message informing them of their `id`. This is the format of this message:
`Your id is <id>`
- The client can send a message to another client using the second client's id. suppose the sender's id is 1 and the receiver's id is 2. The sender sends this message to the server:
`@2 <message body>` for example: `@2 hello there!`
- Clients will get their messages in real time in this format:
`from <id>: <message body>` for example, the user at id 2 will receive this message: `from 1: hello there!`
- If the id that a client wishes to send a message to isn't online or doesn't exist, an error message is sent to that client.
- If the client's message doesn't conform to the described format, an appropriate error message is generated.
- I used the `netcat` CLI tool to mimic clients. On several terminals, I ran netcat to connect to `localhost:2001` on a tcp connection. stdin and stdout were then used to communicate with the server.

The full description for the original task can be found here: https://gaia.cs.umass.edu/kurose_ross/programming/Python_code_only/WebServer_programming_lab_only.pdf
