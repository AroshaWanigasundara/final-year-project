from paths import *
from clients import *
from accuracy import *
from aggregation import *
from labelflip import *
from fileupload import *
from malremove import *
from imutils import paths
import pickle
import h5py
from tensorflow.python.keras.models import Model
import subprocess
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import gradient_descent_v2
from tensorflow.python.keras import backend as K
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
# label_flip('clients_1', 1, 7)
# label_flip('clients_2', 1, 7)
# label_flip('clients_3', 1, 7)
# label_flip('clients_4', 1, 7)
# label_flip('clients_5', 1, 7)

#validate the filpped data
label_count_of_clients('clients_1')
#label_count_of_clients('clients_2')
#label_count_of_clients('clients_3')
#label_count_of_clients('clients_4')
#label_count_of_clients('clients_5')

#defining the neural network
class SimpleMLP:
    @staticmethod
    def build(shape, classes):
        model = Sequential()
        model.add(Dense(50, input_shape=(shape,)))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model


#compiling the model

#for SGD optimizer
learning_rate = 0.1
#no.of communicatio rounds
iterations = 4
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
datarequest = True

# Function to run get_cid_of_data with a timeout
def run_get_cid_with_timeout():
    global cid
    cid = None
    def target():
        global cid
        cid = get_cid_of_data_ar1()
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout_duration)

    if thread.is_alive():
        print("Timeout occurred for get_cid_of_data. Running off_chain_request.")
        return True

    return False

for comm_round in range(iterations):

  #get the global model's weights (In each communication round, the current global model weights are retrieved with)
  global_weights = global_model.get_weights()

  scaled_local_weight_list = list()

  #randomize client data using keys to access each client batch data in the clients_batched dictionary
  client_names = list(clients_batched.keys())
  random.shuffle(client_names)

  #loop through each client and create new local model
  for client in client_names:
        smlp_local = SimpleMLP()
        local_model = smlp_local.build(784,10)

        local_model.compile( loss = loss,
                            optimizer= optimizer,
                            metrics= metrics)

        local_model.set_weights(global_weights)

        clients_train = clients_batched[client]
        for batchdata, labeldata in clients_train:
            train_x = np.asarray(batchdata)
            train_y = np.asarray(labeldata)
            local_model.fit(train_x, train_y, epochs=5, verbose=0)

        #scale the model weights and add to list
        scaling_factor = weight_scalling_factor(clients_batched, client)
        scaled_weights = scale_model_weights(local_model.get_weights(), scaling_factor)
        scaled_local_weight_list.append(scaled_weights)

        #Flattern weight metrix
        weight_vector = np.concatenate([matrix.flatten() for matrix in scaled_weights])
        weight_vector_list = weight_vector.tolist()

        # Convert the variable to a file
        file_path = "./web3-storage-quickstart/clients_model/{}.txt".format(client)
        file_content = str(weight_vector_list)  # Convert the variable to a string if necessary
        with open(file_path, "w") as file:
            file.write(file_content)
        
        #clear session to free memory after each communication round
        tf.keras.backend.clear_session()


  content_ID = model_upload('clients_model')
  off_chain_request(content_ID)
  while(run_get_cid_with_timeout()):
      off_chain_request(content_ID)

  #to get the average over all the local model, we simply take the sum of the scaled weights
  #average_weights = sum_scaled_weights(scaled_local_weight_list)
  average_weights = get_aggregation_data(cid)
  #average_weights = median_scaled_weights(scaled_local_weight_list)

  #update global model
  global_model.set_weights(average_weights)

  #test global model and print out metrics after each communications round
  for(X_test, y_test) in test_batched:
      global_acc, global_loss = test_model(X_test, y_test, global_model, comm_round, 'globalModel','')

  #get accuracy scores
  tp_div_support_dict = classes_acc_testss(X_test, y_test, global_model, comm_round, tp_div_support_dict)

file_path = "./web3-storage-quickstart/graph_plot/chaccuracy0.txt"
file_content = str(tp_div_support_dict)  # Convert the variable to a string if necessary
with open(file_path, "w") as file:
      file.write(file_content)

confusion_matrix_acc(global_model,X_test,y_test)

# plot predict scores for each label
predic_acc(tp_div_support_dict,iterations)