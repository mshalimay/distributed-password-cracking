from flask import Flask, render_template, request, jsonify
import hashlib
from helper_functions import validate_port
import sys

# instantiate the Flask server
server = Flask(__name__)

SUBDOMAIN = f"http://localhost"
POST_ENDPOINT = "/decryption" 

def decrypt_password(hashed_password:str, search_space:list):

    # check if the password is in the cache
    decrypted_password = lookup_password(hashed_password)
    if decrypted_password is not None:
        return decrypted_password

    # if not in the database, try to decrypt it
    for guess in search_space:
        if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
            return guess
    return None

def store_password(hashed_password:str, decrypted_password:str):   
    # read the file contents into a set; if file not exist, create an empty set
    try:
        with open("passwords.txt", "r") as f:
            # put contents of the file into a set
            passwords = set(f.read().splitlines())
    except FileNotFoundError:
        passwords = set()

    # add the new password to the set
    passwords.add(f"{hashed_password}:{decrypted_password}")

    with open("passwords.txt", "w") as f:
        # write the set back to the file
        for password in passwords:
            f.write(password + "\n")
        
def lookup_password(hashed_password):
    # open the passwords cache file and look for the hashed password
    try:
        with open("passwords.txt", "r") as f:
            # read the file contents into dictionary
            passwords = dict([line.strip().split(":") for line in f.readlines()])

            if hashed_password in passwords:
                return passwords[hashed_password]
            else:
                return None
    except FileNotFoundError:
        return None
            
@server.route(POST_ENDPOINT, methods=['POST'])
def decrypt():
    # check if content-type header is present and of type 'application/json'
    header = request.headers.get('Content-Type')
    if header != 'application/json':
        response = {
            "code": 415,
            "status": "error",
            "message": "missing content-type header or unsuported format. Expected 'application/json'",
        }
        return jsonify(response), 415

    #check if request body is empty
    if not request.data:
        response = {
            "code": 400,
            "status": "error",
            "message": "missing request body",
        }
        return jsonify(response), 400

    # parse request body
    try:
        # extract parameters from request body
        client_request = request.json
        md5_password = client_request['md5_password']
        search_space = client_request['search_space']
        
    except KeyError as e:
        response = {
            "code": 400,
            "status": "error",
            "message": f"Key Error. Request body is missing fields: {str(e)}.",
        }
        return jsonify(response), 400
    except Exception as e:
        response = {
            "code": 400,
            "status": "error",
            "message": f"Unexpected error. Error message: {str(e)}. Error type: {type(e).__name__}",
        }
        return jsonify(response), 400

    # Do the password decryption
    try:
        decrypted_password = decrypt_password(md5_password, search_space)

        if decrypted_password is not None:
            response = {
                    "code": "200",
                    "status": "success",
                    "message": "The password was decrypted successfully.",
                    "data": {
                        "md5_password": md5_password,
                        "decrypted_password": decrypted_password
                    }
                }
            store_password(md5_password, decrypted_password)
            return jsonify(response), 200

        else:
            response = {
                    "code": "204",
                    "status": "No content",
                    "message": "Your request was received, but the password could not be decrypted. Try changing the maximum password length.",
                    "data": {
                        "md5_password": md5_password,
                        "decrypted_password": None
                    }
                }
            return jsonify(response), 202

    except OSError as e:
        response = {
            "code": "500",
            "status": "failure",
            "message": f"Failure due to internal filesystem error. Error message: {str(e)}."
        }
        return jsonify(response), 500
            
    except Exception as e:
        response = {
            "code": "400",
            "status": "failure",
            "message": f"Failure due to an unexpected error. Error message: {str(e)}. Error type: {type(e)}"
        }    
        return jsonify(response), 400


if __name__ == '__main__':
    import argparse
    # instantiate argument parser
    parser = argparse.ArgumentParser()

    # take md5_password and max_password_length from command line
    parser.add_argument("port", type=int, help="Integer between 1024 and 65535 representing the port number where the decryption service is running.", metavar="<port>")
    args = parser.parse_args()

    
    port_error_message = validate_port(args.port)
    if port_error_message:
        print(port_error_message)
        sys.exit(0)
    
    server.run(host='0.0.0.0', port=args.port)