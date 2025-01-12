# SQL Query Converter Client Library

## **Project Overview**
The objective of this project is to build a **client-side library** that translates SQL queries from various relational database management systems (DBMSes) such as **MySQL**, **Oracle**, and **MS SQL** to be compatible with **PostgreSQL** using its **native wire protocol**. This library will serve as a middle layer, enabling applications to connect to PostgreSQL without modifying their existing DB-specific queries.

---

## **Architecture Design**
### **Current Workflow (Without the Library)**
```
Application > Original DB Client > Original DBMS
```

### **Proposed Workflow (With the Library)**
```
Application > Our DB Client > PostgreSQL
```
- The **Application** sends queries in the original DBMS's dialect.
- The **Our DB Client** library intercepts the queries, translates them to PostgreSQL-compatible queries, and communicates with PostgreSQL using its native wire protocol.
- The **PostgreSQL** server processes the translated query and returns results through the library.

---

## **Key Features of the Library**
1. **SQL Dialect Translation**
   - Translates queries from MySQL, Oracle, and MS SQL into PostgreSQL syntax.
   - Handles differences in functions, data types, and query structures.

2. **PostgreSQL Wire Protocol Implementation**
   - Implements the PostgreSQL wire protocol to communicate directly with the PostgreSQL server.
   - Supports authentication, query execution, and result handling.

3. **Python API**
   - Provides a Python interface for connecting to PostgreSQL using translated queries.
   - Pluggable with existing DB clients for seamless integration.

4. **Error Handling and Compatibility Checks**
   - Detects and logs incompatible queries.
   - Suggests modifications or fallback options when translation is not possible.

---

## **SQL Translation Examples**
### **MySQL to PostgreSQL Translation**
| MySQL Query                        | PostgreSQL Equivalent              |
|------------------------------------|------------------------------------|
| `SELECT NOW();`                    | `SELECT CURRENT_TIMESTAMP;`        |
| `SHOW TABLES;`                     | `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';` |
| `LIMIT 10, 20`                     | `LIMIT 20 OFFSET 10`               |
| `AUTO_INCREMENT`                   | `SERIAL`                           |

### **Oracle to PostgreSQL Translation**
| Oracle Query                       | PostgreSQL Equivalent              |
|------------------------------------|------------------------------------|
| `SELECT SYSDATE FROM DUAL;`        | `SELECT CURRENT_TIMESTAMP;`        |
| `ROWNUM`                           | `LIMIT`                            |
| `NVL(column, 'default')`           | `COALESCE(column, 'default')`      |
| `VARCHAR2`                         | `VARCHAR`                          |

### **MS SQL to PostgreSQL Translation**
| MS SQL Query                       | PostgreSQL Equivalent              |
|------------------------------------|------------------------------------|
| `GETDATE()`                        | `CURRENT_TIMESTAMP`                |
| `TOP 10`                           | `LIMIT 10`                         |
| `ISNULL(column, 'default')`        | `COALESCE(column, 'default')`      |
| `IDENTITY(1,1)`                    | `SERIAL`                           |

---

## **Wire Protocol Implementation**
The PostgreSQL wire protocol is a binary protocol used for communication between a client and a PostgreSQL server. Our library will implement key aspects of this protocol, including:

1. **Startup Message**
2. **Authentication**
3. **Query Execution**
4. **Result Parsing**
5. **Error Handling**

---

## **Python API Design**
```python
class DBClient:
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Establish a connection to the PostgreSQL server."""
        self.connection = self._start_postgres_connection()

    def execute_query(self, query: str) -> list:
        """Translate and execute a query on the PostgreSQL server."""
        translated_query = self._translate_query(query)
        return self._send_query(translated_query)

    def _translate_query(self, query: str) -> str:
        """Translate queries from MySQL/Oracle/MS SQL to PostgreSQL."""
        # Implement query translation logic here
        pass

    def _start_postgres_connection(self):
        """Handle the PostgreSQL wire protocol startup."""
        # Implement wire protocol logic here
        pass

    def _send_query(self, query: str) -> list:
        """Send the query to PostgreSQL and parse the results."""
        # Implement query execution logic here
        pass
```

---

## **Example Usage**
```python
from db_client import DBClient

# Initialize the client
client = DBClient(host="localhost", port=5432, user="admin", password="secret")

# Connect to PostgreSQL
client.connect()

# Execute a MySQL query
results = client.execute_query("SELECT NOW();")
print(results)
```

---

## **Testing**
To test the library, we will:
1. Set up a **PostgreSQL server**.
2. Write **unit tests** to validate query translations.
3. Ensure that the client can successfully connect to PostgreSQL and execute queries.

### **Unit Test Example**
```python
import unittest
from db_client import DBClient

class TestDBClient(unittest.TestCase):
    def setUp(self):
        self.client = DBClient(host="localhost", port=5432, user="test_user", password="test_pass")
        self.client.connect()

    def test_query_translation(self):
        mysql_query = "SELECT NOW();"
        expected_pg_query = "SELECT CURRENT_TIMESTAMP;"
        self.assertEqual(self.client._translate_query(mysql_query), expected_pg_query)

    def test_query_execution(self):
        results = self.client.execute_query("SELECT CURRENT_TIMESTAMP;")
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()
```

---

## **Future Enhancements**
1. **Support for Additional DBMS Dialects**
   - Extend translation support for DBMSes like SQLite, DB2, etc.

2. **Advanced Query Parsing**
   - Use a SQL parser library to handle complex queries and edge cases.

3. **Performance Optimization**
   - Optimize the wire protocol implementation for better performance.

4. **GUI for Query Translation**
   - Provide a GUI tool for users to test query translations interactively.

---

## **Conclusion**
This client library provides a novel solution for enhancing the portability of SQL queries across DBMSes by translating them into PostgreSQL-compatible queries and handling communication via the PostgreSQL wire protocol. With proper testing and optimizations, this solution can be a robust tool for developers migrating from other relational databases to PostgreSQL.

