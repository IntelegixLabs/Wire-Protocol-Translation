// wire_client.h
#ifndef WIRE_CLIENT_H
#define WIRE_CLIENT_H

#ifdef __cplusplus
extern "C" {
#endif

// Initializes the connection to the Python Flask server
int initialize_connection(const char* server_url);

// Sends a query to the Flask server and returns the result
char* execute_query(const char* query);

// Sends a batch of queries to the Flask server and returns the combined results
char* execute_batch_queries(const char* queries[], size_t query_count);

// Closes the connection to the Flask server
void close_connection();

#ifdef __cplusplus
}
#endif

#endif // WIRE_CLIENT_H
