from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

def get_service(credential_path):
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credential_path, SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl = DISCOVERY_DOC,
        static_discovery=False,
    )
    return form_service

def get_create_request(form_title: str) -> dict:
    return {
        "info": {
            "title": form_title,
        }
    }

def get_set_quizz_request() -> dict:
    return {
        "requests": [
            {
                "updateSettings": {
                    "settings": {"quizSettings": {"isQuiz": True}},
                    "updateMask": "quizSettings.isQuiz",
                }
            }
        ]
    }

def get_insert_request(questions: list) -> dict:
    insert_body = {
        "requests": []
    }
    for index, question in enumerate(questions):
        insert_body["requests"].append({
            "createItem": {
                "item": {
                    "title": question["title"],
                    "questionItem": question["questionItem"]
                },
                "location": {"index": index}
            }
        })
    return insert_body

def get_question_object(question_title: str) -> dict:
    return {
        "title": question_title,
        "questionItem": {
            "question": {
                "required": True
            }
        }
    }
