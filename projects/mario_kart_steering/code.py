from adafruit_circuitplayground.express import cpx

cpx.pixels.brightness = 0.05
cpx.pixels.fill(0x3333ff)

# a lot of the tilt calculations used to be in this file, but
# it's best to leave that heavier work for the computer.
while True:
    # wait for an input to avoid constantly spamming stuff.
    input()

    if cpx.switch:
        x, y, z = cpx.acceleration
        print(x, y, z, cpx.button_a, cpx.button_b)
    else:
        print(0.0, 0.0, 0.0, False, False)
