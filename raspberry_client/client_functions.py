import requests, json

BASE_URL = "http://127.0.0.1:8000/api/v1/"

def get_auth_token(username, password):
    response = requests.post(BASE_URL + "token/login/", data={'username': username, 'password': password}).json()
    return response['auth_token']

def post_measurement(auth_token):
    token_header = {'Authorization': "Token " + auth_token}
    response = requests.post('http://127.0.0.1:8000/api/v1/post/measurements/raspberry/', headers=token_header).json()
    return response

def post_measurementpoint(auth_token, measurement_id, measurement_point_json_filename):
    token_header = {'Authorization': "Token " + auth_token}

    with open(measurement_point_json_filename, 'r') as measurement_point_json:
        data = json.load(measurement_point_json)

    data['measurement'] = measurement_id
    print(data)

    response = requests.post('http://127.0.0.1:8000/api/v1/post/measurementpoints/raspberry/', headers=token_header, data=data)
    return response

def initalize_measurement(account_json_filename):
    with open(account_json_filename) as account_json:
        account_data = json.load(account_json)
    auth_token = get_auth_token(account_data['username'], account_data['password'])
    measurement_response = post_measurement(auth_token=auth_token)
    return auth_token, measurement_response['id']


if __name__ == "__main__":
    auth_token, measurement_id = initalize_measurement('account.json')
    post_measurementpoint(auth_token=auth_token, measurement_id=measurement_id, measurement_point_json_filename="test.json")
    post_measurementpoint(auth_token=auth_token, measurement_id=measurement_id, measurement_point_json_filename="test.json")
    post_measurementpoint(auth_token=auth_token, measurement_id=measurement_id, measurement_point_json_filename="test.json")


