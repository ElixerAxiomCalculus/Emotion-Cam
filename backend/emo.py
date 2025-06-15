import cv2
from deepface import DeepFace

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # Let DeepFace handle both face detection + emotion analysis
        results = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=True,
            detector_backend='retinaface'
        )

        for result in results:
            x, y, w, h = result['region']['x'], result['region']['y'], result['region']['w'], result['region']['h']

            # Skip small/invalid detections
            if w < 100 or h < 100:
                continue

            emotion = result['dominant_emotion']

            # Draw face bounding box and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    except Exception as e:
        print("DeepFace error:", e)

    cv2.imshow("Real-time Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()