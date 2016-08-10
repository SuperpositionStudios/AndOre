import child_server_config as config

def drint(text):
    if config.developing:
        print(text)

def flatten_2d_list(x):
    response = []
    for i in x:
        for k in i:
            response.append(k)
    return response