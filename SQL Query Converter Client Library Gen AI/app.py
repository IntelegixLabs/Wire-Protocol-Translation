from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import openai
import os
import sqlglot
from dotenv import load_dotenv, find_dotenv

app = FastAPI()

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
load_dotenv(find_dotenv(), override=True)


class QueryConversionRequest(BaseModel):
    source_dialect: str  # mysql, oracle, mssql
    target_dialect: str  # mysql, oracle, mssql
    query: str


@app.post("/convert-query-sqlglot")
def convert_query(request: QueryConversionRequest):
    try:
        # Convert SQL query
        converted_query = sqlglot.transpile(
            request.query,
            read=request.source_dialect,
            write=request.target_dialect
        )
        return {"converted_query": converted_query[0] if converted_query else ""}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/convert-query-gen-ai")
def convert_query(request: QueryConversionRequest):
    try:
        prompt = (
            f"Convert the following SQL query from {request.source_dialect} to {request.target_dialect} syntax:\n"
            f"{request.query}\n"
            f"Provide only the converted query without explanation."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",  # You can use gpt-4 or gpt-3.5-turbo
            messages=[{"role": "system", "content": "You are an SQL expert."},
                      {"role": "user", "content": prompt}]
        )

        converted_query = response.choices[0].message.content.strip()

        return {"converted_query": converted_query}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    uvicorn.run("app:app", host=os.getenv("AI_HOST", "localhost"),
                port=int(os.getenv("AI_PORT", 5000)),
                reload=False)
