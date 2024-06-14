# main.py

This script is designed to automate the process of detecting and clicking on green bubbles in a game window. It uses computer vision techniques to identify the bubbles and bombs in the game, and then uses the PyAutoGUI library to automate mouse movements and clicks.

## Dependencies

- OpenCV
- NumPy
- PyAutoGUI
- Time
- Keyboard
- PyGetWindow
- Threading

## Hotkeys

- 'p': Toggles the running state of the script.
- 'q': Stops the running state of the script.
- 's': Starts the script if it's not already running.

## Usage

Run the script and use the hotkeys to control its execution. The script will automatically detect and click on green bubbles in the active game window. The script will stop if it has been running for more than 35 seconds, if the PyAutoGUI failsafe is triggered, or if the 'q' hotkey is pressed.

## Accuracy

Please note that the script does not guarantee 100% accuracy in detecting and clicking on the green bubbles.
