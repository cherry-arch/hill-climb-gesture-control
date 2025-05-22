import cv2
import mediapipe as mp
import pyautogui

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Function to count fingers
def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for i in range(1, 5):
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[tips[i]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

# Webcam
cap = cv2.VideoCapture(0)
click_flag = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for lm in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, lm, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(lm)
            total = fingers.count(1)

            # GAS (All fingers open)
            if total == 5:
                pyautogui.keyDown('right')
                pyautogui.keyUp('left')

            # BRAKE (Fist)
            elif total == 0:
                pyautogui.keyDown('left')
                pyautogui.keyUp('right')

            # Index only = cursor move
            elif fingers[1] == 1 and total == 1:
                x = int(lm.landmark[8].x * screen_width)
                y = int(lm.landmark[8].y * screen_height)
                pyautogui.moveTo(x, y)

            # Click: Index + Thumb
            elif fingers[0] == 1 and fingers[1] == 1 and total == 2:
                if not click_flag:
                    pyautogui.click()
                    click_flag = True
            else:
                click_flag = False

    cv2.imshow("Hill Climb Controller", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
