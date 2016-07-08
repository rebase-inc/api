from datetime import datetime
from logging import getLogger
from random import randint
from time import sleep

from github import Github
from github.MainClass import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_PER_PAGE
from github.Requester import Requester


logger = getLogger(__name__)


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
        super().__init__(token,
                         None,
                         DEFAULT_BASE_URL,
                         DEFAULT_TIMEOUT,
                         None,
                         None,
                         'PyGithub/Python',
                         DEFAULT_PER_PAGE,
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
        status, responseHeaders, output = request_method(*args, **kwargs)
        _output = self._Requester__structuredFromJson(output)
        if self.rate_limiting[0] < 10:
            logger.debug('Rate Limit | Remaining Calls: %d, Limit: %d', self.rate_limiting[0], self.rate_limiting[1])
        if status == 403 and _output.get("message").startswith("API Rate Limit Exceeded"):
            self.rate_limit_retries += 1
            if self.rate_limit_retries > self.max_retries:
                raise GithubRateLimitMaxRetries(*args[0:3])
            delta = datetime.utcfromtimestamp(self.rate_limiting_resettime) - datetime.utcnow()
            logger.debug('Rate Limited! Sleeping for %d minutes and %d seconds', delta.total_seconds()//60, delta.total_seconds())
            sleep(delta.total_seconds()+randint(1, self.delay))
            # recurse up to max_retries calls
            status, responseHeaders, output = self._request_encode(request_method, *args, **kwargs)
        if status == 403 and _output.get('message').startswith('You have triggered an abuse detection mechanism'):
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



