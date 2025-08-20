# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client 
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import csv
from datetime import datetime
import os

class FormApiHelper:
    SCOPES = "https://www.googleapis.com/auth/forms.body"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    @staticmethod
    def get_service(self, credential_path):
        print(f"[debug] current working directory: {os.getcwd()}")
        print(f"[debug] credential_path: {credential_path}")
        store = file.Storage("token.json")
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credential_path, FormApiHelper.SCOPES)
            creds = tools.run_flow(flow, store)

        form_service = discovery.build(
            "forms",
            "v1",
            http=creds.authorize(Http()),
            discoveryServiceUrl = FormApiHelper.DISCOVERY_DOC,
            static_discovery=False,
        )
        return form_service

class FormBuilder:
    def __init__(self,
                 titile: str,
                 credential_path: str,
                 quizz_csv_path: str,
                 point_per_question: int = 5):
        self.titile = titile
        self.credential_path = credential_path
        self.quizz_csv_path = quizz_csv_path
        self.point_per_question = point_per_question
        self.form_service = FormApiHelper.get_service(self, self.credential_path)
        self.form_object = None

    def build(self):
        self.form_object = self.create_form(self.titile)
        print("Form created, form_object:\n", self.form_object)

        update_result = self.update_quiz_settings()
        print("Quiz settings updated:", update_result)

        questions = self.get_questions_from_csv()
        insert_result = self.insert_questions(questions)
        print("Questions inserted:", insert_result)


    def create_form(self, formt_title):
        form_service = FormApiHelper.get_service(self, self.credential_path)
        NEW_FORM = {
            "info": {
                "title": formt_title,
            }
        }
        create_result = form_service.forms().create(body=NEW_FORM).execute()
        return create_result

    def update_quiz_settings(self):
        form_id = self.form_object["formId"]
        update_body = {
            "requests": [
                {
                    "updateSettings": {
                        "settings": {"quizSettings": {"isQuiz": True}},
                        "updateMask": "quizSettings.isQuiz",
                    }
                }
            ]
        }
        update_result = (
            self.form_service.forms()
            .batchUpdate(formId=form_id, body=update_body)
            .execute()
        )
        return update_result

    def insert_questions(self, questions):
        form_id = self.form_object["formId"]
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

        insert_result = (
            self.form_service.forms()
            .batchUpdate(formId=form_id, body=insert_body)
            .execute()
        )
        return insert_result

    def get_multiple_choice_options(self, option_str):
        options = []
        split_lines = option_str.split("\n")
        for i in range(len(split_lines)):
            option = self.remove_new_lines(split_lines[i])
            option = self.remove_option_letter(option, i)
            if option:  # Ensure the option is not empty
                options.append({"value": option})
        return options
    
    def remove_new_lines(self, text: str):
        return text.strip().replace("\r", "").replace("\n", "").replace("\u2028", "")

    def replace_new_lines(self, text: str, replace_char):
        return text.strip().replace("\n", replace_char).replace("\u2028", replace_char)
    
    def remove_option_letter(self, option_text: str, option_index: int):
        if option_index == 0:
            return option_text.replace("(A) ", "")
        elif option_index == 1:
            return option_text.replace("(B) ", "")
        elif option_index == 2:
            return option_text.replace("(C) ", "")
        elif option_index == 3:
            return option_text.replace("(D) ", "")
        elif option_index == 4:
            return option_text.replace("(E) ", "")
        else:
            raise ValueError("Unsupported option index")
    

    def get_correct_option(self, options: list, answer_letter: str):
        if not options:
            raise ValueError("Options list cannot be empty.")
        answers = []
        index = ord(answer_letter) - ord('A')
        if index < 0 or index >= len(options):
            raise ValueError(f"Answer letter {answer_letter} is out of range for options.")
        answers.append({"value": options[index]["value"]})
        return answers

    def get_questions_from_csv(self):
        questions = []
        print(f"[debug] current working directory: {os.getcwd()}")
        print(f"[debug] self.quizz_csv_path: {self.quizz_csv_path}")
        with open(self.quizz_csv_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                title = self.replace_new_lines(row.get("題目"), "\r")
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
                    choice_options = self.get_multiple_choice_options(row.get("選項", ""))
                    choice_answers = self.get_correct_option(choice_options, row.get("答案", ""))
                    question["questionItem"]["question"]["choiceQuestion"] = {
                        "type": "RADIO",
                        "shuffle": True,
                        "options": choice_options,
                    }
                    question["questionItem"]["question"]["grading"] = {
                        "correctAnswers": {
                            "answers": choice_answers
                        },
                        "pointValue": self.point_per_question
                    }
                    # print(question["questionItem"]["question"])
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
