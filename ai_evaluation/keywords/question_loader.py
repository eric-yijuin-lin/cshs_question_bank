import pandas as pd
from pathlib import Path
import os


class QuestionLoader:
    REQUIRED_COLUMNS = ["年度", "科目", "考點", "關鍵字"]

    def __init__(self, csv_path: str = None):
        self.csv_path = Path(csv_path)
        self.df = None
        self.grouped_df = None

    def load_csv(self) -> pd.DataFrame:
        """
        讀取 CSV，並檢查欄位。
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"找不到 CSV 檔案：{self.csv_path}")

        df = pd.read_csv(self.csv_path, encoding="utf-8-sig")

        missing_columns = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(f"CSV 缺少必要欄位：{missing_columns}")

        self.df = df
        return self.df

    def clean_data(self) -> pd.DataFrame:
        """
        清理資料：
        1. 移除考點或關鍵字為空的 row
        2. 去除前後空白
        3. 移除重複資料
        """
        if self.df is None:
            self.load_csv()

        df = self.df.copy()

        df = df.dropna(subset=["考點", "關鍵字"])

        for col in self.REQUIRED_COLUMNS:
            df[col] = df[col].astype(str).str.strip()

        df = df.drop_duplicates(
            subset=["年度", "科目", "考點", "關鍵字"]
        )

        self.df = df
        return self.df

    def group_keywords_by_topic(self) -> pd.DataFrame:
        """
        依照「考點」分組，
        將同一個考點底下的關鍵字用 # 串起來，
        並在 group 完成後給每一筆資料一個 id。
        """
        if self.df is None:
            self.clean_data()

        grouped_df = (
            self.df
            .groupby("考點", as_index=False)["關鍵字"]
            .apply(lambda keywords: "#".join(keywords))
        )

        # 加上 ID，從 1 開始
        grouped_df.insert(0, "id", range(1, len(grouped_df) + 1))

        self.grouped_df = grouped_df
        return self.grouped_df

    def get_grouped_keywords_as_dict(self) -> list[dict]:
        """
        回傳 list[dict]，方便 Flask jsonify。
        """
        if self.grouped_df is None:
            self.group_keywords_by_topic()

        return self.grouped_df.to_dict(orient="records")

