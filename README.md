# Hand Gesture LED Controller

A real-time computer vision project that uses **MediaPipe Hand Landmarker**, **OpenCV**, **Python**, and **Arduino** to control two physical LEDs using hand gestures.

The webcam detects the user's **index** and **middle** fingers. Their states are sent from Python to Arduino over serial communication, allowing the LEDs to turn ON/OFF in real time.

## Features

- Real-time hand landmark detection with MediaPipe
- Index finger controls LED 1
- Middle finger controls LED 2
- OpenCV camera interface and visual feedback
- Serial communication between Python and Arduino
- Automatic download of the MediaPipe hand model on first run
- Preview-only mode if Arduino is unavailable

## Gesture Mapping

| Finger | LED | Arduino Pin |
|---|---|---:|
| Index | LED 1 | 2 |
| Middle | LED 2 | 3 |

Serial commands are two characters followed by a newline:

| Command | LED 1 | LED 2 |
|---|---|---|
| `00` | OFF | OFF |
| `01` | OFF | ON |
| `10` | ON | OFF |
| `11` | ON | ON |

## System Architecture

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Landmarker
   ↓
Index / Middle Finger Detection
   ↓
Serial Command (00 / 01 / 10 / 11)
   ↓
Arduino
   ├── Pin 2 → LED 1
   └── Pin 3 → LED 2
```

## Hardware Requirements

- Arduino Uno or compatible board
- 2 × LEDs
- 2 × 220Ω resistors
- Breadboard
- Jumper wires
- USB cable
- Computer with webcam

## Circuit Connections

```text
Arduino Pin 2 → 220Ω resistor → LED 1 anode (+)
LED 1 cathode (-) → GND

Arduino Pin 3 → 220Ω resistor → LED 2 anode (+)
LED 2 cathode (-) → GND
```

> Use a resistor in series with each LED.

## Project Structure

```text
Hand-Gesture-LED-Controller/
├── Arduino/
│   └── hand_gesture_led.ino
├── Python/
│   ├── hand_gesture_controller.py
│   └── requirements.txt
├── images/
├── .gitignore
├── LICENSE
└── README.md
```

The `hand_landmarker.task` model is intentionally not stored in the repository. The Python script downloads it automatically on first run.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/Hand-Gesture-LED-Controller.git
cd Hand-Gesture-LED-Controller
```

### 2. Install Python dependencies

```bash
pip install -r Python/requirements.txt
```

## Arduino Setup

1. Open `Arduino/hand_gesture_led.ino` in Arduino IDE.
2. Connect the Arduino board.
3. Select the correct board under **Tools → Board**.
4. Select the correct port under **Tools → Port**.
5. Upload the sketch.
6. Close the Arduino Serial Monitor before starting the Python program.

## Python Configuration

Open:

```text
Python/hand_gesture_controller.py
```

Set the Arduino serial port near the top of the file:

```python
COM_PORT = "COM3"
BAUD_RATE = 9600
```

Examples:

```python
# Windows
COM_PORT = "COM5"

# Linux
COM_PORT = "/dev/ttyUSB0"

# macOS
COM_PORT = "/dev/cu.usbmodemXXXX"
```

## Run the Controller

From the project root:

```bash
python Python/hand_gesture_controller.py
```

On the first run, the script downloads the MediaPipe hand landmark model automatically.

Press **Q** to quit. On exit, the program sends `00` so both LEDs are turned OFF.

## How Finger Detection Works

MediaPipe provides 21 hand landmarks. This project uses:

- Index fingertip: landmark `8`
- Index PIP joint: landmark `6`
- Middle fingertip: landmark `12`
- Middle PIP joint: landmark `10`

A finger is considered raised when its fingertip is above its PIP joint in the image coordinate system:

```python
landmarks[tip].y < landmarks[pip].y
```

## Troubleshooting

### Arduino does not connect

- Verify the USB cable.
- Check **Tools → Port** in Arduino IDE.
- Update `COM_PORT` in the Python script.
- Close Arduino Serial Monitor.

### Camera does not open

The default camera is index `0`:

```python
cv2.VideoCapture(0)
```

If you have multiple cameras, try `1` or another available index.

### LEDs do not respond

Check LED polarity, resistors, GND, pin numbers, and that the Arduino sketch was uploaded successfully.

### MediaPipe model problem

Delete the downloaded `hand_landmarker.task` file and run the Python script again.

## Future Improvements

- Support all five fingers
- Control 5 LEDs using individual fingers
- Add RGB LED control
- Add relay-based appliance control
- Add Bluetooth/Wi-Fi communication
- Support multiple hands
- Add custom gesture commands

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Muhammad Abbas
