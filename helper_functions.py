import random
import string
import itertools

def validate_port(port:str) -> str:
    """ Validates the port number inputed by user, returning an error message if it is invalid
    Valid port number = integer between 1024 and 65535
    """
    if (port) < 1024 or (port) > 65535:
        return "Please enter a port number between 1024 and 65535."
    return ""

def validate_port_range(start_port, end_port):
    if start_port < 1024 or start_port > 65535:
        return "Please enter a starting port number between 1024 and 65535."
    elif end_port < start_port:
        return "Please enter an end port number greater than the start port number."
    return ""

def create_list_guesses(max_password_length, ignore_case = True):
    if ignore_case:
        chars = string.ascii_lowercase # all lowercase characters
    else:
        chars = string.printable # all printable characters
    guesses = []
    for password_length in range(1, max_password_length+1):
        for guess in itertools.product(chars, repeat=password_length):
            guess = "".join(guess)
            guesses.append(guess)
    return guesses

def divide_search_space(guesses, num_sets):
    num_sets = min(num_sets, len(guesses))
    search_spaces = [[] for _ in range(num_sets)]
    start=0
    for search_space in search_spaces:
        j = 0
        for i in range(start, len(guesses), num_sets):
            search_space.append(guesses[i])
            j+=1
        start+=1
    return search_spaces

def redivide_search_space(divided_search_space, num_sets):
    # flatten the list of lists
    guesses = [guess for search_space in divided_search_space for guess in search_space]
    return divide_search_space(guesses, num_sets)


def generate_random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

     
if __name__ == "__main__":
    pass
    
    #==================================================
    # Check correcteness of the redivision algorithms
    #==================================================
    # create a list of guesses

    # guesses = create_list_guesses(5)

    # # divide the search space into 7 sets
    # x = divide_search_space(guesses, 2)

    # # redivide the search space into 3 sets
    # xx = redivide_search_space(x,30)

    # # flatten the lists for comparison
    # flat_x = [item for sublist in x for item in sublist]
    # flat_xx = [item for sublist in xx for item in sublist]

    # # sort all the lists
    # flat_x.sort()
    # flat_xx.sort()
    # guesses.sort()

    # # check if all the lists are the same as the original list of guesses
    # incorrect = False
    # if len(flat_x) != len(guesses) or len(flat_xx) != len(guesses):
    #     incorrect=True
        
    # else:
    #     for i in range(len(flat_x)):
    #         if flat_x[i] != guesses[i] or flat_xx[i] != guesses[i]:
    #             incorrect=True
    #             break

    # if incorrect:
    #     print("Incorrect")

    # #==================================================
    # # Compare performance of the redivision algorithms
    # #==================================================
    # import time
    # n_iterations = 100
    

    # guesses = create_list_guesses(5)
    # search_spaces = divide_search_space(guesses, 10)

    # time_0 = time.time()
    # for i in range(n_iterations):
    #     #redivide_search_space(search_spaces, 5)
    #     divide_search_space(guesses, 10)

    # time_algo_1 = (time.time() - time_0)

    # time_0 = time.time()
    # for i in range(n_iterations):
    #     #redivide_search_space_2(search_spaces, 5)
    #     divide_search_space2(guesses, 10)

    # time_algo_2 = (time.time() - time_0)


    # print("Time taken by algo 1: ", time_algo_1)
    # print("Time taken by algo 2: ", time_algo_2)

    ## ======================================================================= 
    # deprecated
    ## =======================================================================

    # two function below have worse performance than the one being used
    
    # def divide_search_space2(guesses, num_sets):
    #     search_space_size = len(guesses)//num_sets
        
    #     search_spaces = [[None]*search_space_size for _ in range(num_sets)]

    #     start=0
    #     for search_space in search_spaces:
    #         j = 0
    #         for i in range(start, len(guesses), num_sets):
    #             if j >= len(search_space):
    #                 search_space.append(guesses[i])
    #             else:
    #                 search_space[j] = guesses[i]
    #             j+=1
    #         start+=1
    # return search_spaces


    # better performance, but more complicated and have to be adjusted for when num_sets > num_elements
    # def redivide_search_space(divided_search_space, num_sets):
    #     num_elements = sum([len(search_space) for search_space in divided_search_space])
    #     num_sets = min(num_sets, num_elements)
    #     new_search_space = [[] for _ in range(num_sets)]

    #     for i in range(len(divided_search_space)):
    #         start = 0
    #         for search_space in new_search_space:
    #             for j in range(start, len(divided_search_space[i]), num_sets):
    #                 search_space.append(divided_search_space[i][j])
    #             start+=1        
    #     return new_search_space



    # def create_divide_search_space(max_password_length, num_sets, ignore_case = True):
    #     if ignore_case:
    #         chars = string.ascii_lowercase # all lowercase characters
    #     else:
    #         chars = string.printable # all printable characters

    #     #list_of_guesses = {i:[] for i in range(1, max_password_length+1)}

    #     divided_search_space = [[] for i in range(num_sets)]
    #     for password_length in range(1, max_password_length+1):
    #         list_of_guesses = []
    #         for guess in itertools.product(chars, repeat=password_length):
    #             guess = "".join(guess)
    #             list_of_guesses.append(guess)

    #         elements_per_set = len(list_of_guesses) // num_sets        
    #         start = 0
    #         for i in range(num_sets):
    #             if i == num_sets-1:
    #                 divided_search_space[i].extend(list_of_guesses[start:])
    #             else:
    #                 last_element = start+elements_per_set
    #                 divided_search_space[i].extend(list_of_guesses[start:last_element])
    #                 start += elements_per_set        

    # return divided_search_space
