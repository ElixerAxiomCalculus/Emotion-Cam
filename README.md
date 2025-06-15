#  EmotionCam

**EmotionCam** is a real-time web-based application that seamlessly integrates facial emotion recognition, tone analysis, and sentiment detection using live **camera** and **microphone** input. It's designed as a complete multimodal AI experience powered by state-of-the-art models for expressive human-computer interaction.

---

##  Features

*  **Facial Emotion Recognition**
  Detects emotions like *happy, sad, angry, surprised,* and more using the webcam with DeepFace.

*  **Voice-Based Sentiment & Tone Analysis**
  Converts speech to text using Vosk and performs tone classification via transformer models.

*  **Multimodal Emotion Analysis Dashboard**
  Displays real-time feedback with emotion bars, tone tags, confidence scores, and dynamic UI.

*  **Lightweight & Fast**
  Uses efficient models for smooth real-time performance even on low-end machines.

*  **Privacy-First**
  Runs entirely on the client and local backend – no data is sent to external servers.

---

##  Tech Stack

###  Backend

* Python (Flask + Flask-SocketIO)
* Vosk Speech Recognition
* DeepFace for facial emotion analysis
* Hugging Face Transformers (`distilroberta`, `twitter-roberta`, etc.)

###  Frontend

* React.js + Vite for blazing fast UI
* WebRTC APIs for camera/mic access
* Socket.IO for real-time streaming
* Animated emotion/tone visualization

---

##  Project Structure

```
EmotionCam/
├── backend/
│   ├── tts.py               # Speech input processing & tone/emotion classification
│   ├── tone.py              # NLP-based sentiment analysis
│   ├── emo.py               # Facial emotion recognition (DeepFace)
│   ├── requirements.txt     # Backend dependencies
│   └── vosk-model/          # Vosk STT model directory
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx, App.css
│   │   ├── main.jsx
│   │   └── assets/
│   ├── public/
│   └── package.json, vite.config.js
│
└── README.md
```

---

##  Setup Instructions

###  Backend (Python)

1. **Set up virtual environment**

   ```bash
   cd backend
   python -m venv env
   env\Scripts\activate   # or source env/bin/activate on macOS/Linux
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Flask server**

   ```bash
   python tts.py
   ```

###  Frontend (React)

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Run frontend**

   ```bash
   npm run dev
   ```

> Make sure both backend and frontend are running concurrently.

---


##  Models Used

*  `vosk-model-small-en-us-0.15` – offline speech-to-text
*  `j-hartmann/emotion-english-distilroberta-base` – emotion classification
*  `cardiffnlp/twitter-roberta-base-sentiment` – sentiment analysis
*  DeepFace – real-time facial emotion recognition

---

##  Future Ideas

*  Personal Emotion Report Generator
*  Emotion trends & daily mood tracking
*  Multi-language support
*  Integration with games or VR for expressive gameplay

---

##  Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change or add.


---

##  Author

**Sayak Mondal**
🔗 [GitHub](https://github.com/ElixerAxiomCalculus) | 🌐 [www.aisayak.in](http://www.aisayak.in)

> Built with ❤️ for real-time emotional insight and AI-driven human interaction.
