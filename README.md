# README
This is a simple Python HTTPS proxy server with HTTP basic authentication. Initially was created to secure Prometheus access but may be used for another similar purposes.

In the current form it is not very suitable for high load projects because of using threads to handle accepted connections.
