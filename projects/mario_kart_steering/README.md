# Mario Kart DS Steering Wheel
This project lets you control Mario Kart DS running in an emulator on your computer. This should be plug-and-play with the default DeSmuME controls, but you should modify the constants in `controller.py` to match your own if they're different. Very little of the code here is actually running on CPX, but it's still quite nifty.
A video of this project in use can be found here: https://youtu.be/CLirlkh-bsk. The game can be controlled as follows:

- Button A -> Accelerate
- Button B -> Reverse
- Button A and B -> Use item
- Tilting -> Steering

### Requirements
- pySerial (https://pypi.org/project/pyserial/)
- PyAutoGUI (https://pypi.org/project/pyautogui/)
- A Linux-based operating system (for now...)