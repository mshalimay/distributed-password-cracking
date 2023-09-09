import requests
from cracker_service import SUBDOMAIN, POST_ENDPOINT
import json
import argparse
import sys
from helper_functions import validate_port_range, create_list_guesses, divide_search_space, redivide_search_space
import concurrent.futures

   
def send_message_to_server(md5_password:str, port:int, search_space:list):
    """ Send a message to the server with the md5 password and search space
    if server does not respond or responds with status != 2xx, return error codes

    Args:
        md5_password (str): the hashed password to be decrypted
        port (int): the port number where the decryption service is running
        search_space (list): a list of guesses the server should use to try to decrypt the hashed password

    Returns:
        error code(int): 
            0: server responded with status 2xx
            -1: server did not respond; 
            -2: server responded with status != 2xx
        decrypted_password (str): decrypted password if server was able to decrypt; else None

        response (dict): response covertible to JSON with more information about communication with server
    """
    # construct url and to send message to server; exit and return error message if failed
    url = f"{SUBDOMAIN}:{port}{POST_ENDPOINT}"
     
    try:      
        server_response = requests.post(
            url, 
            json={
                'md5_password': md5_password,
                'search_space': search_space
            }
        )
    except requests.exceptions.ConnectionError as e:
        response = {
            "code": 500,
            "status": "error",
            "message": f"Failed to submit the job to the decryption server due to connection error."
        }
        return -1, None, response
    
    if server_response.ok:
        if server_response.status_code==200:
            return 0, server_response.json()['data']['decrypted_password'], server_response.json()
        else:
            response_content = json.loads(server_response.text)
            message = response_content.get('message', None)
            response = {
                "code": server_response.status_code,
                "status": "error",
                "message": f"Failed to submit the job to the decryption server. Please try submitting your password again." +
                           f" Response status code from server: {server_response.status_code}. " +
                           f" Error message received from server: {message}."
            }
            return 0, None, response
    else:
        response_content = json.loads(server_response.text)
        message = response_content.get('message', None)
        response = {
            "code": server_response.status_code,
            "status": "error",
            "message": f"Failed to submit the job to the decryption server. Please try submitting your password again." +
                       f" Response status code from server: {server_response.status_code}. " +
                       f" Error message received from server: {message}."
        }
        return -2, None, response


if __name__ == '__main__':
    # instantiate argument parser
    parser = argparse.ArgumentParser()

    # take md5_password and max_password_length from command line
    parser.add_argument("start_port", type=int, help="Integer between 1024 and 65535 representing the port number where the decryption service is running.", metavar="<start-port>")
    parser.add_argument("end_port", type=int, help="Integer between 1024 and 65535 representing the port number where the decryption service is running.", metavar="<end-port>")

    parser.add_argument("md5_password", type=str ,help="The md5 hash of the password to be decrypted", metavar='<md5_password>')
    parser.add_argument("max_password_length", type=int, help="The maximum length of the password to be decrypted", metavar='<max_password_length>')

    # if invalid arguments, print help message and exit
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as err:
        parser.print_help()
        sys.exit(2)

    locals().update(vars(args))


    # ## hand inputs for debugging
    # start_port = 5000
    # end_port = 5002
    # md5_password = "cce6b3fb87d8237167f1c5dec15c3133"
    # max_password_length = 4
    
    # validate port range; exit and return error message if invalid
    port_error_message = validate_port_range(start_port, end_port)
    if port_error_message:
        print(port_error_message)
        sys.exit(0)

    num_sets = end_port - start_port + 1

    guesses = create_list_guesses(max_password_length)

    search_spaces = divide_search_space(guesses, num_sets)
    valid_servers = [port for port in range(start_port, end_port+1)]

    first_iteraton = True
    
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
                    error_code, decrypted_password, response = future.result()

                    if error_code==-1:
                        port = valid_servers.remove(futures_mapping[future][1])
                        print(f"Warning: server running on port {futures_mapping[future][1]} is not responding. Removing from list of servers.")

                    elif error_code==-2:
                        print(f"Warning: server running on port {futures_mapping[future][1]} sent error message.")
                        print("Details:")
                        print(json.dumps(response, indent=4))                      

                    elif decrypted_password:
                        print(f"\nThe password was decrypted!\nDecrypted password: {decrypted_password}")
                        sys.exit(0)

                    else:
                        search_spaces.remove(futures_mapping[future][0])
                        
                except Exception as e:
                    print(f"Thread raised an exception. Error message: {str(e)}. Error type:{type(e).__name__}")
    
        if len(valid_servers)==0:
            print("No more servers are responding but the password is still not decrypted. Please try again later.")
            sys.exit(0)

        if len(search_spaces)==0:
            print("No password found. Please try again with a larger password_max_length parameter.")
            sys.exit(0)
        else:
            search_spaces = redivide_search_space(search_spaces, len(valid_servers))            
        