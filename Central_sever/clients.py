import numpy as np
import random
import cv2
import os
from matplotlib import pyplot as plt

#batch the training data for each clients
clients_batched = dict()

def load(paths, verbose=0):
  data = list()
  labels = list()

  for (i, imgpath)in enumerate(paths):
    im_gray = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
    image = np.array(im_gray).flatten()

    #label of the image is extracted from the image path (selecting the second to last element of the resulting list, which is assumed to be the label of the image)
    label = imgpath.split(os.path.sep)[-2]
    data.append(image/255)
    labels.append(label)

    if verbose >0 and i>0 and (i+1) %verbose ==0 :
      print("[INFO] processed {}/{}".format(i+1,len(paths)))
  return data,labels


def create_clients(image_list, label_list, num_clients=10,initial='clients'):

  #create a list of client names
  client_names =['{}_{}'.format(initial, i+1) for i in range(num_clients)]

  #randomize data
  data = list(zip(image_list, label_list))
  random.shuffle(data)

  #sharing data with particular each client
  size = len(data)//num_clients
  shards = [data[i:i + size] for i in range(0, size*num_clients, size)]

  #code asserts that the number of clients is equal to the number of shards,
  assert(len(shards) == len(client_names))


  #returns  [key]= client name and [value] = corresponding shard of data for that client.
  return {client_names[i] : shards[i] for i in range(len(client_names))}


def batch_data(data_shard, batch_size =32):

    # Shuffle the data shard
    random.shuffle(data_shard)
    # Group data and labels into batches
    batches = []
    for i in range(0, len(data_shard), batch_size):
        batch_data = []
        batch_label = []
        for data, label in data_shard[i:i+batch_size]:
            batch_data.append(list(data))
            batch_label.append(list(label))
        batches.append((batch_data, batch_label))
    return batches


#print clients
def label_count_of_clients(clientsname):

    clientsdata = clients_batched[clientsname]
    counts = [0] * 10
    for batch, labels in clientsdata:
        # Use batch and labels here
        labelclass = [np.argmax(element) for element in labels]
        for num in labelclass:
            counts[num] += 1
    plt.bar(range(10), counts)
    plt.xlabel('Numbers')
    plt.ylabel('Counts')
    plt.title(clientsname)
    plt.show()


