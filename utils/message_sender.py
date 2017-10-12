import logging
import plivo

from time import sleep

from utils import StandardAlertLevels


class MessageSender(object):
    """
    Class used to send alerts to users
    """
    RETRY = 10  # how many times will we rettry calling the send_message API
    # (RETRY+1)*(RETRY/2)*WAIT_FACTOR is the maximum waiting time in seconds
    # in case of API problems. for 10 and 0.5 it is 27.5
    WAIT_FACTOR = 0.5

    def __init__(self, config):
        self.config = config
        self.responses = {'main': None,
                          'config_errors': []}

    def send(self, alert_level, alert_text, retry=RETRY):
        """

        :param alert_level:
        :param alert_text:
        :param retry:
        :return:
        """
        try:
            receivers = []
            if alert_level == StandardAlertLevels.it:
                receivers = self.config.it_alert_numbers
            else:
                for level in range(alert_level + 1):
                    level_name = 'level_{}'.format(level)
                    try:
                        level_numbers = self.config.alert_numbers[level_name]
                        receivers.extend(level_numbers)
                    except KeyError:
                        # this happens when alert_numbers[level_X] is not
                        # defined and an alert of level X is generated
                        message = 'No alarm numbers set for level {} alarms'
                        message = message.format(level)

                        # if there was an alert with higher level than the
                        # available alert_numbers levels, we need to warn IT
                        if level > StandardAlertLevels.no_alert:
                            self.send_config_error(message)

                    except TypeError:
                        # this happens when alert_numbers[level_X] is defined
                        # but empty
                        message = 'No alarm numbers set for level {} alarms'
                        message = message.format(level)
                        logging.info(message)

            if not receivers and level != StandardAlertLevels.no_alert:
                message = 'No alarm numbers set for {}'
                message = message.format(alert_text)
                self.send_config_error(message)

            # remove duplicates
            receivers = list(set(receivers))

            response = self._plivio_send(alert_text, receivers, retry)

            logging.debug(response)
            self.responses['main'] = response
            return self.responses

        except Exception as e:
            logging.fatal(e)
            raise FatalError(alert_text)

    def _plivio_send(self, alert_text, receivers, retry=RETRY):
        """
        Sends an SMS using plivo.com

        :param alert_text:
        :param receivers:
        :param retry:
        :return:
        """

        if retry == 0:
            raise APISendError(alert_text, self.RETRY)

        if isinstance(receivers, list):
            receivers = '<'.join(receivers)

        params = {
            'dst': receivers,
            'src': self.config.sender_number,
            'text': alert_text
        }

        logging.debug(params)

        p = plivo.RestAPI(
            self.config.plivio_auth_id, self.config.plivio_auth_token)
        # response = p.send_message(params)
        response = 202, params

        if response[0] != 202:
            retry = retry - 1
            seconds = (self.RETRY - retry) * self.WAIT_FACTOR
            sleep(seconds)
            self._plivio_send(alert_text, receivers, retry)

        return response

    def send_config_error(self, message):
        """

        :param message:
        :return:
        """
        message = '{} - IT problem: {}'.format(
            self.config.app_name, message)
        logging.warn(message)
        responses = MessageSender(self.config).send(
            StandardAlertLevels.it, message)
        self.responses['config_errors'].append(responses['main'])


class APISendError(RuntimeError):
    """
    Error caused to the API not returning success codes
    """
    def __init__(self, message, retry):
        """

        :param message:
        :param retry:
        """
        text = 'After trying {} times I had to give up trying sending "{}"'
        text = text.format(retry, message)

        # Call the base class constructor with the parameters it needs
        super(APISendError, self).__init__(text)
        logging.fatal(message)


class FatalError(RuntimeError):
    """
    Error to signal a major problem that needs to be somehow reported
    """
    def __init__(self, message):
        """

        :param message:
        """
        # Call the base class constructor with the parameters it needs
        super(FatalError, self).__init__(message)
        logging.fatal(message)
