# Copyright (c) 2017 LINE Corporation
# These sources are released under the terms of the MIT license: see LICENSE

import logging
import textwrap

from django.conf import settings

from promgen.models import Project, Service

logger = logging.getLogger(__name__)


class NotificationBase(object):
    '''
    Base Notification class
    '''
    MAPPING = [
        ('project', Project),
        ('service', Service),
    ]

    def __init__(self):
        # In case some of our sender plugins are not using celery,
        # We store our calling function in self.__send so that send()
        # and test() can call the correct function while leaving the
        # original function alone in case it needs to be called directly
        if hasattr(self._send, 'delay'):
            self.__send = self._send.delay
        else:
            self.__send = self._send

    @classmethod
    def help(cls):
        if cls.__doc__:
            return textwrap.dedent(cls.__doc__)

    def _send(self, target, alert, data):
        '''
        Sender specific implmentation

        This function will receive some kind of target value, such as an email
        address or post endpoint and an individual alert combined with some
        additional alert meta data
        '''
        raise NotImplementedError()

    def config(self, key):
        '''
        Plugin specific configuration

        This wraps our PROMGEN settings so that a plugin author does not need to
        be concerned with how the configuration files are handled but only about
        the specific key.
        '''
        try:
            return settings.PROMGEN[self.__module__][key]
        except KeyError:
            logger.error('Undefined setting. Please check for %s under %s in settings.yml', key, self.__module__)

    def send(self, data):
        '''
        Send out an alert

        This handles looping through the alerts from Alert Manager and checks
        to see if there are any notification senders configured for the
        combination of project/service and sender type.

        See tests/examples/alertmanager.json for an example payload
        '''
        sent = 0
        alerts = data.pop('alerts', [])
        for alert in alerts:
            for label, klass in self.MAPPING:
                if label not in alert['labels']:
                    logger.debug('Missing label %s', label)
                    continue
                logger.debug('Checking senders for %s=%s', label, alert['labels'][label])
                for obj in klass.objects.filter(name=alert['labels'][label]):
                    for sender in obj.sender.filter(sender=self.__module__):
                        logger.debug('Sending to %s', sender)
                        if self.__send(sender.value, alert, data):
                            sent += 1
        if sent == 0:
            logger.debug('No senders configured for project or service')
        return sent

    def test(self, target, alert):
        '''
        Send out test notification

        Combine a simple test alert from our view, with the remaining required
        parameters for our sender child classes
        '''
        logger.debug('Sending test message to %s', target)
        self.__send(target, alert, {'externalURL': ''})
