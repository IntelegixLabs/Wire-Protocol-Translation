## 🛠️ How It Works

- <strong>Detect the Source DBMS:</strong>
The script identifies whether the incoming query is from MySQL, Oracle, or MS SQL based on specific keywords.


- <strong>Send Query to OpenAI:</strong>
The translate_query function sends the query to OpenAI's GPT model with a prompt asking for conversion to PostgreSQL syntax.


- <strong>Execute on PostgreSQL:</strong>
The translated query is executed on the PostgreSQL database, and the result is returned to the client.

## Install the required packages:

```commandline
pip install Flask psycopg openai
```

## Replace your_openai_api_key with your OpenAI API key.

## Start the Flask server:

```commandline
python query_translator.py
```

## Send a query to the server (via Postman or Curl):

```commandline
curl -X POST http://localhost:5000/execute_query -H "Content-Type: application/json" -d '{"query": "SHOW DATABASES;"}'
```