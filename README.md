## Short description
A multithreaded and distributed password cracker using a brute-force method with caching. 

Given a hashed password, the client divides the search space among multiple FLask servers responsible for decrypting the password.The client loops receiving messages from the server until the password is cracked.

Communication: through JSON following the REST protocol.

Fault-tolerance: if a server goes down, the client redistributes the workload among the remaining servers

Cache: servers cache previously cracked passwords to a local file for faster cracking in following attempts.


## Instructions

1) To deploy the crack services, execute:

`python cracker_service.py <port>`

- `port` is the port the server will bind to

Execute this command in more than one CMD to simulate multiple cracking services.


2)To deploy the client, execute:

`python client.py [-h] <start-port> <end-port> <md5_password> <max_password_length>`

- `start-port`: Integer between 1024 and 65535 representing the starting number of the range of decryption services running.
- `end-port`: Integer between 1024 and 65535 representing the end number of the range of decryption services running.
- `md5_password`: The hashed password.
- `max_password_length`: The maximum length of the password to be decrypted.



3) To generate a hashed password, can use

`hashlib.md5(password.encode()).hexdigest()`

4) The `performance_client` offer some functionality to test performance. Modify the parameters in the `main` function as you see fit.