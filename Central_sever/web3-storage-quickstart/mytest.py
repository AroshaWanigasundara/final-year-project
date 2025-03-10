import sys
import requests
import numpy as np
import tensorflow as tf
import ast

#cid = 'bafybeidp6tp3oeizgyoqwrzdxq5hhttumk7aeppkvsnwxrqrqinitifeju'
#gateway_url = '.ipfs.w3s.link'

def get_median(cid):
    # Fetch and store all arrays
    weight_list = list()
    median_weight_list = list()

    weight_list = [
      [1, 5, -19, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77],
      [2, 16, -10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78],
      [3, -7, -11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 71, 75, 79]]

    

    #weight_list = [ast.literal_eval(item) for item in weight_list]

    for grad_list_tuple in zip(*weight_list):
        layer_median = np.median(grad_list_tuple, axis=0) * len(grad_list_tuple)
        median_weight_list.append(layer_median)

    file_path = "./iteration.txt"
    file_content = str(median_weight_list)
    with open(file_path, "w") as file:
        file.write(file_content)
        print('successful')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cid_parameter = sys.argv[1]
        get_median(cid_parameter)
    else:
        print("Please provide the 'cid' parameter.")
        