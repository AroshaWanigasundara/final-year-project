from clients import clients_batched

def label_flip(clientsname, flip_index, fliped_index):
    clientsdata = clients_batched[clientsname]
    data_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    counts = [0] * 10
    for batch, labels in clientsdata:
        y_train_flip = list(labels)
        for i, y in enumerate(labels):
          if y[flip_index] == 1:
            data_array[fliped_index] = 1
            y_train_flip[i] = data_array
          labels[i] = y_train_flip[i]