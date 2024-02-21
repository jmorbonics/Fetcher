from src import switch as switch_module
import time


if __name__ == '__main__':

    total_seconds = 60
    sample_hz = 2

    switch1 = switch_module.Switch({
        "pins": {
            "pin": 2
        }
    })

    switch2 = switch_module.Switch({
        "pins": {
            "pin": 3
        }
    })

    start_time = time.time()
    while time.time() - start_time < total_seconds:

        loop_start = time.time()
        print(1, switch1.is_pressed)
        print(2, switch2.is_pressed)

        time.sleep(max(0, 1/sample_hz - (time.time() - loop_start)))
