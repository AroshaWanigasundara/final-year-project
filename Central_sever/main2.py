from paths import *
from clients import *
from accuracy import *
from labelflip import *
from fileupload import *
from imutils import paths
import requests
import io
import h5py
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import gradient_descent_v2
import threading
import time

image_paths = list(paths.list_images(img_path))
random.shuffle(image_paths)
num_images = int(len(image_paths) * 0.1)
image_list, label_list = load(image_paths[:num_images],verbose=10000)

lb = LabelBinarizer()
label_list = lb.fit_transform(label_list)

#split data fro trainig and testing
X_train, X_test, y_train, y_test = train_test_split(image_list, label_list, test_size=0.1, random_state=42)

client = create_clients(X_train, y_train, num_clients=10, initial='clients')

#batch the training data for each clients
#clients_batched = dict()

for(client_names, data) in client.items():
      clients_batched[client_names] = batch_data(data)

#batch the test data
test_batched = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(len(y_test))

#label count of client
label_count_of_clients('clients_1')
#label_count_of_clients('clients_2')
#label_count_of_clients('clients_3')
#label_count_of_clients('clients_4')
#label_count_of_clients('clients_5')

#filp 1 into 7
label_flip('clients_1', 1, 7)
label_flip('clients_2', 1, 7)
label_flip('clients_3', 1, 7)
label_flip('clients_4', 1, 7)
# label_flip('clients_5', 1, 7)

#validate the filpped data
label_count_of_clients('clients_1')
# label_count_of_clients('clients_2')
# label_count_of_clients('clients_3')
# label_count_of_clients('clients_4')
#label_count_of_clients('clients_5')

#defining the neural network
class SimpleMLP:
    @staticmethod
    def build(shape, classes):
        model = Sequential()
        model.add(Dense(50, input_shape=(shape,)))
        model.add(Activation("relu"))
        #model.add(Dense(200))
        #model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model


#compiling the model

#for SGD optimizer
learning_rate = 0.1
#no.of communicatio rounds
iterations = 10
epsilon = 1.0  # Initial privacy budget
alpha = learning_rate / iterations  # Learning rate for Foolsgold
max_noise = 1.0  # Maximum noise magnitude

loss = 'categorical_crossentropy'
metrics= ['accuracy']
optimizer = gradient_descent_v2.SGD(learning_rate=alpha, momentum=0.9)


tp_div_support_dict = np.zeros((iterations, 10))

#Initialize the global model
smlp_global = SimpleMLP()
global_model = smlp_global.build(784,10)
timeout_duration = 180
comm_round = 0

def get_aggregation_data(cid):

    MAX_RETRIES = 5
    loaded_model_weights = []

    for i in range(MAX_RETRIES):

        try:

            # transaction code
            #file_url = f'https://{cid}.ipfs.w3s.link/global_model/global_model_weights.h5'
            file_url = f'https://{cid}.ipfs.w3s.link/global_model_weights.h5'
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

# Function to run get_cid_of_data with a timeout
def run_get_cid_with_timeout(comm_round):
    global cid
    cid = None
    def target():
        global cid
        cid = get_cid_of_data(comm_round)
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout_duration)

    if thread.is_alive():
        print("Timeout occurred for get_cid_of_data. Running off_chain_request.")
        off_chain_request(content_ID)
        return True

    return False


while comm_round < iterations:
  
  if run_get_cid_with_timeout(comm_round):
        continue

  print('Successfully got cid of global model')

  #cid = "bafybeicsq5ja55vqkujo6wg34rfmfjr652stycapjqw5z2mbludxdac6be"  
  global_model_weight = get_aggregation_data(cid)
  print('Successfully got global model')

  global_model.set_weights(global_model_weight)
  print('Successfully set global model')

  #test global model and print out metrics after each communications round
  for(X_test, y_test) in test_batched:
      global_acc, global_loss = test_model(X_test, y_test, global_model, comm_round, 'globalModel','')

  #get accuracy scores
  tp_div_support_dict = classes_acc_testss(X_test, y_test, global_model, comm_round, tp_div_support_dict)

  scaled_local_weight_list = []

  #randomize client data using keys to access each client batch data in the clients_batched dictionary
  client_names = list(clients_batched.keys())
  random.shuffle(client_names)

  index_ID = 1  
  #loop through each client and create new local model
  for client in client_names:
        smlp_local = SimpleMLP()
        local_model = smlp_local.build(784,10)

        local_model.compile( loss = loss,
                            optimizer= optimizer,
                            metrics= metrics)

        local_model.set_weights(global_model_weight)

        clients_train = clients_batched[client]
        for batchdata, labeldata in clients_train:
            train_x = np.asarray(batchdata)
            train_y = np.asarray(labeldata)
            local_model.fit(train_x, train_y, epochs=5, verbose=0)

        #Save the model weights using h5py
        file_path = "./web3-storage-quickstart/clients_model_full/{}.h5".format(client)
        with h5py.File(file_path, 'w') as hf:
            for i, layer_weights in enumerate(local_model.get_weights()):
                hf.create_dataset(f'layer_{i}', data=layer_weights)
        
        #clear session to free memory after each communication round
        tf.keras.backend.clear_session()


  content_ID = model_upload('clients_model_full')
  off_chain_request_full(content_ID)
  comm_round += 1

file_path = "./web3-storage-quickstart/graph_plot/fullblockaccuracy0.txt"
file_content = str(tp_div_support_dict)  # Convert the variable to a string if necessary
with open(file_path, "w") as file:
      file.write(file_content)

confusion_matrix_acc(global_model,X_test,y_test)

# plot predict scores for each label
predic_acc(tp_div_support_dict,iterations)