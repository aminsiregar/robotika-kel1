import cv2
import mediapipe as mp
from model import KeyPointClassifier
import landmark_utils as u


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

kpclf = KeyPointClassifier()

gestures = {
    0: "Naik",
    1: "Turun",
    2: "Kiri",
    3: "Kanan",
    4: "Maju",
    5: "Mundur",
    6: "Hovering",
    7: "ON",
    8: "OFF",
    9: "Tidak Ada Objek",
}

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # Default gesture_index to 9 (Tidak Ada Objek)
        gesture_index = 9

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_list = u.calc_landmark_list(image, hand_landmarks)
                keypoints = u.pre_process_landmark(landmark_list)
                gesture_index = kpclf(keypoints)

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        # Flip the image horizontally for a selfie-view display.
        final = cv2.flip(image, 1)
        cv2.putText(final, gestures[gesture_index],
                    (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, 255)
        cv2.imshow('MediaPipe Hands', final)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
