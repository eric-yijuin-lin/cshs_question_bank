import csv
import form_api

DEFAULT_QUESTION_POINT = 5
PRARGRAPH_QUESTION_POINT = 20

def get_question_title(csv_row: dict):
    title = csv_row.get("題目", "")
    if not title:
        raise ValueError("題目欄位不能為空")
    title = replace_new_lines(title, "\r")
    return title

def get_question_type(csv_row: dict):
    question_type = csv_row.get("題型", "")
    if not question_type:
        raise ValueError("題型欄位不能為空")
    return question_type

def get_multiple_choice_options(csv_row: dict):
    options = []
    split_lines = csv_row.get("選項", None).split("\n")
    for i in range(len(split_lines)):
        option = remove_new_lines(split_lines[i])
        option = remove_option_letter(option, i)
        if option:  # Ensure the option is not empty
            options.append({"value": option})
    return options

def remove_new_lines(text: str):
    return text.strip().replace("\r", "").replace("\n", "").replace("\u2028", "")

def replace_new_lines(text: str, replace_char):
    return text.strip().replace("\n", replace_char).replace("\u2028", replace_char)

def get_single_choice_object(api_object: dict, csv_row: dict):
    choice_options = get_multiple_choice_options(csv_row)
    choice_answers = get_correct_options(choice_options, csv_row)
    api_object["questionItem"]["question"]["choiceQuestion"] = {
        "type": "RADIO",
        "shuffle": True,
        "options": choice_options,
    }
    api_object["questionItem"]["question"]["grading"] = {
        "correctAnswers": {
            "answers": choice_answers
        },
        "pointValue": DEFAULT_QUESTION_POINT
    }
    return api_object

def get_text_answer_object(api_object: dict, paragraph: bool):
    point_per_question = PRARGRAPH_QUESTION_POINT if paragraph else DEFAULT_QUESTION_POINT
    api_object["questionItem"]["question"]["textQuestion"] = {
        "paragraph": paragraph
    }
    api_object["questionItem"]["question"]["grading"] = {
        "pointValue": point_per_question
    }
    return api_object

def remove_option_letter(option_text: str, option_index: int):
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

def get_correct_options(options: list, csv_row: dict):
    answers = []
    answer_letter = csv_row.get("答案", "")
    index = ord(answer_letter) - ord('A')
    if index < 0 or index >= len(options):
        raise ValueError(f"Answer letter {answer_letter} is out of range for options.")
    answers.append({"value": options[index]["value"]})
    return answers

def get_questions_from_csv(quizz_csv_path):
    questions = []
    with open(quizz_csv_path, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            title = get_question_title(row)
            api_object = form_api.get_question_object(title)
            question_type = get_question_type(row)

            if question_type == "單選":
                api_object = get_single_choice_object(api_object, row)
            elif question_type == "填充" or question_type == "簡答":
                api_object = get_text_answer_object(api_object, paragraph=False)
            elif question_type == "實做":
                api_object = get_text_answer_object(api_object, paragraph=True)
            else:
                raise ValueError(f"Unsupported question type: {question_type}")

            questions.append(api_object)
        return questions
