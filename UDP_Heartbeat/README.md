## UDP Heartbeat Server and Client

### Description:
This project consists of a healthcheck server that uses periodical heartbeats
sent from clients on UDP to check that they are still up.

### Overview of Protocol:
Clients are registered on the server by specifying their address (IP and port number)
and a timeout period. Every timeout period, the client must send a series of
UDP requests, collectively called a `full heartbeat message` to the server.


`full heartbeat message`: Is a string of 10 UDP requests each having format

`heartbeat <sequence number> <time>`

where `sequence number` is a number from 1 to 10 depending on the request's
place in the order that the client issued the 10 requests. 
Also, `time` is the timestamp of the time when the request was issued from 
the client


### Assumptions:
- It is assumed that as long as the client is functional, it sends 10
appropriately-formatted and correctly-ordered UDP requests (A.K.A. a full heartbeat message)
to the server. 
- It is assumed that the network layer is an unreliable courier and that
issued UDP requests from the client might get lost.
- It is an accepted risk that all 10 requests from a client might
be lost in the network (or delayed long enough that that they reach the server 
after a failure alarm has been sounded) 
and the server might incorrectly announce the failure
of a client. But this event is assumed to be improbable enough that the
generation rate of false alarms due to this fact is negligible.
- It is assumed that no malicious actors will be injecting out-of-order or malformed
requests to confuse the server or imitate actual clients (not an unrealistic
assumption if the system is to be deployed at a private, protected datacenter.)
- Even if only one of the ten heartbeat requests reaches the server, the
client is assumed to be functional.

  
### Execution:
- First run the server by executing `python UDP_heartbeat_server.py`
- Run the client using `python client.py`
- Read the code to customize behavior
