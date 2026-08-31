
import os
import re
import pandas as pd
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


class DataAnalystAgent:

    def __init__(self, schema):
        key = os.getenv("GEMINI_API_KEY")

        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        self.client = genai.Client(api_key=key)
        self.schema = schema

    def ask(self, prompt):
        response = self.client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text.strip()

    def generate_sql(self, question):

        prompt = f"""
You are a senior analytics engineer.

Generate ONE safe SQLite SELECT query for the user's question.

Database Schema:
{self.schema}

Rules:
- Return ONLY SQL.
- Only SELECT or WITH queries.
- Never modify data.
- Do not invent tables or columns.
- Use orders.amount for revenue.
- Use SUM(orders.quantity) for units sold.
- Use SQLite syntax.
- Use explicit JOIN conditions.
- Do not use multiple SQL statements.

User Question:
{question}
"""

        text = self.ask(prompt)

        # Remove markdown SQL fences if Gemini returns them
        text = re.sub(
            r"^```(?:sql)?\s*|\s*```$",
            "",
            text,
            flags=re.IGNORECASE
        )

        return text.strip()

    def explain_results(self, question, sql, df):

        rows = df.head(50).to_dict(orient="records")

        prompt = f"""
You are a business data analyst.

Answer the user's question using ONLY the query result.

Question:
{question}

SQL:
{sql}

Query Result:
{rows}

Give:
1. A direct answer.
2. 1-3 useful business insights.

Do not invent facts that are not present in the result.
"""

        return self.ask(prompt)

