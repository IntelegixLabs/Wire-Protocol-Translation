import psycopg
from sqlparse import parse
from flask import Flask, request, jsonify

class WireTranslator:
    def __init__(self, pg_host="localhost", pg_port=5432, pg_user="postgres", pg_password="password", pg_db="test_db"):
        self.conn = psycopg.connect(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            dbname=pg_db
        )
        self.cursor = self.conn.cursor()

    def translate_query(self, original_query):
        # Basic translation logic from MySQL to PostgreSQL
        parsed_query = parse(original_query)[0]
        tokens = [token.value for token in parsed_query.tokens if not token.is_whitespace]

        if tokens[0].lower() == "show":
            if tokens[1].lower() == "databases":
                return "SELECT datname FROM pg_database;"
            elif tokens[1].lower() == "tables":
                return "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        elif tokens[0].lower() == "describe":
            return f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{tokens[1]}';"

        return original_query  # Return unmodified if no translation rule applies

    def execute_query(self, query):
        translated_query = self.translate_query(query)
        self.cursor.execute(translated_query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

# Flask server to accept queries from the client
app = Flask(__name__)
translator = WireTranslator()

@app.route("/execute_query", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        result = translator.execute_query(query)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/close", methods=["POST"])
def close_connection():
    translator.close()
    return jsonify({"message": "Connection closed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
