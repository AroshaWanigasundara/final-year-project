import os
import json
import numpy as np
import requests
import ast
import subprocess
import h5py
import io
from web3 import Web3
import tensorflow as tf
from flask import Flask, request, jsonify
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import gradient_descent_v2

app = Flask(__name__)

# Define custom parameters to be used by the adapter.
custom_params = {
    'cid': ['cid', 'contentIdentifier'],
    'endpoint': False
}

class SimpleMLP:
    @staticmethod
    def build(shape, classes):
        model = Sequential()
        model.add(Dense(50, input_shape=(shape,)))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model
    
#for SGD optimizer
learning_rate = 0.1
iterations = 10
epsilon = 1.0  # Initial privacy budget
alpha = learning_rate / iterations  # Learning rate for Foolsgold
max_noise = 1.0  # Maximum noise magnitude

#no.of communicatio rounds

loss = 'categorical_crossentropy'
metrics= ['accuracy']
optimizer = gradient_descent_v2.SGD(learning_rate=alpha, momentum=0.9)

smlp_global = SimpleMLP()
global_model = smlp_global.build(784,10)

def reshape(arrays):
    # Assuming you have the shapes of the original arrays
    shapes = [
        (784, 50),
        (50,),
        #(200, 200),
        #(200, 1),
        (50, 10),
        (10,),
        # Repeat the pattern for the remaining shapes
    ]

    # Create an empty list to store the reshaped arrays
    reshaped_list = []

    # Start index for slicing the flattened vector
    start_index = 0

    # Iterate over the shapes and reshape the vector
    for shape in shapes:
        # Calculate the size of the current array
        size = np.prod(shape)

        # Extract the corresponding slice from the vector
        slice_vector = arrays[start_index:start_index + size]

        # Reshape the slice to the original shape
        reshaped_array = np.reshape(slice_vector, shape, order='C')

        # Add the reshaped array to the list
        reshaped_list.append(reshaped_array)

        # Update the start index for the next slice
        start_index += size

    return reshaped_list

def calculate_median(arrays):

    median_grad = list()
    #get the average grad accross all client gradients
    for grad_list_tuple in zip(*arrays):
        layer_median = np.median(grad_list_tuple, axis=0)
        #layer_median = np.median(grad_list_tuple, axis=0)*len(grad_list_tuple)
        median_grad.append(layer_median)

    return median_grad

#Return the sum of the listed scaled weights. The is equivalent to scaled avg of the weights
def calculate_mean(arrays):

    avg_grad = list()
    #get the average grad accross all client gradients
    for grad_list_tuple in zip(*arrays):
        layer_mean = tf.math.reduce_sum(grad_list_tuple, axis=0)/(len(grad_list_tuple))
        avg_grad.append(layer_mean)

    return avg_grad

def model_upload(fileName):
    js_file_path = './put-files.js'

    command = ['node', js_file_path, json.dumps(fileName)]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode().strip()
        #print("JavaScript function executed successfully.")
        print("Result:", result)
    except subprocess.CalledProcessError as e:
        print("Error executing JavaScript function:", e.output.decode())

    return result

def get_aggregation_data(cid):

    MAX_RETRIES = 5
    loaded_model_weights = []

    for i in range(MAX_RETRIES):

        try:

            # transaction code
            file_url = f'https://{cid}.ipfs.w3s.link/global_model_weights.h5'
            #file_url = f'https://{cid}.ipfs.w3s.link/global_model/global_model_weights.h5'
            response = requests.get(file_url, stream=True)
            content = response.content
            data = io.BytesIO(content)
            with h5py.File(data, 'r') as hf:
                for i in range(len(hf.keys())):
                    loaded_model_weights.append(hf[f'layer_{i}'][:])

            # Transaction succeeded, exit loop
            break

        except Exception as e:

            print(f"Error: {e}")  
            print(f"Retrying, attempt {i+1}/{MAX_RETRIES}")

    return loaded_model_weights

def get_cid_of_glmodel():
    w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'))

    contract_address = "0x89Cf7FC0bE35066A80cC03E8Cf3DF9878cB4A9ad"
    with open('off_chain_contract_abi.json', 'r') as f:
        contract_abi = json.load(f)

    contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)

    result = contract_instance.functions.aggregationCid().call()

    return result


@app.route('/', methods=['POST'])
def create_request():
    weight_list = []
    data = request.json
    job_run_id = data.get('id')

    try:
        cid = get_cid_of_glmodel()
        print('Successfully obtained the cid of the global model')
        #cid = "bafybeidvqav3jnkwdadt7mfr234yw6cnjma7jk7w2crpyx2ieicdrzz6sy"
        global_model_weight = get_aggregation_data(cid)
        print('Successfully obtained the global model')
        global_model.set_weights(global_model_weight)
        print('Successfully set the global model')
        for i in range(1, 10):
            local_model_weights = []
            file_url = f"https://{data['data']['cid']}.ipfs.w3s.link/clients_model/clients_{i}.h5"
            response = requests.get(file_url, stream=True)
            content = response.content
            model = io.BytesIO(content)
            with h5py.File(model, 'r') as hf:
                for i in range(len(hf.keys())):
                    local_model_weights.append(hf[f'layer_{i}'][:])
            # response = requests.get(file_url, stream=True)
            # content = response.content.decode('utf-8')
            # clweight_list = ast.literal_eval(content)
            # #clweight_list = convert_ndarray_to_list(clweight_list)
            # reshape_weight_list = reshape(clweight_list)
            weight_list.append(local_model_weights)
            #reshape_weigt_list = reshape(clweight_list)
            #weight_list.append(reshape_weigt_list)

        #results_array = calculate_median(weight_list)
        #print('Successfully created the median array')

        results_array = calculate_mean(weight_list)
        print('Successfully created the mean array')

        global_model.set_weights(results_array)
        print('Successfully aggregate the global model')

        #Save the model weights using h5py
        model_weights = global_model.get_weights()
        with h5py.File('./global_model_weights.h5', 'w') as hf:
            for i, layer_weights in enumerate(model_weights):
                hf.create_dataset(f'layer_{i}', data=layer_weights)

        content_ID = model_upload('global_model_weights.h5')

        # message = {'result': cid}
        message = content_ID

        return jsonify({
            'id': job_run_id,
            'data': message
        }), 200
    except Exception as error:
        print('Error:', error)
        return jsonify({
            'id': job_run_id,
            'error': str(error)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('EA_PORT', 8080)))
