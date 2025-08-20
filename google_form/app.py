from builder import FormBuilder

builder = FormBuilder(
    titile="flask 簡易伺服器",
    credential_path="./google_form/client_secrets.json",
    quizz_csv_path="./google_form/20250819.csv")

builder.build()