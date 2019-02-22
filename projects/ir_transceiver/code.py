import adafruit_irremote
import board
import pulseio
import time
from adafruit_circuitplayground.express import cpx

# Create a 'pulseio' output, to send infrared signals on the IR transmitter
pwm = pulseio.PWMOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)
pulseout = pulseio.PulseOut(pwm)

# Create an encoder that will take numbers and turn them into NEC IR pulses
encoder = adafruit_irremote.GenericTransmit(
    header=[9500, 4500], one=[550, 550], zero=[550, 1700], trail=0
)

# Create a 'pulseio' input, to listen to infrared signals on the IR receiver
pulsein = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)
# Create a decoder that will take pulses and turn them into numbers
decoder = adafruit_irremote.GenericDecode()

SELECT_COLOUR = 0x0000FF
ACTIVE_COLOUR = 0xFFFFFF
BLANK_COLOUR = 0x000000
FAIL_COLOUR = 0xFF0000
CONFIRM_COLOUR = 0x00FF00
WAITING_COLOUR = 0xFFFF00

IR_ERRORS = (
    adafruit_irremote.IRDecodeException,
    adafruit_irremote.IRNECRepeatException,
)


def flash_neopixel(index, colour, length=0.5):
    """
    Turn a neopixel a specific colour for a given amount
    of time. It will return to its original colour after.
    """

    original_colour = cpx.pixels[index]

    cpx.pixels[index] = colour
    time.sleep(length)
    cpx.pixels[index] = original_colour


def flash_led(amount, length=0.1):
    """Flash the red LED a given amount of times."""

    for _ in range(amount):
        time.sleep(length)
        cpx.red_led = True
        time.sleep(length)
        cpx.red_led = False


def selection_colour(index):
    """
    Find out what colour a specific neopixel should be
    when we're in selection mode. Neopixels that "store"
    an IR signal will be highlighted for the user.
    """

    if saved_signals[index] is None:
        return BLANK_COLOUR
    else:
        return SELECT_COLOUR


cpx.pixels.brightness = 0.01
saved_signals = [None] * 10

previous_index = 0
current_index = 0
button_held = False
selecting = None

while True:

    # when the switch is flicked, toggle between the modes
    if selecting != cpx.switch:
        selecting = cpx.switch
        cpx.pixels.fill(BLANK_COLOUR)

        if selecting:
            for index in range(10):
                cpx.pixels[index] = selection_colour(index)

            cpx.pixels[current_index] = ACTIVE_COLOUR
            flash_led(3)

        else:
            cpx.pixels[current_index] = ACTIVE_COLOUR
            flash_led(2)

    # we only want to process new button presses, not button holds.
    if selecting and not button_held:

        previous_index = current_index

        # the buttons are used to move the "cursor" and select a neopixel.
        if cpx.button_a:
            button_held = True
            current_index = (current_index + 1) % 10

        elif cpx.button_b:
            button_held = True
            current_index = (current_index - 1) % 10

        else:
            continue

        cpx.pixels[previous_index] = selection_colour(previous_index)
        cpx.pixels[current_index] = ACTIVE_COLOUR

    # this will run when we're in signal receive/transmit mode.
    elif not selecting and not button_held:

        # transmit the signal under the current neopixel (if it exists).
        if cpx.button_a:
            button_held = True
            signal = saved_signals[current_index]

            if signal is None:
                flash_neopixel(current_index, FAIL_COLOUR)
                continue

            cpx.red_led = True
            encoder.transmit(pulseout, signal)
            cpx.red_led = False

        # or wait for an incoming signal and save it under this neopixel.
        elif cpx.button_b:
            button_held = True
            cpx.pixels[current_index] = WAITING_COLOUR
            pulses = decoder.read_pulses(pulsein)  # wait for a signal.

            try:
                # attempt to convert received pulses into numbers.
                received_code = decoder.decode_bits(pulses, debug=False)
            except IR_ERRORS:
                flash_neopixel(current_index, FAIL_COLOUR)
            else:
                saved_signals[current_index] = received_code
                flash_neopixel(current_index, CONFIRM_COLOUR)

            cpx.pixels[current_index] = ACTIVE_COLOUR

    if button_held and not (cpx.button_a or cpx.button_b):
        button_held = False
