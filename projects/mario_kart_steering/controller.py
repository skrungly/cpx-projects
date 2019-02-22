import pyautogui
import math
import serial
import time

pyautogui.PAUSE = 0  # minimise input latency

# these values are in degrees from 0 to 90.
STEER_THRESHOLD = 80
TURN_THRESHOLD = 55
DRIFT_THRESHOLD = 0  # disable drifting. it barely works.

MAX_STEER_HOLD = 0.5

# this is what we send to the CPX to request the next
# reading. it doesn't usually matter what this says, but
# it has to be somewhat unique so that we can find it again.
DATA_TO_WRITE = b":ok_hand:\r\n"

CPX_SERIAL_PORT = "/dev/ttyACM0"  # TODO: make this platform-independent.
CPX_BAUD_RATE = 115200

cpx_conn = serial.Serial(
    CPX_SERIAL_PORT,
    CPX_BAUD_RATE,
    timeout=1.0
)

# configure your emulator controls here. these are defaults for DeSmuME.
STEER_LEFT = "left"
STEER_RIGHT = "right"
DRIFT = "w"
ACCELERATE = "x"
REVERSE = "z"
USE_ITEM = "s"


def read_cpx_input():
    """
    Read the accelerometer and button data from the CPX. It should
    provide this data printed in the form "x y z a b", where "x y z"
    refers to each axis of the accelerometer reading (floats), and
    "a b" refers to whether buttons a and b are pressed (bools).
    """

    # let the CPX know that we want the next reading, and skip
    # any unnecessary output since the previous reading.
    cpx_conn.write(DATA_TO_WRITE)
    cpx_conn.read_until(DATA_TO_WRITE)

    output_string = cpx_conn.read_until(b"\r\n")
    x, y, z, a, b = output_string.decode().strip().split()

    return (float(x), float(y), float(z), a == "True", b == "True")


def press_key_if(target_key, condition):
    """
    A basic helper function which uses PyAutoGUI to press a key if
    a condition is met, or releases it if the condition isn't met.
    """

    if condition:
        pyautogui.keyDown(target_key)
    else:
        pyautogui.keyUp(target_key)


def main_loop():

    steer_timer = time.time()
    previous_angle = 0

    while True:
        x, y, z, button_a, button_b = read_cpx_input()

        if x != 0:
            tilt_angle = math.degrees(math.atan(y / x))
        else:
            tilt_angle = 90.0

        if y < 0:
            tilt_angle = -tilt_angle

        # if the tilt is increasing, we will continue steering.
        if abs(tilt_angle) < abs(previous_angle):
            steer_timer = time.time()

        do_steer = False  # will decide if we actually steer.

        if abs(tilt_angle) < STEER_THRESHOLD:

            # if the tilt is shallow, just steer for a small amount of time.
            # this is better than continuously steering for small tilts,
            # because otherwise the kart becomes very difficult to control.
            if abs(tilt_angle) > TURN_THRESHOLD:
                steer_amount = STEER_THRESHOLD - abs(tilt_angle)
                max_steer_amount = STEER_THRESHOLD - TURN_THRESHOLD

                # this will be a fraction of MAX_STEER_HOLD based on the tilt
                hold_length = MAX_STEER_HOLD * steer_amount / max_steer_amount

                # if we haven't steered enough for this tilt, keep steering.
                if time.time() - steer_timer < hold_length:
                    do_steer = True
                else:
                    do_steer = False

            # if it's not a shallow tilt, just continue steering.
            else:
                do_steer = True

        # if we're not steering, keep the timer up-to-date.
        else:
            steer_timer = time.time()

        if do_steer:
            press_key_if(STEER_RIGHT, tilt_angle < 0)
            press_key_if(STEER_LEFT, tilt_angle > 0)
            press_key_if(DRIFT, abs(tilt_angle) < DRIFT_THRESHOLD)
        else:
            pyautogui.keyUp(STEER_RIGHT)
            pyautogui.keyUp(STEER_LEFT)
            pyautogui.keyUp(DRIFT)

        press_key_if(ACCELERATE, button_b and not button_a)
        press_key_if(REVERSE, button_a and not button_b)
        press_key_if(USE_ITEM, button_a and button_b)

        previous_angle = tilt_angle


try:
    main_loop()
finally:
    cpx_conn.close()
