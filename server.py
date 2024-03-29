import base64
import logging
import socket
import ssl
import threading
import traceback

from exc import BasicAuthError
import settings as cfg


class ConnHandler(threading.Thread):

    def __init__(self, client_sock: ssl.SSLSocket, addr: tuple, *args, **kwargs):
        self.sock = client_sock
        self.sock.settimeout(cfg.SOCK_TIMEOUT)
        self.addr = addr
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        rxbuf = True
        msgbuf = []
        err = False
        # keep_alive = False

        while rxbuf:
            try:
                rxbuf = self.sock.recv(cfg.CHUNK_SIZE)
            except ssl.SSLError as e:
                logging.error('ssl.SSLError, %s', e)
                err = True
                break
            except OSError as e:
                logging.error('exception on recv(): %s', e)
                traceback.print_exc()
                err = True
                break

            msgbuf.append(rxbuf)
            logging.debug(rxbuf)

            # keep_alive = 'keep-alive' in rxbuf
            if b'\r\n\r\n' in rxbuf:
                break

        msgbuf = b''.join(msgbuf)

        if not err and msgbuf:
            try:
                self.check_basic_auth(msgbuf)
                self.proxy_request(msgbuf)
            except BasicAuthError:
                logging.error('AuthError')
                self.send_basicauth_err()
            except OSError as err:
                logging.error(err)
        
        self.sock.shutdown(socket.SHUT_WR)
        logging.debug('socket shutdown %s', self.sock)
        self.sock.close()
        logging.debug('socket closed %s', self.sock)

        logging.debug('Thread stopped')

    @staticmethod
    def check_basic_auth(msgbuf: bytes):
        buf_lower = msgbuf.lower()
        try:
            auth_index = buf_lower.index(b'authorization:')
        except ValueError:
            raise BasicAuthError

        auth_header = msgbuf[auth_index:].split(b'\r\n', maxsplit=1)[0]
        header_data = auth_header.partition(b':')[2].lstrip()
        auth_data = header_data.split(b' ')[1]
        login, passwd = base64.b64decode(auth_data).decode().split(':')

        if not (login == cfg.BASIC_LOGIN and passwd == cfg.BASIC_PASSWD):
            raise BasicAuthError

    def send_basicauth_err(self):
        resp = (
            b'HTTP/1.1 401 Unauthorized\r\n'
            b'WWW-Authenticate: Basic realm="' + 
            bytes(cfg.BASIC_REALM, 'ascii') + b'"\r\n\r\n'
        )

        logging.debug(resp)

        self.socksend(self.sock, resp)

    def proxy_request(self, msgbuf: bytes):
        """Proxy received request to a remote server and return response to the 
        requester."""
        rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rsock.connect((cfg.PROXIED_HOST, cfg.PROXIED_PORT))

        self.socksend(rsock, msgbuf)
        rsock.shutdown(socket.SHUT_WR)

        chunk = True
        while chunk:
            chunk = rsock.recv(cfg.CHUNK_SIZE)
            if chunk:
                self.socksend(self.sock, chunk)

        logging.debug('request proxied, remote socket close')

        rsock.shutdown(socket.SHUT_RDWR)
        rsock.close()

    @staticmethod
    def socksend(sock: socket.socket, msg: bytes):
        sent = 0
        msglen = len(msg)

        while sent < msglen:
            sent += sock.send(msg[sent:])


def create_tls_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=cfg.CERTFILE_PATH, keyfile=cfg.KEYFILE_PATH)
    # Enable selfsigned certificates
    ctx.verify_mode = ssl.CERT_OPTIONAL

    return ctx


def accept_loop(sock: ssl.SSLSocket):
    while True:
        client_sock, addr = sock.accept()

        logging.debug('accepted from %s', addr)

        handler = ConnHandler(client_sock, addr)
        handler.start()


def run_server():
    if cfg.DEBUG:
        logging.basicConfig(level='DEBUG')

    # Create IPv4 streaming(TCP) socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind socket to the specified address. The address should correspond to
    # the address family which was used when socket is created. For IPv4
    # address family it is a tuple (host, port)
    sock.bind((cfg.HOST, cfg.PORT))
    # begin to listen and accept connections on bounded socket
    sock.listen(cfg.BACKLOG)

    tlsctx = create_tls_context()
    sock = tlsctx.wrap_socket(sock, server_side=True,
                              do_handshake_on_connect=False,
                              suppress_ragged_eofs=False)
    
    logging.debug(sock)
    
    try:
        accept_loop(sock)
    except KeyboardInterrupt:
        logging.debug('got SIGINT(KeyboardInterrupt)')
    except OSError as err:
        logging.error(err)
        traceback.print_exc()

    sock.close()

    # wait for all client sockets handlers to complete
    logging.debug('waiting for not closed requests...')


if __name__ == '__main__':
    run_server()
