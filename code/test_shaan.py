from src import vehicle as vehicle_module
import time

if __name__ == '__main__':

    vehicle = vehicle_module.Vehicle(
        {
            "motors": {
                "left": {
                    "pins": {
                        "speed": 13,
                        "control1": 5,
                        "control2": 6
                    }
                },
                "right": {
                    "pins": {
                        "speed": 12,
                        "control1": 7,
                        "control2": 8
                    }
                }
            }
        }
    )

    # print('Forward')
    # vehicle.drive_forward()
    # time.sleep(5)
    # vehicle.stop()

    print("Turn Right")
    vehicle.pivot_right()


    # stop = False
    # for distance_sensor in vehicle.distance_sensors:
    #     if distance_sensor.distance < 0.25:
    #         self.vehicle.stop()
    #         stop = True

    # if not stop:
    #     self.vehicle.drive_forward(10)