import random
from flask import Flask, request, jsonify, render_template
import json
from keywords.question_loader import QuestionLoader
from keywords.ai_judge import AiJudgeService

import os
print("Current working directory:", os.getcwd())
keyword_service = QuestionLoader("./ai_evaluation/keywords/question_bank.csv")
question_bank = keyword_service.get_grouped_keywords_as_dict()
# print("Question Bank:", question_bank)


def load_credentials(path: str = "./ai_evaluation/credentials.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

credentials = load_credentials()
api_key = credentials.get("openai_api_key")
model = credentials.get("model", "gpt-5.2")
ai_judge = AiJudgeService(api_key, model)

app = Flask(__name__)

def get_question():
    question = random.choice(question_bank)
    return question


@app.route("/")
def index():
    return jsonify({
        "message": "Flask API Server is running."
    })


@app.route("/keywords_match", methods=["GET", "POST"])
def keywords_match():
    if request.method == "GET":
        question = get_question()

        return render_template(
            "keywords_match.html",
            question=question
        )

    question_id = request.form.get("question_id")
    keywords = request.form.getlist("keywords")

    # 移除空白輸入
    keywords = [
        keyword.strip()
        for keyword in keywords
        if keyword.strip()
    ]

    if not question_id:
        return jsonify({
            "success": False,
            "message": "缺少 question_id"
        }), 400

    if not keywords:
        return jsonify({
            "success": False,
            "message": "請至少輸入一個關鍵字"
        }), 400
    
    id = int(question_id)
    question_data = next((q for q in question_bank if q["id"] == id), None)
    if not question_data:
        return jsonify({
            "success": False,
            "message": "無效的 question_id"
        }), 400
    
    ai_result = ai_judge.judge_keywords(
        topic=question_data["考點"],
        reference_keywords=question_data["關鍵字"],
        user_keywords=keywords
    )

    print("AI Judge Result:", ai_result)

    return jsonify(ai_result)
    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5052)