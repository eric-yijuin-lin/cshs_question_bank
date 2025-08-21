# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client 
import csv_parser, form_api

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
        self.form_service = form_api.get_service(self.credential_path)
        self.form_object = None

    def build(self):
        self.form_object = self.create_form(self.titile)
        print("Form created, form_object:\n", self.form_object)

        update_result = self.set_as_quizz()
        print("Quiz settings updated:", update_result)

        questions = csv_parser.get_questions_from_csv(self.quizz_csv_path)
        print(f"[debug] questions = csv_parser.get_questions_from_csv")
        print(questions)
        insert_result = self.insert_questions(questions)
        print("Questions inserted:", insert_result)


    def create_form(self, formt_title):
        form_service = form_api.get_service(self.credential_path)
        request_body = form_api.get_create_request(formt_title)
        create_result = form_service.forms().create(body=request_body).execute()
        return create_result

    def set_as_quizz(self):
        form_id = self.form_object["formId"]
        request_body = form_api.get_set_quizz_request()
        update_result = (
            self.form_service.forms()
            .batchUpdate(formId=form_id, body=request_body)
            .execute()
        )
        return update_result

    def insert_questions(self, questions):
        form_id = self.form_object["formId"]
        request_body = form_api.get_insert_request(questions)
        insert_result = (
            self.form_service.forms()
            .batchUpdate(formId=form_id, body=request_body)
            .execute()
        )
        return insert_result
