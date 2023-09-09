# homework-4-mshalimay
# Part 2

First of all, I deployed different cracking services in different ports using separate command lines.

Then to test this part, I did a couple of things:
1) Ran the code in debug mode and:
	- verified the division algorithm was correctly dividing the search space
		- the division algorithms correctness were verified separately, inside the `helper_functions.py` file. The tests are indicated and commented out in the file
	- Inserted breakpoints in each branch inside the `for future in concurrent.futures.as_completed(futures):` loop. Then I checked if different workers were running by running until the breakpoints were triggered (which would occur only if there were more than one concurrent jobs in the for loop)
	- I purposefully made some servers respond with bad messages, in which case different breakpoints would have to be triggered 

2)  In the `send_message_to_server`, I inserted a line printing to the console the port the concurrent job was connecting  (it is commented out in the code). This way, every time a concurrent thread was deployed I could see in the console the print message

3) I also checked the terminals of each deployed server to see if they were receiving requests from the clients concurrently. 

It is worth noticing that the way the code is written, if a password that should be cracked with 100% probability is not cracked, it is necessarily because the jobs were not distributed correctly (for instance, if some search space lacked guesses). Therefore, randomly generating passwords, passing then with the exact necessary password_max_length for cracking and veryfing that the passwords are cracked is another way to verify the jobs were properly divided. This was done in part 4, during the performance tests - notice the `print("No password found. Please try again with a larger password_max_length parameter.")`  would indicate when passwords were not found.

# Part 3
- To test this part, I deployed different cracking services in different ports using separate command lines.

To test this part, I ran the code in debug mode and:
	1) Inserted ports that were purposefully wrong and checked if the search space was properly *redivided*. That is, the loop responsible for concurrent execution started some inputed invalid ports, which is the same as having a server that is off. In this case, the search space *must* be redivided and I checked in the debug mode if this was the case
	2) Inserted breakpoints in the lines responsible for fault tolerance (`(if error code == -1`), forced stopped some of the cracking services in the command line and checked if the breakpoints were being activated and the search space was properly redivided


Given I checked the redivision algorithms were working (see Part 2 above) and that in Part 2 and  the client correctly computed the passwords, properly redividing the jobs was sufficient to see that falt tolerance was working.

Moreover, as commented in Part 2, by the way the code is written, if a password that should be cracked with 100% probability is not cracked, it is necessarily because the jobs were not distributed correctly (for instance, after fault tolerance the search space is not correctly divided between the remaining servers). Therefore, randomly generating passwords, passing then with the exact necessary password_max_length for cracking and veryfing that the passwords are cracked is another way to verify the jobs were properly divided. In part 4, during the performance tests, I passed wrong ports and force stopped some of then during the execution of simulations. The `print("No password found. Please try again with a larger password_max_length parameter.")`  would indicate when passwords were not found and it was not triggered.

# Part 4

Fault tolerance is dealt by removing servers when they do not respond and redividing the search space evenly among the remaining servers. 

For this part, I generated a range of random strings of lengths 1 to 5, hashed them and ran the client to decrypt them. After finishing a batch of simulations for a specified word lenght, I took the average time to decrypt for each case (1 server, 2 servers, etc). The maximum number of servers deployed concurrently was 10.

The script `performance_client.py` contains the code for the simulations described above. The parameters for simulations can me modified in the `main` block

The image below shows the times when varying the word length and number of servers working.
Comments:
- For very small words, (word lens 1,2,3) there is to no gain of increasing the number of decryption servers. This is probably due to the fact that passwords are easier to crack and this do not compensate the overhead of dividing the passwords among workers
- As the max_word_length grows, the average time to completion is smaller when more cracking services are deployed. The case word length = 5 illustrates this best
- There is some variance in time as the number of servers grow (see word len 4, where it first decreases then increases). I did not have time to investigate this, but one possible reason is due to resource allocation in my local machine during the spawning process.

![Sample image](https://github.com/mpcs-52040/homework-4-mshalimay/blob/main/times.png)

# Part 5

To implement the cache, I introduced in the `cracker_service.py` lines that:
1) saved the hashed and cracked password into a local text file in case the password is cracked by one of the concurrent servers.

2) looked in the 'saved cache file' for the  hashed password before trying to brute force decrypt and return it in case it is found in the cache file 
	- obs: the text file is open in read mode only, so there is no problem of concurrent threads trying to look it up

Obs: in a more complex implementation, the cracked passwords can be saved in a database or other more complex file structures; I adopted this simple approach of saving to a local as it suffices for the assignment and illustrate the use of cache



