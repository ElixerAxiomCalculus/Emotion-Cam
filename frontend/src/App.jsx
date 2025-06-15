import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:5000", {
  transports: ["websocket"],
  upgrade: false,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});

function App() {
  const [transcript, setTranscript] = useState("");
  const [emotion, setEmotion] = useState("n/a");
  const [sentiment, setSentiment] = useState("n/a");
  const [tone, setTone] = useState("n/a");

  const [isStreaming, setIsStreaming] = useState(false);
  const [isCamOn, setIsCamOn] = useState(false);

  const contextRef = useRef(null);
  const processorRef = useRef(null);
  const inputRef = useRef(null);

  const floatTo16BitPCM = (input) => {
    const output = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      let s = Math.max(-1, Math.min(1, input[i]));
      output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return output;
  };

  const startStreaming = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    contextRef.current = new AudioContext({ sampleRate: 16000 });
    inputRef.current = contextRef.current.createMediaStreamSource(stream);
    processorRef.current = contextRef.current.createScriptProcessor(4096, 1, 1);

    inputRef.current.connect(processorRef.current);
    processorRef.current.connect(contextRef.current.destination);

    processorRef.current.onaudioprocess = (e) => {
      const floatSamples = e.inputBuffer.getChannelData(0);
      const int16Samples = floatTo16BitPCM(floatSamples);
      const byteBuffer = new Uint8Array(int16Samples.buffer);
      const base64 = btoa(String.fromCharCode(...byteBuffer));
      socket.emit("audio_stream", { chunk: base64 });
    };

    setIsStreaming(true);
    setIsCamOn(true);
  };

  const stopStreaming = () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current.onaudioprocess = null;
    }
    if (inputRef.current) {
      inputRef.current.disconnect();
    }
    if (contextRef.current) {
      contextRef.current.close();
    }

    setTranscript("");
    setEmotion("n/a");
    setSentiment("n/a");
    setTone("n/a");
    setIsStreaming(false);
    setIsCamOn(false);
  };

  useEffect(() => {
    socket.on("transcription", (data) => setTranscript(data.text));
    socket.on("tone_analysis", (data) => {
      setEmotion(data.emotion[0]?.label || "n/a");
      setSentiment(data.sentiment?.label || "n/a");
      setTone(data.tone[0]?.label || "n/a");
    });
    socket.on("partial", (data) => setTranscript("..." + data.text));
    socket.on("error", (err) => console.error("Server Error:", err));
  }, []);

return (
  <div
    style={{
      minHeight: "100vh",
      backgroundColor: "#121212",
      color: "#fff",
      fontFamily: "Segoe UI, sans-serif",
      padding: "2rem",
    }}
  >

    <div
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
      }}
    >
      
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <h1 style={{ fontSize: "2rem", fontWeight: "bold" }}>EmotionCam 🎙️</h1>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: isStreaming ? "#4CAF50" : "#f44336",
            }}
          ></div>
          <span style={{ fontSize: "14px" }}>
            {isStreaming ? "Mic + Camera Active" : "Idle"}
          </span>

          {!isStreaming ? (
            <button
              onClick={startStreaming}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#fff",
                color: "#000",
                border: "none",
                borderRadius: "6px",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              Start
            </button>
          ) : (
            <button
              onClick={stopStreaming}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#f44336",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              Stop
            </button>
          )}
        </div>
      </div>

      
      <div
        style={{
          display: "flex",
          gap: "2rem",
          flexWrap: "wrap",
          justifyContent: "space-between",
        }}
      >
        
        <div style={{ flex: 1, minWidth: "350px" }}>
          <h2 style={{ fontSize: "1.3rem", marginBottom: "0.5rem" }}>Facial Emotion Recognition</h2>
          {isCamOn && (
            <div
              style={{
                borderRadius: "12px",
                overflow: "hidden",
                border: "3px solid #4CAF50",
                marginBottom: "1rem",
                maxWidth: "100%",
              }}
            >
              <img
                src="http://localhost:5000/video"
                alt="Live Emotion Feed"
                style={{
                  width: "100%",
                  transform: "scaleX(-1)",
                }}
              />
            </div>
          )}
        </div>

        
        <div style={{ flex: 1, minWidth: "350px" }}>
          <div
            style={{
              background: "#1f1f1f",
              padding: "1rem 1.5rem",
              borderRadius: "10px",
              marginBottom: "1.5rem",
              lineHeight: "1.6",
            }}
          >
            <h3 style={{ marginBottom: "0.5rem" }}>Transcript:</h3>
            <p style={{ wordWrap: "break-word" }}>{transcript || "(Waiting for input...)"}</p>
          </div>

          <div
            style={{
              background: "#1f1f1f",
              padding: "1rem 1.5rem",
              borderRadius: "10px",
              lineHeight: "1.6",
            }}
          >
            <p><strong>Emotion:</strong> {emotion}</p>
            <p><strong>Sentiment:</strong> {sentiment}</p>
            <p><strong>Tone:</strong> {tone}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);


}

export default App;
