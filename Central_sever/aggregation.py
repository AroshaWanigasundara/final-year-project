import tensorflow as tf
import numpy as np
from clients import clients_batched
import requests
import ast

def weight_scalling_factor(clients_train_data, client_name):

    #first calculate the total training data points across clients
    global_count = 0
    for client in clients_batched:
        clientsdata = clients_batched[client]
        for batch, labels in clientsdata:
          for num in labels:
            global_count += 1

    # get the total number of data points held by a client
    local_count = 0
    clientsdata = clients_batched[client_name]
    for batch, labels in clientsdata:
      for num in labels:
        local_count += 1

    return local_count/global_count


#function for scaling a models weights
def scale_model_weights(weight, scalar):

    weight_final = []
    steps = len(weight)
    for i in range(steps):
        weight_final.append(scalar * weight[i])
    return weight_final


#Return the sum of the listed scaled weights. The is equivalent to scaled avg of the weights
def sum_scaled_weights(scaled_weight_list):

    avg_grad = list()
    #get the average grad accross all client gradients
    for grad_list_tuple in zip(*scaled_weight_list):
        layer_mean = tf.math.reduce_sum(grad_list_tuple, axis=0)
        avg_grad.append(layer_mean)

    return avg_grad


#Return the sum of the listed scaled weights. The is equivalent to scaled avg of the weights
def sum_scaled_weights(scaled_weight_listss, number_of_clients):

    avg_grad = list()
    new_scaled_weight_list = [(elem[1]) for elem in scaled_weight_listss]
    #get the average grad accross all client gradients
    for grad_list_tuple in zip(*new_scaled_weight_list):
        layer_mean = tf.math.reduce_sum(grad_list_tuple, axis=0)*number_of_clients/len(grad_list_tuple)
        avg_grad.append(layer_mean)

    return avg_grad


def median_scaled_weights(scaled_weight_list):

    median_grad = list()
    #get the average grad accross all client gradients
    for grad_list_tuple in zip(*scaled_weight_list):
        layer_median = np.median(grad_list_tuple, axis=0)*len(grad_list_tuple)
        median_grad.append(layer_median)

    return median_grad

def get_aggregation_data(cid):
   
   # Assuming you have the shapes of the original arrays
    shapes = [
        (784, 50),
        (50,),
        (50, 10),
        (10,),
        # Repeat the pattern for the remaining shapes
    ]

    MAX_RETRIES = 5

    for i in range(MAX_RETRIES):

        try:

            # transaction code
            file_url = f'https://{cid}.ipfs.w3s.link/iteration.txt'
            response = requests.get(file_url, stream=True)
            content = response.content.decode('utf-8')
            weight_list = ast.literal_eval(content)

            # Transaction succeeded, exit loop
            break

        except Exception as e:

            print(f"Error: {e}")  
            print(f"Retrying, attempt {i+1}/{MAX_RETRIES}")


    # Create an empty list to store the reshaped arrays
    reshaped_list = []

    # Start index for slicing the flattened vector
    start_index = 0

    # Iterate over the shapes and reshape the vector
    for shape in shapes:
        # Calculate the size of the current array
        size = np.prod(shape)

        # Extract the corresponding slice from the vector
        slice_vector = weight_list[start_index:start_index + size]

        # Reshape the slice to the original shape
        reshaped_array = np.reshape(slice_vector, shape, order='C')

        # Add the reshaped array to the list
        reshaped_list.append(reshaped_array)

        # Update the start index for the next slice
        start_index += size

    return reshaped_list