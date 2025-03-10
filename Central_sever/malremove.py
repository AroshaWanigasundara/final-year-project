def mal_remove(malicious_client, scaled_local_weight_lists):

    scaled_local_weight_list = [(client, data) for client, data in scaled_local_weight_lists if client not in malicious_client]

    # if not scaled_local_weight_list:
    #   return scaled_local_weight_lists

    return scaled_local_weight_list