import requests
from cracker_service import SUBDOMAIN, POST_ENDPOINT
import json
import argparse
import sys
from helper_functions import validate_port_range, create_list_guesses, divide_search_space, redivide_search_space, generate_random_word
import concurrent.futures
import time
import hashlib   
import csv

def send_message_to_server(md5_password, port, search_space:list):
    url = f"{SUBDOMAIN}:{port}{POST_ENDPOINT}"
     # try to send message to server; exit and return error message if failed
    try:      
        server_response = requests.post(
            url, 
            json={
                'md5_password': md5_password,
                'search_space': search_space
            }
        )
    except requests.exceptions.ConnectionError as e:
        return -1, None
    
    if server_response.ok:
        if server_response.status_code==200:
            return 0, server_response.json()['data']['decrypted_password']
        else:
            return 0, None
    else:
        return -2, None


if __name__ == '__main__':
    # instantiate argument parser

    start_port = 8000
    password_sizes = range(1, 7)
    num_workers_list = range(1,5)

    times = {password_size: {num_workers: 0 for num_workers in num_workers_list} for password_size in password_sizes}
    num_words_to_simulate = 10
    
    for password_size in password_sizes:
        for w in range(num_words_to_simulate):
            # generate random password and md5 hash
            password = generate_random_word(password_size)
            md5_password = hashlib.md5(password.encode()).hexdigest()
            max_password_length = password_size

            # decrypt password with varying number of workers
            for num_workers in num_workers_list:
                time_0 = time.time()
                end_port = start_port + num_workers - 1
        
                guesses = create_list_guesses(max_password_length)

                num_sets = end_port - start_port + 1
                search_spaces = divide_search_space(guesses, num_sets)
                valid_servers = [port for port in range(start_port, end_port+1)]

                found_password = False

                while True:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        # Start the threads and store the future objects in a list
                        futures = [executor.submit(send_message_to_server, md5_password,  port, search_space) 
                                        for port, search_space in zip(valid_servers, search_spaces)]

                        # Create a mapping from future objects to search spaces
                        futures_mapping = {future:[search_space, port] for future, search_space, port in zip(futures, search_spaces, valid_servers)}

                        # Iterate over the completed threads and retrieve the results
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                error_code, decrypted_password = future.result()

                                if error_code==-1:
                                    port = valid_servers.remove(futures_mapping[future][1])
                                    print(f"Warning: server running on port {futures_mapping[future][1]} is not responding. Removing from list of servers.")

                                elif error_code==-2:
                                    pass

                                elif decrypted_password:
                                    found_password = True
                                    for future_to_cancel in futures:
                                        future_to_cancel.cancel()
                                    break

                                else:
                                    search_spaces.remove(futures_mapping[future][0])
                                    
                            except Exception as e:
                                print(f"Thread raised an exception. Error message: {str(e)}. Error type:{type(e).__name__}")

                    if found_password:
                        time_diff = time.time() - time_0
                        times[password_size][num_workers] += time_diff
                        break
                    
                    if len(valid_servers)==0:
                        print("No more servers are responding but the password is still not decrypted. Please try again later.")
                        sys.exit(0)

                    if len(search_spaces)==0:
                        print("No password found. Please try again with a larger password_max_length parameter.")
                        sys.exit(0)
                    else:
                        search_spaces = redivide_search_space(search_spaces, len(valid_servers))

        for key,value in times[password_size].items():
            times[password_size][key] = value/(w+1)

        # write partial results to a csv file
        with open('performance_results.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # row format: "password_size, num_workers, time"
            for num_workers in num_workers_list:
                row = [password_size, num_workers, times[password_size][num_workers]]
                csv_writer.writerow(row)

    # write results to json file
    with open('performance_results.json', 'w') as f:
        json.dump(times, f, indent=4)
  
