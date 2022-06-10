from multiprocessing import connection
import obd, datetime, json, time
import requests

class RaspberryOBD(obd.Async):

    measurement_number = 1
    measurement_point_number = 1
    commands_watched_amount = 0,
    measurement_point = {}
    auth_token = ""

    BASE_URL = "http://127.0.0.1:8000/api/v1/"

    def set_auth_token(self, account_json_filename):
        with open(account_json_filename) as account_json:
            account_data = json.load(account_json)
        response = requests.post(self.BASE_URL + "token/login/", data=account_data).json()
        self.auth_token = response['auth_token']

    def register_measurement_on_api(self):
        token_header = {'Authorization': "Token " + self.auth_token}
        response = requests.post(self.BASE_URL + 'post/measurements/raspberry/', headers=token_header).json()
        self.measurement_id = response['id']
        
    def post_measurementpoint_to_api(self, measurement_point_data):
        token_header = {'Authorization': "Token " + self.auth_token}
        measurement_point_data['measurement'] = self.measurement_id

        response = requests.post(self.BASE_URL + 'post/measurementpoints/raspberry/', headers=token_header, data=measurement_point_data)
        return response

    def get_supported_mode_01_commands(self):
        supported_01_mode_commands = []

        for available_command in obd.commands[1]:
            if available_command in self.supported_commands:
                supported_01_mode_commands.append(available_command)
        self.commands_watched_amount = len(supported_01_mode_commands)
        return supported_01_mode_commands

    def save_measurement_point_to_json(self):
        pass

    def register_new_obd_value(self, response):
        if not response.is_null():
            self.measurement_point[response.command.name] = response.value.magnitude
        else:
            self.measurement_point[response.commands.name] = ""

        if len(self.measurement_point) == self.commands_watched_amount:
            self.measurement_point["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            print(self.measurement_point)
            self.measurement_point = {}


    def start_watching_and_save_supported_commands(self, supported_commands):

        def register_new_obd_value(response):
            print(response.value)
            if not response.is_null():
                self.measurement_point[response.command.name] = response.value.magnitude

            if len(self.measurement_point) == len(supported_commands):
                self.measurement_point["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                filename = "C:/Users/weyro/OneDrive/Programming/Bachelorarbeit/REST_API/raspberry_obd/raspberry_client/measurements/" + "measurement_" + str(self.measurement_number) + "_measurement_point_" + str(self.measurement_point_number)
                with open(filename, 'w') as fp:
                    json.dump(self.measurement_point, fp, sort_keys=True, indent=4)
                    print("json saved")
                self.measurement_point_number += 1
                self.measurement_point = {}
        
        for command in supported_commands:
            self.watch(command, callback=register_new_obd_value)
        self.start()
        time.sleep(60) 
        self.stop()

    def start_watching_and_send_supported_commands(self, supported_commands):

        def register_new_obd_value(response):
            print(response.value)
            if not response.is_null():
                self.measurement_point[response.command.name] = response.value.magnitude
            else:
                self.measurement_point[response.commands.name] = ""

            print(len(supported_commands))
            print(len(self.measurement_point))

            if len(self.measurement_point) == len(supported_commands):
                self.measurement_point["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                print(self.measurement_point)
                self.post_measurementpoint_to_api(self.measurement_point)
                self.measurement_point = {}
        
        for command in supported_commands:
            self.watch(command, callback=register_new_obd_value)
        self.start()
        time.sleep(60) 
        self.stop()


if __name__ == "__main__":
    connection = RaspberryOBD()
    commands = [obd.commands.RPM, obd.commands.SPEED, obd.commands.THROTTLE_POS, obd.commands.ENGINE_LOAD]
    connection.set_auth_token("account.json")
    connection.register_measurement_on_api()
    print("connected")
    connection.start_watching_and_send_supported_commands(commands)


