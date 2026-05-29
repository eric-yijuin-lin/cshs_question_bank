import json
import os
from openai import OpenAI


class AiJudgeService:
    def __init__(self, api_key: str, model: str = "gpt-5.2"):
        if not api_key:
            raise ValueError("缺少 OpenAI API Key")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def judge_keywords(
        self,
        topic: str,
        reference_keywords: str,
        user_keywords: list[str]
    ) -> dict:
        """
        使用 ChatGPT 判斷使用者輸入的關鍵字是否符合參考答案。

        reference_keywords 範例：
        傳道#授業#解惑#師道#聞道有先後

        user_keywords 範例：
        ["傳道", "授業", "解惑"]
        """

        prompt = {
            "task": "請判斷學生輸入的關鍵字是否符合參考答案。",
            "考點": topic,
            "參考答案": reference_keywords,
            "學生答案": user_keywords,
            "評分規則": [
                "參考答案中的關鍵字以 # 分隔。",
                "學生答案可以與參考答案不完全相同，但語意相近可以算對。",
                "請根據參考答案逐一列出關鍵字。",
                "以參考答案為準，判斷學生答案是否有命中。",
                "只需要判斷對或錯，少寫也算錯。",
                "請只回傳 JSON，不要加入 markdown。"
            ],
            "回傳格式參考": {
                "keywords": [
                    {
                        "reference": "",
                        "user_keyword": "",
                        "matched": False
                    }
                ]
            }
        }

        response = self.client.responses.create(
            model=self.model,
            input=json.dumps(prompt, ensure_ascii=False)
        )

        text = response.output_text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "score": 0,
                "is_correct": False,
                "matched_keywords": [],
                "missed_reference_keywords": [],
                "details": [],
                "feedback": "AI 回傳格式不是合法 JSON，請檢查 prompt 或模型輸出。",
                "raw_response": text
            }