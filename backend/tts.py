import eventlet
eventlet.monkey_patch()


from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import queue
import sounddevice as sd
import sys
import json
from vosk import Model, KaldiRecognizer
from deepface import DeepFace
import cv2
from transformers import pipeline
import base64
import time

MODEL_PATH = "vosk-model-small-en-us-0.15"
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()


model1 = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
model2 = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
model3 = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            cv2.putText(frame, f'Emotion: {emotion}', (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print("Face error:", e)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.04) 

@app.route('/video')
def video():
    return Response(stream_with_context(generate_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/analyse-face", methods=["GET"])
def analyze_face():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return jsonify({"error": "Failed to capture image from camera"}), 500

        results = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=True,
            detector_backend='retinaface'
        )

        if not results:
            return jsonify({"error": "No face detected"}), 400

        emotion = results[0]['dominant_emotion']
        return jsonify({"emotion": emotion})

    except Exception as e:
        print("Emotion analysis error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/analyse-tone', methods=['POST'])
def analyze_tone():
    data = request.get_json()
    txt = data.get("text", "").strip()

    if not txt:
        return jsonify({"error": "No text provided"}), 400

    try:
        res1 = model1(txt)[0]
        res2 = model2(txt)[0]
        res3 = model3(f"tone: {txt}")[0]

        return jsonify({
            "emotion": res1,
            "sentiment": res2,
            "tone": res3
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def on_connect():
    print("Client connected")

@socketio.on('disconnect')
def on_disconnect():
    print("Client disconnected")

@socketio.on('audio_stream')
def handle_stream(data):
    try:
        base64_chunk = data["chunk"]
        audio_bytes = base64.b64decode(base64_chunk)
        print("Chunk size received:", len(audio_bytes))

        if rec.AcceptWaveform(audio_bytes):
            result = json.loads(rec.Result())
            transcript = result.get("text", "")
            print("Transcript:", transcript)

            if transcript:
                res1 = model1(transcript)[0]
                res2 = model2(transcript)[0]
                res3 = model3(f"tone: {transcript}")[0]

                emit("transcription", {"text": transcript})
                emit("tone_analysis", {
                    "emotion": res1,
                    "sentiment": res2,
                    "tone": res3
                })
        else:
            partial = json.loads(rec.PartialResult())
            emit("partial", {"text": partial.get("partial", "")})

    except Exception as e:
        print("Error:", e)
        emit("error", {"error": str(e)})

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    print("Running server with eventlet...")
    socketio.run(app, host="0.0.0.0", port=5000)
