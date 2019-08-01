# README #
This is a simple Python HTTPS proxy server with HTTP basic authentication. 
It is intended to use when you need to secure an access to some plain HTTP 
resource and you don't want to mess with installing and configuring special 
software like Nginx and etc.  

Uses threads to handle connections so not suitable for high loads.  

**Important note**: keep-alive connections are not supported yet.

## Configuration
Open `settings.py` file and set the `PROXIED_HOST` and `PROXIED_PORT` variables.
Also set the `CERTFILE_PATH` and `KEYFILE_PATH` to values that define where 
your SSL certificate and private key files are located.

## Running
Type the command in terminal:
```cmd
python server.py
```

On Linux if you need the server to run in the background then run the command:
```bash
nohup python server.py &
```