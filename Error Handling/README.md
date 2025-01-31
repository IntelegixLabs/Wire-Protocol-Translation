<h1 align="center">Implementing Error Handling & Compatibility in the Middleware Proxy Client</h1>

The goal is to **ensure compatibility** between the original DBMS (MySQL, Oracle, MS SQL) and PostgreSQL by handling errors, maintaining session consistency, and mimicking expected responses.

---

## **1. Error Code Translation**  
Each DBMS has its **own error codes and messages**, which must be mapped to PostgreSQL’s equivalents.

### **Example: MySQL vs. PostgreSQL Error Codes**  
| MySQL Error Code | PostgreSQL Equivalent | Description |
|------------------|----------------------|-------------|
| 1064 | 42601 | Syntax error |
| 1049 | 3D000 | Unknown database |
| 1146 | 42P01 | Table does not exist |
| 1045 | 28000 | Authentication failure |

### **Implementation: Map PostgreSQL Errors to MySQL Codes**  
Intercept errors returned by PostgreSQL and translate them before sending them back.

#### **C++ Implementation for MySQL Proxy**
```cpp
#include <unordered_map>
#include <string>
#include <libpq-fe.h>

// Error Mapping
std::unordered_map<std::string, int> pg_to_mysql_errors = {
    {"42601", 1064},  // Syntax error
    {"3D000", 1049},  // Unknown database
    {"42P01", 1146},  // Table does not exist
    {"28000", 1045}   // Authentication failure
};

// Function to translate PostgreSQL errors to MySQL error codes
int translate_pg_error(PGresult *pg_res) {
    std::string sqlstate = PQresultErrorField(pg_res, PG_DIAG_SQLSTATE);
    if (pg_to_mysql_errors.find(sqlstate) != pg_to_mysql_errors.end()) {
        return pg_to_mysql_errors[sqlstate];
    }
    return 2000;  // Default MySQL error (General Error)
}
```

---

## **2. Transaction Handling**  
Different databases handle transactions differently. PostgreSQL, for example, uses explicit `BEGIN` and `COMMIT`, whereas MySQL has **autocommit enabled by default**.

### **Key Transaction Differences**
| DBMS  | Default Behavior |
|-------|-----------------|
| **MySQL** | Autocommit ON |
| **PostgreSQL** | Requires `BEGIN; ... COMMIT;` |

### **Solution**
1. If an incoming query is `START TRANSACTION` in MySQL, translate it to `BEGIN;` in PostgreSQL.
2. If autocommit is enabled in MySQL, automatically append `COMMIT;` after queries.
3. Ensure rollback compatibility when errors occur.

#### **C++ Implementation**
```cpp
void handle_transaction(const char* mysql_query, PGconn *pg_conn) {
    std::string query(mysql_query);

    if (query == "START TRANSACTION") {
        PQexec(pg_conn, "BEGIN;");
    } else if (query == "COMMIT") {
        PQexec(pg_conn, "COMMIT;");
    } else if (query == "ROLLBACK") {
        PQexec(pg_conn, "ROLLBACK;");
    } else {
        PQexec(pg_conn, query.c_str());
        // Handle implicit commit for MySQL behavior
        PQexec(pg_conn, "COMMIT;");
    }
}
```

---

## **3. Connection Pooling**  
PostgreSQL uses **persistent connections**, whereas MySQL often uses short-lived connections.  
To optimize performance, **implement a connection pool** to reuse existing database connections instead of opening/closing them for every query.

### **Solution: Use `libpq` Connection Pooling**
- Maintain a **pool of active connections**.
- Reuse connections instead of creating new ones.
- Close unused connections after a timeout.

#### **Example: Simple Connection Pool**
```cpp
#include <vector>
#include <mutex>

std::vector<PGconn*> connection_pool;
std::mutex pool_mutex;

PGconn* get_connection() {
    std::lock_guard<std::mutex> lock(pool_mutex);
    if (!connection_pool.empty()) {
        PGconn* conn = connection_pool.back();
        connection_pool.pop_back();
        return conn;
    }
    return PQconnectdb("dbname=test user=postgres password=secret");
}

void release_connection(PGconn* conn) {
    std::lock_guard<std::mutex> lock(pool_mutex);
    connection_pool.push_back(conn);
}
```

---

## **4. Session Management**  
Different databases handle session-specific settings differently. PostgreSQL does not support **MySQL-specific session variables**, so they need to be mapped accordingly.

### **Handling MySQL `SET` Statements**
- MySQL uses `SET SESSION sql_mode = 'STRICT_TRANS_TABLES';`
- PostgreSQL equivalent: `SET LOCAL sql_mode = 'strict';`

#### **Example: Translating MySQL Session Variables**
```cpp
void handle_session_variable(const char* mysql_query, PGconn *pg_conn) {
    std::string query(mysql_query);

    if (query.find("SET SESSION sql_mode") != std::string::npos) {
        query = "SET LOCAL sql_mode = 'strict';";
    } else if (query.find("SET NAMES utf8") != std::string::npos) {
        query = "SET client_encoding = 'UTF8';";
    }

    PQexec(pg_conn, query.c_str());
}
```

---

## **5. Mimicking Expected Behavior**  
Applications expect the same **response format** from the middleware as they would from the original DBMS.

### **Example: MySQL's `SHOW DATABASES` vs. PostgreSQL**
| MySQL | PostgreSQL Equivalent |
|-------|-----------------------|
| `SHOW DATABASES;` | `SELECT datname FROM pg_database;` |
| `SHOW TABLES;` | `SELECT tablename FROM pg_tables WHERE schemaname = 'public';` |

#### **C++ Implementation:**
```cpp
void handle_show_commands(const char* mysql_query, PGconn *pg_conn) {
    std::string query(mysql_query);
    
    if (query == "SHOW DATABASES") {
        query = "SELECT datname FROM pg_database;";
    } else if (query == "SHOW TABLES") {
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public';";
    }

    PQexec(pg_conn, query.c_str());
}
```

---

## **6. Testing & Validation**
To ensure **error handling and compatibility**, test with real-world applications.  
### **Test Cases**
1. **Error Mapping**
   ```cpp
   PGresult *res = PQexec(conn, "SELECT * FROM non_existing_table;");
   assert(translate_pg_error(res) == 1146);  // MySQL’s "Table does not exist"
   ```
2. **Transaction Handling**
   ```cpp
   handle_transaction("START TRANSACTION", conn);
   assert(PQstatus(conn) == CONNECTION_OK);
   ```
3. **Session Variables**
   ```cpp
   handle_session_variable("SET SESSION sql_mode = 'STRICT_TRANS_TABLES';", conn);
   ```
4. **Connection Pooling**
   ```cpp
   PGconn* conn1 = get_connection();
   release_connection(conn1);
   assert(!connection_pool.empty());
   ```

---

## **Conclusion**
By implementing:
✅ **Error Code Mapping**  
✅ **Transaction Handling**  
✅ **Connection Pooling**  
✅ **Session Management**  
✅ **Response Formatting**  

The middleware will **seamlessly act as a drop-in replacement** for MySQL, Oracle, and MS SQL clients, allowing applications to connect to PostgreSQL without modifications.

