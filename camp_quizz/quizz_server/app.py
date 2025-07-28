from flask import Flask, render_template
from csv import DictReader
import random


def get_questions():
    questions = []
    with open('static/questions.csv', mode='r', encoding='utf-8') as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            question = {
                "planet": row["星球"],
                "stage": row["年段"],
                "question_type": row["類型"],
                "answer": row["答案"],
                "question": row["題目"],
                "source": row["出處"],
            }
            print(question)
            questions.append(question)
    return questions

def iniit_question_bank():
    global QUESTION_BANK
    QUESTION_BANK = get_questions()
    random.shuffle(QUESTION_BANK)

QUESTION_BANK = []
iniit_question_bank()

app = Flask(__name__)
@app.route("/")
def home():
    questions = get_questions()
    print(questions[0])
    return render_template("index.html")

@app.route("/question")
def question():
    question = QUESTION_BANK.pop(0)
    return render_template("question.html", question=question)