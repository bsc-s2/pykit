import errno
import logging
import socket
import select

logger = logging.getLogger(__name__)

class S2HttpError(Exception): pass
class BadStatus(S2HttpError): pass
class LineTooLong(S2HttpError): pass
class BadHeadersError(S2HttpError): pass
class ChunkedSizeError(S2HttpError): pass
class NotConnectedError(S2HttpError): pass
class ResponseNotReady(S2HttpError): pass
class HeadersError(S2HttpError): pass
class BadStatusLine(S2HttpError): pass

_MAXLINESIZE = 65536
LINE_RECV_LENGTH = 1024*4
BLOCK_LENGTH = 1024 * 1024 * 20
SEND_BLOCK_SIZE = 8192

NO_CONTENT = 204
NOT_MODIFIED = 304

#example, how to use
#   http = Http('127.0.0.1', 6003)
#   http.request('/file/aa')
#   status = http.status
#   headers = http.headers
#   buf = http.read_body(50*MB)
#or
#   http = Http('127.0.0.1', 6003)
#   http.send_request('file/aa')
#   http.send_body(body)
#   http.finish_request()
#   status = http.status
#   headers = http.headers
#   buf = http.read_body(50*MB)

class Http(object):

    def __init__(self, ip, port, timeout = 60):

        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None

        self.chunked = False
        self.chunk_left = None
        self.content_length = None
        self.has_read = 0

        self.status = None
        self.headers = {}

        self.recv_iter = None

    def __del__( self ):

        if self.recv_iter is not None:
            try:
                self.recv_iter.close()
            except:
                pass
        self.recv_iter = None

        if self.sock is not None:
            try:
                self.sock.close()
            except:
                pass
        self.sock = None

    def request(self, uri, method = 'GET', headers = {}):

        self.send_request( uri, method = method, headers = headers )

        self.finish_request()

    def send_request( self, uri, method = 'GET', headers = {} ):

        self._reset_request()

        self.method = method

        sbuf = [ '{method} {uri} HTTP/1.1'.format( method=method, uri=uri ), ]
        sbuf += self._norm_headers(headers)

        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.sock.settimeout( self.timeout )
        self.sock.connect( (self.ip, self.port) )

        sbuf.extend(['', ''])
        msg = "\r\n".join( sbuf )

        self.sock.sendall( msg )

    def send_body( self, body ):
        if self.sock is None:
            raise NotConnectedError()

        self.sock.sendall( body )

    def finish_request( self ):

        if self.status is not None:
            raise ResponseNotReady()

        self.recv_iter = _recv_loop( self.sock, self.timeout )
        # swollow the first yield and let recv_iter wait for argument
        self.recv_iter.next()

        self._load_resp_status()
        self._load_resp_headers()

    def read_body(self, size):

        if size is None or size < 0:
            raise ValueError('size error!')

        if self.chunked:
            buf = self._read_chunked(size)
            self.has_read += len(buf)
            return buf

        if size > self.content_length - self.has_read:
            size = self.content_length - self.has_read

        if size <= 0:
            return ''

        buf = self._read(size)
        self.has_read += size

        return buf

    def _reset_request(self):

        self.chunked = False
        self.chunk_left = None
        self.content_length = None
        self.has_read = 0

        self.status = None
        self.headers = {}

    def _norm_headers( self, headers=None ):

        _h = {
            'Host': self.ip,
        }
        _h.update( headers or {} )

        hs = []

        for hk, hv in _h.items():
            hs.append( '%s: %s'%(hk, hv) )

        return hs

    def _read(self, size):
        return self.recv_iter.send( ( 'block', size ) )

    def _readline(self):
        return self.recv_iter.send( ( 'line', None ) )

    def _read_status(self):

        line = self._readline()

        try:
            version, status, reason = line.strip().split(None, 2)
            status = int( status )
        except ValueError as e:
            logger.error( repr( e ) )
            raise BadStatusLine( line )

        if not version.startswith('HTTP/'):
            raise BadStatusLine( line )

        if status < 100 or status > 999:
            raise BadStatusLine( line )

        return status

    def _load_resp_status(self):

        while True:

            status = self._read_status()
            if status >= 200:
                break

            # skip the header from the 100 response
            while True:
                skip = self._readline()
                if skip.strip() == '':
                    break

        self.status = status

    def _load_resp_headers(self):

        while True:

            line = self._readline()
            if line == '':
                break

            kv = line.strip().split(':', 1)
            hname = kv[0]
            hval = kv[1]

            self.headers[ hname.lower() ] = hval.strip()

        if (self.status == NO_CONTENT or self.status == NOT_MODIFIED
            or self.method == 'HEAD'):
            self.content_length = 0
            return

        code = self.headers.get('transfer-encoding', '')
        if code.lower() == 'chunked':
            self.chunked = True
            self.content_length = None
            return

        length = self.headers.get('content-length')
        if length is None:
            self.content_length = 0
        elif not length.isdigit():
            raise HeadersError('content-length header value error')
        else:
            self.content_length = int(length)

    def _get_chunk_size(self):

        line = self._readline()

        i = line.find(';')
        if i >= 0:
            # strip chunk-extensions
            line = line[:i]

        try:
            chunk_size = int(line, 16)
        except ValueError:
            raise ChunkedSizeError()

        return chunk_size

    def _read_chunked(self, size):

        buf = []

        if self.chunk_left == 0:
            return ''

        while size > 0:

            if self.chunk_left is None:
                self.chunk_left = self._get_chunk_size()

            if self.chunk_left == 0:
                break

            toread = min(size, self.chunk_left)
            buf.append( self._read(toread) )

            size -= toread
            self.chunk_left -= toread

            if self.chunk_left == 0:
                self._read( len('\r\n') )
                self.chunk_left = None

        if self.chunk_left != 0:
            return ''.join(buf)

        # discard trailer
        while True:
            line = self._readline()
            if line == '':
                break

        self.chunk_left = 0

        return ''.join(buf)

def _recv_loop( sock, timeout ):

    bufs = ['']
    mode, size = yield

    while True:

        if mode == 'line':

            buf = bufs[ 0 ]
            if '\r\n' in buf:
                rst, buf = buf.split( '\r\n', 1 )
                bufs[ 0 ] = buf
                mode, size = yield rst
                continue
            else:
                if len( buf ) >= _MAXLINESIZE:
                    raise LineTooLong()
                else:
                    buf += _recv_raise( sock, timeout, LINE_RECV_LENGTH )[ 'buf' ]
                    bufs[ 0 ] = buf
                    continue
        else:
            total = len( bufs[ 0 ] )
            while total < size:
                bufs.append( _recv_raise( sock, timeout, size-total )[ 'buf' ] )
                total += len(bufs[ -1 ])

            rst = ''.join( bufs )
            if size < len( rst ):
                bufs = [ rst[ size: ] ]
                rst = rst[ :size ]
            else:
                bufs = [ '' ]
            mode, size = yield rst

def _recv_raise( sock, timeout, size ):

    o = { 'buf':None }

    for ii in range( 2 ):
        try:
            o['buf'] = sock.recv( size )
            break
        except socket.error as e:
            if len(e.args) > 0 and e.args[ 0 ] == errno.EAGAIN:
                evin, evout, everr = select.select(
                        [ sock.fileno() ], [], [], timeout )
                if len( evin ) != 0:
                    continue
                else:
                    raise socket.timeout( 'timeout %d seconds while waiting to recv'
                                          % timeout )
            else:
                raise

    if o['buf'] == '':
        raise socket.error('want to read %d bytes, but read empty !' % size)

    return o

