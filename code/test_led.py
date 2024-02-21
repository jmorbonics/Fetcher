from src import led as led_module
import time


total_seconds = 3
cycle_time = 1

led1 = led_module.LED({
    "pins": {
        "pin": 20
    }
})

led2 = led_module.LED({
    "pins": {
        "pin": 21
    }
})

if __name__ == '__main__':

    start_time = time.time()
    while time.time() - start_time < total_seconds:
        print('ON!')
        led1.on()
        led2.on()
        time.sleep(cycle_time)
        print('OFF')
        led1.off()
        led2.off()
        time.sleep(cycle_time)
