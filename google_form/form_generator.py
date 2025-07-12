# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client 
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import csv
import json

POINT_PER_QUESTION = 5

def get_multiple_choice_options(options_str):
    options = []
    for option in options_str.split("\n"):
        option = option.strip().replace("\r", "").replace("\n", "").replace("\u2028", "")
        if option:  # Ensure the option is not empty
            options.append({"value": option})
    return options

def get_correct_option(options_str, answer_letter):
    options = []
    for option in options_str.split("\n"):
        option = option.strip().replace("\r", "").replace("\n", "").replace("\u2028", "")
        if option:  # Ensure the option is not empty
            options.append({"value": option})
    answers = []
    if answer_letter == "A":
        answers.append({"value": options[0]["value"]})
    elif answer_letter == "B":
        answers.append({"value": options[1]["value"]})
    elif answer_letter == "C":
        answers.append({"value": options[2]["value"]})
    elif answer_letter == "D":
        answers.append({"value": options[3]["value"]})
    return answers

def get_questions_from_csv(file_path):
    questions = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            title = row.get("題目").strip().replace("\n", "\r").replace("\u2028", "\r")
            question_type = row.get("題型")
            question = {
                "title": title,
                "questionItem": {
                    "question": {
                        "required": True
                    }
                }
            }
    
            if question_type == "單選":
                question["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "RADIO",
                    "shuffle": True,
                    "options": get_multiple_choice_options(row.get("選項", "")),
                }
                question["questionItem"]["question"]["grading"] = {
                    "correctAnswers": {
                        "answers": get_correct_option(row.get("選項", ""), row.get("答案", ""))
                    },
                    "pointValue": POINT_PER_QUESTION
                }
                print(question["questionItem"]["question"])
            elif question_type == "填充" or question_type == "簡答":
                question["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": False
                }
            elif question_type == "實做":
                question["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": True
                }
                print(question["questionItem"]["question"]["textQuestion"])
            else:
                raise ValueError(f"Unsupported question type: {question_type}")

            questions.append(question)

    return questions


SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
  creds = tools.run_flow(flow, store)

form_service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
)

NEW_FORM = {
    "info": {
        "title": "Quickstart form",
    }
}
result = form_service.forms().create(body=NEW_FORM).execute()

update = {
    "requests": [
        {
            "updateSettings": {
                "settings": {"quizSettings": {"isQuiz": True}},
                "updateMask": "quizSettings.isQuiz",
            }
        }
    ]
}
question_setting = (
    form_service.forms()
    .batchUpdate(formId=result["formId"], body=update)
    .execute()
)
getresult = form_service.forms().get(formId=result["formId"]).execute()
print(getresult)
        
questions = get_questions_from_csv("./程式設計題庫 - 工作表1.csv")


NEW_QUESTION = {
    "requests": []
}

for index, question in enumerate(questions):
    # if index > 0:
    #     break
    NEW_QUESTION["requests"].append({
        "createItem": {
            "item": {
                "title": question["title"],
                "questionItem": question["questionItem"]
            },
            "location": {"index": index}
        }
    })


# Adds the question to the form
question_setting = (
    form_service.forms()
    .batchUpdate(formId=result["formId"], body=NEW_QUESTION)
    .execute()
)

# Prints the result to show the question has been added
get_result = form_service.forms().get(formId=result["formId"]).execute()
print(get_result)