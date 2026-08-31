# AI SQL Data Analyst Agent

A hackathon-ready starter app that converts natural-language analytics questions into safe SQLite SQL, executes them, creates a chart, and asks Gemini to explain the result.

## Windows setup

```powershell
cd ai_sql_data_analyst
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
streamlit run app.py
```

Or copy `.env.example` to `.env` and load it in your shell/environment. For local development you can also add `load_dotenv()` to `src/agent.py`.

## Example questions

- What are the top 5 products by revenue?
- Which region generated the most revenue?
- Show monthly revenue.
- Which product category sold the most units?
- What is the average order value by region?

## Roadmap

1. CSV upload
2. PostgreSQL connector
3. SQL parser/validator
4. Conversation memory
5. Autonomous "Why did revenue change?" investigation
6. KPI dashboard
7. Query history and exports
8. Deployment
