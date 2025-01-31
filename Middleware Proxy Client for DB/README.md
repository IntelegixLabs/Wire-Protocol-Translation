<h1 align="center">Middleware/Proxy Client for DB Wire Protocol Translation</h1>


### **Creating a Middleware/Proxy Client for DB Wire Protocol Translation**  
The goal is to develop a **drop-in replacement** for MySQL, Oracle, or MS SQL client libraries that intercepts database communication, translates queries, and forwards them to a PostgreSQL backend.  

---

## **1. System Overview**
The middleware will:
1. **Expose C/C++ APIs** that match the original DBMS client libraries (e.g., `libmysqlclient`, `OCI`, `dblib`).
2. **Intercept SQL queries** before they are sent to the database.
3. **Translate queries and protocol messages** into PostgreSQL-compatible format.
4. **Send the translated queries to PostgreSQL** and handle responses.
5. **Format the responses** back into the original DBMS format before returning them to the application.

---

## **2. Architecture**
```
Application → (MySQL/Oracle/MS SQL Client API) → [Middleware Proxy] → PostgreSQL
```
- The middleware **pretends to be the original DBMS client library**.
- It translates requests before sending them to PostgreSQL.
- It also translates PostgreSQL responses back to the original DBMS response format.

---

## **3. Implementation Steps**
### **Step 1: Create a Shared Library to Replace the DBMS Client**
We need a **shared library (`.so`/`.dll`)** that exposes the same functions as the original DBMS client.  
- MySQL: `libmysqlclient.so`
- Oracle: `libclntsh.so`
- MS SQL: `libsybdb.so`

#### **Example: Stub for a MySQL-Compatible Client**
```cpp
// proxy_client.cpp
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>

// Define a fake MySQL connection struct
typedef struct {
    int fake_fd;
} proxy_mysql_conn;

// Function to mimic mysql_real_connect()
MYSQL *mysql_real_connect(MYSQL *mysql, const char *host, const char *user, 
                          const char *passwd, const char *db, unsigned int port,
                          const char *unix_socket, unsigned long client_flag) {
    printf("Intercepted mysql_real_connect() -> Redirecting to PostgreSQL\n");
    
    // Here we could set up a connection to PostgreSQL
    return mysql;  // Return a fake connection object
}

// Function to mimic mysql_query()
int mysql_query(MYSQL *mysql, const char *query) {
    printf("Intercepted MySQL Query: %s\n", query);
    
    // Convert MySQL query to PostgreSQL
    std::string translated_query = convert_to_postgresql(query);

    // Forward query to PostgreSQL (use libpq)
    PGconn *conn = PQconnectdb("dbname=test user=postgres password=secret");
    PGresult *res = PQexec(conn, translated_query.c_str());

    int result = PQresultStatus(res) == PGRES_COMMAND_OK ? 0 : 1;
    PQclear(res);
    PQfinish(conn);

    return result;
}

// Compile as: g++ -shared -o libmysqlproxy.so proxy_client.cpp -lpq
```
### **Step 2: Query Translation**
- Use **sqlglot** or **handwritten translation rules**.
- **Example: Converting MySQL to PostgreSQL**
```cpp
std::string convert_to_postgresql(const char* mysql_query) {
    std::string query(mysql_query);

    // Replace MySQL LIMIT syntax with PostgreSQL equivalent
    size_t pos = query.find("LIMIT");
    if (pos != std::string::npos) {
        query.replace(pos, 5, "FETCH FIRST");
    }

    // Replace MySQL NOW() with PostgreSQL CURRENT_TIMESTAMP
    query = std::regex_replace(query, std::regex("NOW\\(\\)"), "CURRENT_TIMESTAMP");

    return query;
}
```

---

### **Step 3: Redirect PostgreSQL Responses to MySQL Format**
- PostgreSQL returns query results in **text or binary format**.
- Convert **PostgreSQL’s response format** into **MySQL-compatible response**.

#### **Example: Mapping PostgreSQL Results to MySQL Results**
```cpp
MYSQL_RES *convert_postgres_to_mysql(PGresult *pg_res) {
    int num_fields = PQnfields(pg_res);
    MYSQL_RES *mysql_res = mysql_store_result();

    for (int i = 0; i < PQntuples(pg_res); i++) {
        MYSQL_ROW row = mysql_fetch_row(mysql_res);
        for (int j = 0; j < num_fields; j++) {
            row[j] = PQgetvalue(pg_res, i, j);
        }
    }
    return mysql_res;
}
```

---

### **Step 4: Provide a Dynamic Link Library**
- **Compile the proxy client as a shared library** (`.so` for Linux, `.dll` for Windows).
- **Override** the original DB client functions.
- **Set LD_PRELOAD** to intercept MySQL client calls dynamically.

#### **Linux Compilation**
```sh
g++ -shared -fPIC -o libmysqlproxy.so proxy_client.cpp -lpq
```

#### **Preload Interception (Linux)**
```sh
LD_PRELOAD=./libmysqlproxy.so my_app
```

#### **Windows Compilation**
```sh
cl /LD proxy_client.cpp /D_USRDLL /D_WINDLL /I C:\path\to\PostgreSQL\include /link /LIBPATH:C:\path\to\PostgreSQL\lib libpq.lib
```

---

### **Step 5: Support Authentication (Optional)**
- PostgreSQL requires different authentication mechanisms.
- You may need to **intercept login packets** and translate credentials.

Example for a fake authentication handler:
```cpp
MYSQL *mysql_real_connect(MYSQL *mysql, const char *host, const char *user, 
                          const char *passwd, const char *db, unsigned int port,
                          const char *unix_socket, unsigned long client_flag) {
    printf("Intercepted Authentication: Redirecting user %s to PostgreSQL\n", user);

    // Authenticate with PostgreSQL
    PGconn *pg_conn = PQsetdbLogin(host, std::to_string(port).c_str(), NULL, NULL, db, user, passwd);

    if (PQstatus(pg_conn) == CONNECTION_BAD) {
        printf("PostgreSQL Connection Failed\n");
        return NULL;
    }

    return mysql;
}
```

---

## **4. Challenges & Solutions**
| Challenge | Solution |
|-----------|----------|
| **MySQL, Oracle, and MSSQL have different query syntaxes** | Use **query translation rules** or **LLM-based conversion** |
| **Different authentication mechanisms** | Intercept login requests and use **PostgreSQL authentication** |
| **Performance overhead of translation** | Use **connection pooling and caching** to optimize performance |
| **Binary vs. Text Protocol Differences** | Implement **binary format conversion** functions |

---

## **5. Testing**
- Use **unit tests** for SQL translation.
- Use **integration tests** with real applications.
- Run `Wireshark` to inspect packets.

Example **Test Case:**
```cpp
void test_query_translation() {
    std::string mysql_query = "SELECT NOW(), a FROM users LIMIT 5";
    std::string expected_pg_query = "SELECT CURRENT_TIMESTAMP, a FROM users FETCH FIRST 5 ROWS ONLY";
    assert(convert_to_postgresql(mysql_query) == expected_pg_query);
}
```

---

## **Conclusion**
- This **middleware proxy client** replaces the original MySQL/Oracle/MSSQL client libraries.
- It **intercepts SQL queries**, translates them into PostgreSQL, and **converts responses back**.
- This allows **applications to migrate seamlessly** without changing code.
