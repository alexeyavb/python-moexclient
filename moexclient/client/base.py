import json
import sys
import socket
import warnings
from urlparse import urlparse
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection

LOG = logging.getLogger(__name__)


class TCPKeepAliveHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        options = list(HTTPConnection.default_socket_options)
        if sys.platform == 'linux2':
            options.extend([
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 7)
            ])
        elif sys.platform == 'darwin':
            options.extend([
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            ])
        # keepalive is not implemented for windows
        kwargs['socket_options'] = options
        return super(TCPKeepAliveHTTPAdapter, self).init_poolmanager(*args,
                                                                     **kwargs)


class Session(object):
    def __init__(self, url, session=None):
        """ Session controlled communication client.

        :param url: backend url
        """
        self.url = url
        self._json = json.JSONEncoder

        if not session:
            session = requests.Session()
            for schema in list(session.adapters):
                session.mount(schema, TCPKeepAliveHTTPAdapter())

        self.session = session

        # FIXME(akurbatov): add cert/key for verify=True
        self.session.verify = False
        warnings.filterwarnings('ignore', 'Unverified HTTPS request')

    def _log_request(self, url, method, **kwargs):
        if not LOG.isEnabledFor(logging.DEBUG):
            return

        string_parts = ['REQ: curl -g -i --insecure']
        string_parts.extend(['-X', method.upper()])
        string_parts.append(url)

        headers = kwargs.get('headers')
        data = kwargs.get('data')
        json = kwargs.get('json')

        if headers:
            for header_name, header_value in headers.items():
                string_parts.append(
                    '-H "{}: {}"'.format(header_name, header_value))

        if json:
            data = self._json.encode(json)

        if data:
            string_parts.append("-d '{}'".format(data))

        LOG.debug(' '.join(string_parts))

    def _log_response(self, resp):
        if not LOG.isEnabledFor(logging.DEBUG):
            return

        content_type = resp.headers.get('Content-Type', None)
        if 'application/json' in content_type:
            text = data = json.loads(resp.text)
        else:
            text = 'Omitted, Content-Type is set to {}.'.format(content_type)

        string_parts = ['RESP:']
        string_parts.append('[{}]'.format(resp.status_code))

        for header_name, header_value in resp.headers.items():
            string_parts.append('{}: {}'.format(header_name, header_value))

        string_parts.append('\nRESP BODY: {}\n'.format(text))

        LOG.debug(' '.join(string_parts))

    def request(self, method, url, raise_exc=True, **kwargs):
        if not urlparse(url).netloc:
            url = "{}/{}".format(self.url.rstrip('/'), url.lstrip('/'))

        resp = self._send_request(method, url, **kwargs)
        if raise_exc:
            resp.raise_for_status()

        return resp

    def _send_request(self, method, url, connect_retries=0,
                      connect_retry_delay=0.5, **kwargs):
        self._log_request(url, method, headers=kwargs.get('headers'),
                          data=kwargs.get('data'),
                          json=kwargs.get('json'))
        try:
            resp = self.session.request(method, url, **kwargs)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as err:
            if connect_retries <= 0:
                raise
            LOG.info('Request failure: %s. Retrying in %.1fs.',
                     err, connect_retry_delay)
            time.sleep(connect_retry_delay)

            return self._send_request(
                method, url,
                connect_retries=connect_retries - 1,
                connect_retry_delay=connect_retry_delay * 2,
                **kwargs)

        self._log_response(resp)
        return resp

    def get(self, url, **kwargs):
        """Perform a GET request.
        """
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request.
        """
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request.
        """
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request.
        """
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request.
        """
        return self.request('PATCH', url, **kwargs)


class MoexClient(object):
    def __init__(self):
        session = Session('http://iss.moex.com/iss')
        self.histoty = HistotyClient(session)
        self.markets = MarketManager(session)
        self.boards = BoardsManager(session)
        self.securities = SecuritiesManager(session)
        self.indices = IndexManager(session)


class BaseClient(object):
    def __init__(self, session):
        self.session = session

    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', (None, 100))
        response = self.session.request(method, url, **kwargs)
        content_type = response.headers.get('Content-Type')
        if 'application/json' in content_type.lower() and response.text:
            data = response.json()
        else:
            data = response.text
        return data

    def _get(self, url, **params):
        url += '.json?iss.meta=off'
        # json_extended = params.pop('json_extended', False)
        # if json_extended:
        #     url += '&iss.json=extended'

        for kv in params.items():
            url += '&%s=%s' % kv
        data = self.request('GET', url)

        result = {}
        for group, data in data.items():
            columns, values = data['columns'], data['data']
            list(dict(zip(columns, vals)) for vals in values)
            result[group] = [dict(zip(columns, vals)) for vals in values]

        return result


class HistotyClient(BaseClient):
    def get(self, engine='stock', market='stocks', board=None, security=None, data=None):
        if not board:
            raise Exception('board is not specified')
        return self._get('/history/engines/%s/markets/%s/boards/%s/securities')


class MarketManager(BaseClient):
    def list(self, engine='stock'):
        return self._get('/engines/%s/markets' % engine)


class BoardsManager(BaseClient):
    def list(self, market, engine='stock'):
        return self._get('/engines/%s/markets/%s/boards' % (engine, market))


class SecuritiesManager(BaseClient):
    def find(self, query, all=False):
        params = {'q': query}
        if not all:
            params['is_trading'] = 1
        return self._get('/securities', **params)

    def get(self, secid, **params):
        return self._get('/securities/%s' % secid, **params)

    def get_marketdata(self, secid, engine, market, **params):
        url = '/engines/%s/markets/%s/securities/%s' % (engine, market, secid)
        data = self._get(url, **params)

    def get_by_market(self, secid, engine, market, board=None):
        url = '/engines/%s/markets/%s' % (engine, market)
        if board:
            url += '/boards/%s/' % board
        url += '/securities/%s' % secid
        return self._get(url)

    def list(self, market, engine='stock', board=None, index=None, securities=None):
        if board:
            url = '/engines/%s/markets/%s/boards/%s/securities' % (engine, market, board)
        else:
            url = '/engines/%s/markets/%s/securities' % (engine, market)

        params = {}
        if index:
            params['index'] = index
        if securities:
            params['securities'] = securities

        return self._get(url, **params)


class IndexManager(BaseClient):
    def list(self):
        return self._get('/statistics/engines/stock/markets/index/analytics')
