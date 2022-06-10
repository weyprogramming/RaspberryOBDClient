import obd, datetime, json

class RaspberryOBD(obd.Async):

    commands_watched_amount = 0,
    measurement_point = {}

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
        if len(self.measurement_point) == self.commands_watched_amount:
            self.measurement_point["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            self.save_measurement_point_to_json()
    


    def start_watching_supported_commands(self, supported_commands):
        for command in supported_commands:
            self.watch(command, callback=self.register_new_obd_value())
        self.start()    


    


if __name__ == "__main__":
    print(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))


