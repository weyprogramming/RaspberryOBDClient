from genericpath import exists
from pathlib import Path
import json, requests, obd, datetime, time, pathlib, os
class obdRestApiRequests():

    BASE_URL = "https://obd-rest-service.herokuapp.com/api/v1/"
    BASE_DIR = Path(__file__).resolve().parent

    auth_token = {}
    current_measurement_id = None

    def set_auth_token(self, username, password):
        data = {"username":username, "password":password}
        response = requests.post(self.BASE_URL + "token/login/", data=data).json()
        self.auth_token = {'Authorization' : "Token " + response['auth_token']}

    def register_new_measurement(self):
        response = requests.post(self.BASE_URL + 'post/measurements/raspberry/', headers=self.auth_token)
        self.current_measurement_id = response.json()['id']
        if response.status_code == 201:
            return True
        else:
            return False

    def post_measurement_point(self, measurement_data):
        measurement_data['measurement'] = self.current_measurement_id
        response = requests.post(self.BASE_URL + 'post/measurementpoints/raspberry/', headers=self.auth_token, data=measurement_data)
        if response.status_code == 201:
            return True
        else:
            return False
    
    def check_json_directory(self):
        json_dir_path = self.BASE_DIR / "measurement_transfer"
        filenames = os.listdir(json_dir_path.__str__())
        for filename in filenames:
            current_file_path = json_dir_path / filename
            current_file_path_str = str(current_file_path)
            with open(current_file_path_str, "r") as fp:
                measurement_point = json.load(fp)
                self.post_measurement_point(measurement_data=measurement_point)
            os.remove(current_file_path_str)

    
class obdConnection(obd.Async):

    BASE_DIR = pathlib.Path(__file__).parent.resolve()

    measurement_point = {}
    current_measurement_id = None
    current_measurement_point_id = 0
    dir_exists = False
    rest_dir_exists = False

    def watch_commands_and_write_dict(self, commands, watch_time, callbacks):

        def write_to_dict(obd_response):
            if not obd_response.is_null():
                self.measurement_point[obd_response.command.name] = obd_response.value.magnitude
            if len(self.measurement_point) == len(commands):
                self.measurement_point["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                self.measurement_point['measurement'] = self.current_measurement_id
                for callback in callbacks:
                    callback(self.measurement_point)
                self.measurement_point = {}

        for command in commands:
            self.watch(command, callback=write_to_dict())
        self.start()
        time.sleep(watch_time)
        self.stop()
    
    def write_measurement_point_to_json(self, measurement_point):

        if not self.dir_exists:
            pathlib.Path(self.BASE_DIR + "measurements").mkdir(parents=True, exist_ok=False)
            pathlib.Path(self.BASE_DIR + "measurements/measurement_" + str(self.current_measurement_id)).mkdir(parents=True, exist_ok=False)
            self.dir_exists = True

        file_path = self.BASE_DIR + 'measurements/measurement_' + str(self.current_measurement_id) + "/measurement_point_" + str(self.current_measurement_point_id) + ".json"
        with open(file_path, 'w') as fp:
            json.dump(measurement_point, fp, sort_keys=True, indent=2)

        if not self.rest_dir.exists:
            pathlib.Path(self.BASE_DIR + "measurement_transfer").mkdir(parents=True, exist_ok=False)
            self.rest_dir_exists = True

        rest_file_path = self.BASE_DIR + "measurement_transfer/measurement_" + str(self.current_measurement_id) + "_measurement_point_" + str(self.current_measurement_point_id) + ".json"
        with open(rest_file_path, 'w') as fp:
            json.dump(measurement_point, fp, sort_keys=True, indent=2)




if __name__ == "__main__":
    client = obdRestApiRequests()
    client.set_auth_token("weyro", "Venire999")
    client.register_new_measurement()
    client.check_json_directory()

