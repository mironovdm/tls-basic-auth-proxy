HOST = ''
PORT = 9091

BACKLOG = 10
CHUNK_SIZE = 1024

PROXIED_HOST = 'localhost'
PROXIED_PORT = 9090

# Socket blocking input/output timeout in seconds
SOCK_TIMEOUT = 15

# HTTP Basic auth
BASIC_LOGIN = 'admin'
BASIC_PASSWD = 'passwd'
BASIC_REALM = 'Access to resource'

# TLS settings
CERTFILE_PATH = 'ssl/cert.pem'
KEYFILE_PATH = 'ssl/private.pem'

# Adds HSTS header to response with specified MAX_AGE period
HSTS = False
HTST_MAX_AGE = 60
