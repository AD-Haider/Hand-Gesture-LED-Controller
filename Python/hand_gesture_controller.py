"""
Hand Gesture LED Controller (2 LEDs) — MediaPipe v0.10+ compatible
====================================================================
Index finger  → LED 1 (Arduino Pin 2)
Middle finger → LED 2 (Arduino Pin 3)

Requirements:
    pip install opencv-python mediapipe pyserial

On first run, this script auto-downloads the hand landmarker model (~8 MB).
Update COM_PORT below to match your Arduino (check Arduino IDE → Tools → Port).
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import serial
import time
import urllib.request
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
COM_PORT   = "COM3"    # Change to your port, e.g. "COM5" or "/dev/ttyUSB0"
BAUD_RATE  = 9600
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# Landmark indices: Index tip=8, pip=6 | Middle tip=12, pip=10
FINGER_TIPS = [8, 12]
FINGER_PIP  = [6, 10]
LED_LABELS  = ["Index", "Middle"]
LED_COLORS  = [(0, 165, 255), (0, 255, 0)]

# ─────────────────────────────────────────────
# Download model if not present
# ─────────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("[*] Downloading hand landmarker model (~8 MB)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("[✓] Model downloaded.")

# ─────────────────────────────────────────────
# Setup MediaPipe HandLandmarker (new v0.10 API)
# ─────────────────────────────────────────────
BaseOptions           = mp_python.BaseOptions
HandLandmarker        = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
RunningMode           = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detector = HandLandmarker.create_from_options(options)

# ─────────────────────────────────────────────
# Setup Serial
# ─────────────────────────────────────────────
ser = None
for attempt in range(5):
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"[✓] Connected to Arduino on {COM_PORT}")
        break
    except serial.SerialException as e:
        print(f"[!] Attempt {attempt+1}: {e}")
        time.sleep(1)

if ser is None:
    print("[✗] Could not open serial port. Running in preview-only mode.")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_fingers = []


def get_finger_states(landmarks):
    """Returns [index_up, middle_up] as booleans."""
    return [landmarks[tip].y < landmarks[pip].y
            for tip, pip in zip(FINGER_TIPS, FINGER_PIP)]


def send_to_arduino(fingers):
    if ser and ser.is_open:
        cmd = "".join("1" if f else "0" for f in fingers) + "\n"
        ser.write(cmd.encode())


def draw_hand(frame, landmarks, w, h):
    """Draw hand skeleton from landmark list."""
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    connections = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),
        (5,9),(9,13),(13,17)
    ]
    for a, b in connections:
        cv2.line(frame, pts[a], pts[b], (80, 200, 80), 2)
    for i, pt in enumerate(pts):
        color = (0, 255, 255) if i in FINGER_TIPS else (255, 255, 255)
        cv2.circle(frame, pt, 5, color, -1)
        cv2.circle(frame, pt, 5, (0, 0, 0), 1)


def draw_ui(frame, fingers, h, w):
    for i, (up, label, color) in enumerate(zip(fingers, LED_LABELS, LED_COLORS)):
        x = 60 + i * 220
        y_rect = h - 80
        circle_color = color if up else (50, 50, 50)
        cv2.circle(frame, (x + 40, y_rect - 30), 22, circle_color, -1)
        cv2.circle(frame, (x + 40, y_rect - 30), 22, (255, 255, 255), 2)
        cv2.putText(frame, label, (x, y_rect + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)
        cv2.putText(frame, "ON" if up else "OFF", (x + 20, y_rect + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color if up else (100, 100, 100), 2)

    cv2.putText(frame, f"Fingers up: {sum(fingers)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 200), 2)
    status = f"Arduino: {COM_PORT}" if (ser and ser.is_open) else "Arduino: Not connected"
    cv2.putText(frame, status, (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    cv2.putText(frame, "Press Q to quit", (w - 210, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)


# ─────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────
print("[*] Show your hand — Index and Middle fingers control the 2 LEDs.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)

    fingers = [False, False]

    if result.hand_landmarks:
        landmarks = result.hand_landmarks[0]
        draw_hand(frame, landmarks, w, h)
        fingers = get_finger_states(landmarks)

        if fingers != prev_fingers:
            send_to_arduino(fingers)
            prev_fingers = fingers[:]
            print(f"[→] Index={'ON' if fingers[0] else 'OFF'}  "
                  f"Middle={'ON' if fingers[1] else 'OFF'}")

    draw_ui(frame, fingers, h, w)
    cv2.imshow("Hand Gesture LED Control (2 LEDs)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
if ser and ser.is_open:
    ser.write(b"00\n")
    ser.close()
cap.release()
cv2.destroyAllWindows()
detector.close()
print("[✓] Done.")