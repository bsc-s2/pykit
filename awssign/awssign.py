import base64
import datetime
import hmac
import json
import urllib
from hashlib import sha256

SIGV4_TIMESTAMP = '%Y%m%dT%H%M%SZ'
CREDENTIALS_SUFFIX = 'aws4_request'
EMPTY_PAYLOAD_HASH = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
ALGORITHM = 'AWS4-HMAC-SHA256'
UNSIGNED_PAYLOAD = 'UNSIGNED-PAYLOAD'
VALID_AUTH_ARGS = [
    'X-Amz-Algorithm',
    'X-Amz-Credential',
    'X-Amz-Date',
    'X-Amz-Expires',
    'X-Amz-SignedHeaders',
    'X-Amz-Signature',
]


class InvalidSigningDateError(Exception):
    pass


class InvalidHeadersNotToSignError(Exception):
    pass


class RequestDateFormatError(Exception):
    pass


class InvalidRequestError(Exception):
    pass


class InvalidRequestVerbError(InvalidRequestError):
    pass


class InvalidRequestArgError(InvalidRequestError):
    pass


class InvalidRequestUriError(InvalidRequestError):
    pass


class InvalidRequestHeadersError(InvalidRequestError):
    pass


class InvalidRequestArgNameError(InvalidRequestArgError):
    pass


class InvalidRequestArgValueError(InvalidRequestArgError):
    pass


class InvalidRequestHeaerNameError(InvalidRequestHeadersError):
    pass


class SigV4(object):

    def _to_utf8(self, string):
        if isinstance(string, unicode):
            string = string.encode('utf-8')

        return string

    def _escape(self, s, safe='/'):
        s = self._to_utf8(s)
        return urllib.quote(s, safe)

    def _unescape_plus(self, s):
        s = self._to_utf8(s)
        return urllib.unquote_plus(s)

    def _uri_encode_args(self, args):
        encoded_args = {}
        for k, v in args.items():
            encoded_k = self._escape(k, '~')

            if isinstance(v, basestring):
                encoded_v = self._escape(v, '~')
            elif type(v) == type([]):
                encoded_v = []
                for value in v:
                    if isinstance(value, basestring):
                        encoded_v.append(self._escape(value, '~'))
                    else:
                        encoded_v.append(value)
            else:
                encoded_v = v

            encoded_args[encoded_k] = encoded_v

        return encoded_args

    def _build_canonical_query_string(self, encoded_args):
        arg_names = []
        for k, _ in encoded_args.items():
            if k != 'X-Amz-Signature':
                arg_names.append(k)

        arg_names.sort()

        key_value_strs = []
        for name in arg_names:
            value = encoded_args[name]

            if type(value) == type([]):
                value = value[0]

            if not isinstance(value, str):
                value = ''

            key_value_strs.append(name + '=' + value)

        return '&'.join(key_value_strs)

    def _utf8_join(self, string_list, separator):
        utf8_list = []
        for string in string_list:
            utf8_list.append(self._to_utf8(string))

        return separator.join(utf8_list)

    def _build_canonical_headers(self, signed_headers, headers):
        l = []

        for name in signed_headers.split(';'):
            value = headers[name]

            if type(value) == type([]):
                value_str = self._utf8_join(value, ',')
            elif isinstance(value, basestring):
                value_str = self._to_utf8(value)
            else:
                value_str = ''

            l.append(name + ':' + value_str)

        return '\n'.join(l) + '\n'

    def _build_canonical_request(self, ctx):
        return '\n'.join([
            ctx['verb'],
            ctx['uri'],
            ctx['canonical_query_string'],
            ctx['canonical_headers'],
            ctx['signed_headers'],
            ctx['hashed_payload'],
        ])

    def _build_string_to_sign(self, ctx):
        return '\n'.join([
            ctx['algorithm'],
            ctx['request_date'],
            ctx['credential_scope'],
            ctx['hashed_canonical_request'],
        ])

    def _make_sha256(self, s):
        return sha256(s).hexdigest()

    def _make_hmac_sha256(self, key, msg, to_hex=False):
        if to_hex:
            sig = hmac.new(key, msg, sha256).hexdigest()
        else:
            sig = hmac.new(key, msg, sha256).digest()
        return sig

    def _derive_signing_key(self, secret_key, credential_scope):
        scope_items = credential_scope.split('/')

        k_date = self._make_hmac_sha256('AWS4' + secret_key, scope_items[0])
        k_region = self._make_hmac_sha256(k_date, scope_items[1])
        k_service = self._make_hmac_sha256(k_region, scope_items[2])
        k_signing = self._make_hmac_sha256(k_service, scope_items[3])

        return k_signing

    def _calc_signature(self, signing_key, string_to_sign):
        return self._make_hmac_sha256(signing_key, string_to_sign, to_hex=True)

    def _query_string_to_args(self, query_string):
        args = {}

        if query_string == '':
            return args

        items = query_string.split('&')

        for item in items:
            key, eq_sign, value = item.partition('=')
            arg_name = self._unescape_plus(key)

            if arg_name not in args:
                args[arg_name] = []
            if eq_sign == '=':
                args[arg_name].append(self._unescape_plus(value))
            else:
                args[arg_name].append(True)

        for arg_name, arg_value in args.items():
            if len(arg_value) == 1:
                args[arg_name] = arg_value[0]

        return args

    def _args_to_query_string(self, args):
        qs = []
        encoded_args = self._uri_encode_args(args)

        for arg_name, arg_value in encoded_args.items():
            if isinstance(arg_value, list):
                for value in arg_value:
                    if isinstance(value, str):
                        qs.append(arg_name + '=' + value)
                    elif value == True:
                        qs.append(arg_name)

            elif isinstance(arg_value, str):
                qs.append(arg_name + '=' + arg_value)

            elif arg_value:
                qs.insert(0, arg_name)

        return '&'.join(qs)


class Signer(SigV4):

    def __init__(self, access_key, secret_key, region=None, service=None, default_expires=None):
        self._access_key = self._to_utf8(access_key)
        self._secret_key = self._to_utf8(secret_key)
        self._service = self._to_utf8(service) or 's3'
        self._region = self._to_utf8(region) or 'us-east-1'
        self._default_expires = default_expires or 60

    def _get_request_date(self, request_date):
        if isinstance(request_date, (int, long, float)):
            dt = datetime.datetime.utcfromtimestamp(request_date)
            request_date = dt.strftime(SIGV4_TIMESTAMP)
        elif isinstance(request_date, basestring):
            try:
                datetime.datetime.strptime(request_date, SIGV4_TIMESTAMP)
            except:
                raise RequestDateFormatError(
                    'request date: %s is not iso base formmat like 20161206T120102Z' % str(request_date))
        else:
            datetime_now = datetime.datetime.utcnow()
            request_date = datetime_now.strftime(SIGV4_TIMESTAMP)

        return request_date

    def _clean_query_string(self, query_string):
        items = query_string.split('&')
        qs = []

        for item in items:
            arg_name = item.partition('=')[0]
            arg_name = self._unescape_plus(arg_name)

            if arg_name in VALID_AUTH_ARGS:
                continue

            qs.append(item)

        return '&'.join(qs)

    def _clean_args(self, args):
        for arg_name in VALID_AUTH_ARGS:
            if arg_name in args:
                args.pop(arg_name)

        return args

    def _trimall(self, s):
        return ' '.join(s.split())

    def _standardize_headers(self, headers, headers_not_to_sign):
        headers_not_to_sign_low = []
        for h_name in headers_not_to_sign:
            h_name = self._to_utf8(h_name)
            headers_not_to_sign_low.append(h_name.lower())

        stand_headers = {}

        for k, v in headers.items():
            k = self._to_utf8(k)
            v = self._to_utf8(v)

            low_name = k.lower().strip()
            stand_v = self._trimall(str(v))

            if low_name not in stand_headers:
                stand_headers[low_name] = []

            stand_headers[low_name].append(stand_v)

        for k, v in stand_headers.items():
            if len(v) == 1:
                stand_headers[k] = v[0]

        signed_header_names = []

        for h_name in stand_headers.keys():
            if h_name not in headers_not_to_sign_low:
                signed_header_names.append(h_name)

        signed_header_names.sort()

        return ';'.join(signed_header_names), stand_headers

    def _validate_arg_value(self, arg_value):
        if arg_value == True or isinstance(arg_value, basestring):
            return

        if not isinstance(arg_value, list):
            raise InvalidRequestArgValueError(
                'arg value: %s, must be string or list or True' % repr(arg_value))

        for value in arg_value:
            if not isinstance(value, basestring) and value != True:
                raise InvalidRequestArgValueError(
                    'multi arg value: %s, must be string or True' % repr(value))

    def _validate_uri_and_args(self, uri, args):
        if not isinstance(uri, basestring) or not uri.startswith('/'):
            raise InvalidRequestUriError(
                'uri: %s, must be a string and starts with /' % repr(uri))

        has_query_string = False
        if len(uri.split('?')) > 1:
            has_query_string = True
        if has_query_string == True and args != None:
            raise InvalidRequestError(
                'use both query string and args is not allowed')

        if args == None:
            return

        if type(args) != type({}):
            raise InvalidRequestArgError('args: %s, is not a dict' % repr(args))

        for arg_name, arg_value in args.items():
            if not isinstance(arg_name, basestring):
                raise InvalidRequestArgNameError(
                    'arg name: %s, is not a string' % repr(arg_name))

            self._validate_arg_value(arg_value)

    def _validate_headers(self, headers):
        if not isinstance(headers, dict):
            raise InvalidRequestHeadersError(
                'headers: %s, is not a dict' % repr(headers))

        has_host = False
        for k, _ in headers.items():
            if not isinstance(k, basestring):
                raise InvalidRequestHeaerNameError(
                    'header name: %s, is not a string' % repr(k))

            if k.lower() == 'host':
                has_host = True

        if has_host != True:
            raise InvalidRequestHeadersError('absence of host header')

    def _validate_request(self, request):
        if not isinstance(request, dict):
            raise InvalidRequestError(
                'request: %s, is not a dict' % repr(request))
        if not isinstance(request.get('verb'), basestring):
            raise InvalidRequestVerbError('absence of or invalid request verb')

        self._validate_uri_and_args(request.get('uri'), request.get('args'))

        self._validate_headers(request.get('headers'))

    def _modify_request_headers(self, request, query_auth,
                                sign_payload, request_date):
        has_amz_date = False
        hashed_payload = None

        for k, v in request['headers'].items():
            low_name = k.lower()

            if low_name == 'authorization':
                request['headers'].pop(k)
            elif low_name == 'x-amz-date':
                request['headers'].pop(k)
                has_amz_date = True
            elif low_name == 'x-amz-content-sha256':
                hashed_payload = self._to_utf8(v)
                request['headers'].pop(k)

        if has_amz_date == True or query_auth != True:
            request['headers']['X-Amz-Date'] = request_date

        if hashed_payload != None:
            request['headers']['X-Amz-Content-SHA256'] = hashed_payload
            return hashed_payload

        if query_auth == True:
            return UNSIGNED_PAYLOAD

        if sign_payload != True:
            request['headers']['X-Amz-Content-SHA256'] = UNSIGNED_PAYLOAD
            return UNSIGNED_PAYLOAD

        if isinstance(request.get('body'), basestring) and len(request['body']) > 0:
            hashed_payload = self._make_sha256(self._to_utf8(request['body']))
        else:
            hashed_payload = EMPTY_PAYLOAD_HASH

        request['headers']['X-Amz-Content-SHA256'] = hashed_payload
        return hashed_payload

    def _get_credential_scope(self, request_date, signing_date=None):
        credential_date = signing_date or request_date[:8]

        if not isinstance(credential_date, basestring):
            raise InvalidSigningDateError(
                'invalid signing date: %s, not of string type' % repr(credential_date))

        credential_scope = '/'.join([
            credential_date,
            self._region,
            self._service,
            CREDENTIALS_SUFFIX
        ])

        return credential_scope

    def add_auth(self, request, **argkv):
        self._validate_request(request)

        query_auth = argkv.get('query_auth', False)
        sign_payload = argkv.get('sign_payload', False)
        headers_not_to_sign = argkv.get('headers_not_to_sign', [])

        if not isinstance(headers_not_to_sign, list):
            raise InvalidHeadersNotToSignError(
                'argument headers_not_to_sign is not a list')

        request_date = self._get_request_date(
            self._to_utf8(argkv.get('request_date')))

        credential_scope = self._get_credential_scope(
            request_date, self._to_utf8(argkv.get('signing_date')))

        credential = self._access_key + '/' + credential_scope

        hashed_payload = self._modify_request_headers(
            request, query_auth, sign_payload, request_date)

        signed_headers, stand_headers = self._standardize_headers(
            request['headers'], headers_not_to_sign)

        utf8_uri = self._to_utf8(request['uri'])
        origin_uri_path, delimiter, origin_query_string = utf8_uri.partition(
            '?')

        if delimiter != '?':
            origin_query_string = None

        ctx = {
            'verb': self._to_utf8(request['verb']),
            'uri': self._escape(self._unescape_plus(origin_uri_path), '/~'),
            'algorithm': ALGORITHM,
            'request_date': request_date,
            'credential_scope': credential_scope,
            'signed_headers': signed_headers,
            'hashed_payload': hashed_payload,
        }

        if origin_query_string != None:
            cleaned_origin_query_string = self._clean_query_string(
                origin_query_string)
            args = self._query_string_to_args(cleaned_origin_query_string)
        else:
            args = self._clean_args(request.get('args', {}))
            query_string_from_args = self._args_to_query_string(args)

        auth_args = {}
        if query_auth == True:
            amz_expires = str(argkv.get('expires') or self._default_expires)
            amz_expires = self._to_utf8(amz_expires)
            auth_args = {
                'X-Amz-Algorithm': ALGORITHM,
                'X-Amz-Credential': credential,
                'X-Amz-Date': request_date,
                'X-Amz-Expires': amz_expires,
                'X-Amz-SignedHeaders': ctx['signed_headers'],
            }

            for k, v in auth_args.items():
                args[k] = v

        encoded_args = self._uri_encode_args(args)

        ctx['canonical_query_string'] = self._build_canonical_query_string(
            encoded_args)

        ctx['canonical_headers'] = self._build_canonical_headers(
            signed_headers, stand_headers)

        ctx['canonical_request'] = self._build_canonical_request(ctx)

        ctx['hashed_canonical_request'] = self._make_sha256(
            ctx['canonical_request'])

        ctx['string_to_sign'] = self._build_string_to_sign(ctx)

        ctx['signing_key'] = self._derive_signing_key(
            self._secret_key, credential_scope)

        ctx['signature'] = self._calc_signature(
            ctx['signing_key'], ctx['string_to_sign'])

        if origin_query_string != None:
            qs = origin_query_string
        else:
            qs = query_string_from_args

        if query_auth == True:
            if len(qs) > 0:
                qs += '&'
            qs += self._args_to_query_string(auth_args)
            qs += '&X-Amz-Signature=' + ctx['signature']

            request['uri'] = origin_uri_path + '?' + qs
        else:
            if len(qs) != 0:
                request['uri'] = origin_uri_path + '?' + qs
            else:
                request['uri'] = origin_uri_path

            l = ['AWS4-HMAC-SHA256 Credential=%s' % credential]
            l.append('SignedHeaders=%s' % ctx['signed_headers'])
            l.append('Signature=%s' % ctx['signature'])
            request['headers']['Authorization'] = ', '.join(l)

        return ctx

    def add_post_auth(self, fields, **argkv):
        request_date = self._get_request_date(
            self._to_utf8(argkv.get('request_date')))

        credential_scope = self._get_credential_scope(
            request_date, self._to_utf8(argkv.get('signing_date')))

        credential = self._access_key + '/' + credential_scope

        ctx = {
            'algorithm': ALGORITHM,
            'request_date': request_date,
            'credential_scope': credential_scope,
            'policy': fields.get('Policy'),
        }

        policy_json_str = json.dumps(ctx['policy'])
        ctx['string_to_sign'] = base64.b64encode(policy_json_str)

        ctx['signing_key'] = self._derive_signing_key(
            self._secret_key, credential_scope)

        ctx['signature'] = self._calc_signature(
            ctx['signing_key'], ctx['string_to_sign'])

        fields['Policy'] = ctx['string_to_sign']
        fields['X-Amz-Algorithm'] = ALGORITHM
        fields['X-Amz-Credential'] = credential
        fields['X-Amz-Date'] = request_date
        fields['X-Amz-Signature'] = ctx['signature']

        return ctx
