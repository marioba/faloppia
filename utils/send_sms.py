import logging
import plivo

from utils import StandardAlertLevels
from utils import FatalError


class MessageSender(object):
    RETRY = 10  # how many times will we rettry calling the send_message API

    def __init__(self, config):
        self.config = config

    def send(self, alert_level, alert_text, retry=RETRY):
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

            response = self._plivio_send(
                alert_text, self.config.sender_number, receivers, retry)

            logging.debug(response)
            return response

        except Exception as e:
            logging.fatal(e)
            raise FatalError(alert_text)

    def _plivio_send(self, alert_text, sender, receivers, retry=RETRY):
        """
        this sends an SMS using plivo.com
        :param alert_text:
        :param sender:
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
            'src': sender,
            'text': alert_text
        }

        logging.debug(params)

        p = plivo.RestAPI(
            self.config.plivio_auth_id, self.config.plivio_auth_token)
        #response = p.send_message(params)
        response = "SENDING DISABLED in send_sms.py"

        if response[0] != 202:
            retry = retry - 1
            self._plivio_send(alert_text, sender, receivers, retry)

        return response

    def send_config_error(self, message):
            message = '{} - IT problem: {}'.format(
                self.config.app_name, message)
            response = MessageSender(self.config).send(
                StandardAlertLevels.it, message)
            logging.warn(message)


class APISendError(RuntimeError):
    def __init__(self, message, retry):
        text = 'After trying {} times I had to give up trying sending {}'
        text = text.format(retry, message)

        # Call the base class constructor with the parameters it needs
        super(APISendError, self).__init__(text)
        logging.fatal(message)
