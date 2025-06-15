from flask import Flask,request,jsonify
from flask_cors import CORS
from transformers import pipeline
model=pipeline("text-classification",model="j-hartmann/emotion-english-distilroberta-base",return_all_scores=True)
model2=pipeline("sentiment-analysis",model="cardiffnlp/twitter-roberta-base-sentiment")
model3 = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
app=Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "backend"

@app.route('/analyse',methods=['POST'])
def analysis():
    data=request.get_json()
    txt=data.get("text","")

    if not txt.strip():
        return jsonify({"error":"no data found"}),400
    
    res1=model(txt)[0]
    res2=model2(txt)[0]
    res3=model3(f"tone: {txt}")[0]

    return jsonify(
        {
            "emotion":res1,
            "sentiment":res2,
            "tone":res3
        }
    )

if __name__=='__main__':
    app.run(debug=True)