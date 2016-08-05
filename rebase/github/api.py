from datetime import datetime
from logging import getLogger
from random import randint
from time import sleep

from github import Github
from github.MainClass import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_PER_PAGE
from github.Requester import Requester

from rebase.common.debug import pdebug


logger = getLogger(__name__)


min_delta = 3600/5000 # min seconds to wait before next request


class RebaseGithubException(Exception):
    _request_format = 'Request {} {} with parameters: {}'.format

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class GithubRateLimitMaxRetries(RebaseGithubException):

    def __init__(self, verb, url, parameters):
        super().__init__('Exceeded max retries for '+self._request_format(verb, url, parameters))


class GithubAbuseBlock(RebaseGithubException):

    def __init__(self, message, verb, url, parameters):
        super().__init__(message+' '+self._request_format(verb, url, parameters))


class RebaseRequester(Requester):

    def __init__(self, token, max_retries=3, delay=30):
        self.rate_limit_retries = 0
        self.max_retries = max_retries
        self.delay = delay
        self.last_request_time = None
        super().__init__(token,
                         None,
                         DEFAULT_BASE_URL,
                         DEFAULT_TIMEOUT,
                         None,
                         None,
                         'PyGithub/Python',
                         100,
                         False)

    def _request_encode(self, request_method, *args, **kwargs):
        '''

        Wraps the original PyGithub.Requester.__requestEncode function.
        If the rate limit is reached:
        - wait until reset time plus random seconds between 1 and 'delay'
        - retry, no more than 'max_retries' times.

        Raises GithubRateLimitMaxRetries if 'max_retries' is exceeded.
        Raises GithubAbuseBlock if Github is blocking us because we do not abide by the limit.

        '''
        if self.last_request_time:
            delta_ = datetime.now() - self.last_request_time
            #logger.debug('delta_: %.2f', delta_.total_seconds())
            if delta_.total_seconds() < min_delta:
                nap_time = min_delta - delta_.total_seconds()
                logger.debug('Going too fast! Sleeping %.2f', nap_time)
                sleep(nap_time)
        url_ = args[1]
        pdebug(url_, 'Request URL: ')
        status, responseHeaders, output = request_method(*args, **kwargs)
        self.last_request_time = datetime.utcnow()
        _output = self._Requester__structuredFromJson(output)
        if self.rate_limiting[0] < 10:
            logger.debug('Rate Limit | Remaining Calls: %d, Limit: %d', self.rate_limiting[0], self.rate_limiting[1])
        if status == 403 and _output.get("message").startswith("API Rate Limit Exceeded"):
            if 'Retry-After' in responseHeaders:
                logger.debug('Found Retry-After header!!! wait %d seconds pleeze', responseHeaders['Retry-After'])
            self.rate_limit_retries += 1
            if self.rate_limit_retries > self.max_retries:
                raise GithubRateLimitMaxRetries(*args[0:3])
            delta = datetime.utcfromtimestamp(self.rate_limiting_resettime) - datetime.utcnow()
            nap_time = delta.total_seconds()+randint(1, self.delay)
            logger.debug('Rate Limited! Sleeping for %d minutes and %d seconds', nap_time // 60, nap_time % 60)
            sleep(nap_time)
            # recurse up to max_retries calls
            status, responseHeaders, output = self._request_encode(request_method, *args, **kwargs)
        if status == 403 and _output.get('message').startswith('You have triggered an abuse detection mechanism'):
            if self.rate_limit_retries > self.max_retries:
                raise GithubRateLimitMaxRetries(*args[0:3])
            if 'Retry-After' in responseHeaders:
                nap_time = int(responseHeaders['Retry-After'])
                logger.debug('Detect Abuse Blocking Message from Github. Sleeping for %d minutes and %d seconds', nap_time // 60, nap_time % 60)
                sleep(nap_time)
                self.rate_limit_retries += 1
                status, responseHeaders, output = self._request_encode(request_method, *args, **kwargs)
            else:
                raise GithubAbuseBlock(_output.get('message'), *args[0:3])
        self.rate_limit_retries = 0
        return status, responseHeaders, output

    def requestJson(self, *args, **kwargs):
        return self._request_encode(super().requestJson, *args, **kwargs)

    def requestMultipart(self, *args, **kwargs):
        return self._request_encode(super().requestMultipart, *args, **kwargs)


class RebaseGithub(Github):

    def __init__(self, token):
        super().__init__(token)
        self._Github__requester = RebaseRequester(token)



