import psycopg
import openai
from flask import Flask, request, jsonify

# Initialize OpenAI API
openai.api_key = "your_openai_api_key"

# Initialize Flask app
app = Flask(__name__)

# PostgreSQL connection details
PG_DETAILS = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "dbname": "test_db",
}


# Connect to PostgreSQL
def connect_postgres():
    conn = psycopg.connect(**PG_DETAILS)
    return conn


# Function to translate queries using OpenAI API
def translate_query(original_query):
    prompt = f"""
    Convert the following {detect_dbms(original_query)} query to PostgreSQL syntax:

    {original_query}
    """
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=200,
        temperature=0.2,
    )
    return response.choices[0].text.strip()


# Function to detect the DBMS based on query structure
def detect_dbms(query):
    if "LIMIT" in query or "SHOW DATABASES" in query:
        return "MySQL"
    elif "DESC" in query or "DUAL" in query:
        return "Oracle"
    elif "TOP" in query or "[" in query:
        return "MS SQL"
    return "unknown"


# Endpoint to execute queries
@app.route("/execute_query", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        # Translate the query to PostgreSQL
        pg_query = translate_query(query)
        conn = connect_postgres()
        cursor = conn.cursor()
        cursor.execute(pg_query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
