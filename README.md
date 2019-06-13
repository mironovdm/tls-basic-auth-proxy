# README
This is a simple Python HTTPS proxy server with HTTP basic authentication. Initially was created to secure access to Prometheus but may be used for another similar purposes. A proxied request to a remote server is not secured by TLS.

Uses threads to handle connections so not suitable for high loads.
