import logging
import plivo

from time import sleep

from app.utils.utils import StandardAlertLevels, remove_duplicates
from app.utils.utils import ApiStatuses


class MessageSender(object):
    """
    Class used to send alerts to users
    """
    RETRY = 10  # how many times will we retry calling the send_message API
    # (RETRY+1)*(RETRY/2)*WAIT_FACTOR is the maximum waiting time in seconds
    # in case of API problems. for 10 and 0.25 it is 13.75
    WAIT_FACTOR = 0.25

    def __init__(self, config):
        self.config = config
        self.responses = {'main': None,
                          'config_errors': []}

    def send_alert(self, alert_level, detail_text, retry=RETRY):
        """

        :param alert_level:
        :param detail_text:
        :param retry:
        :return:
        """

        receivers = []
        alert_text = detail_text
        try:
            if alert_level == StandardAlertLevels.it:
                alert_text = self.config.alert_text[
                    'level_{}'.format(StandardAlertLevels.it)]
                alert_text = alert_text.format(detail_text)
                receivers = self.config.it_alert_numbers
            else:
                for level in range(alert_level + 1):
                    level_name = 'level_{}'.format(level)
                    try:
                        alert_text = self.config.alert_text[level_name]
                        alert_text = alert_text.format(detail_text)
                        level_numbers = self.config.alert_numbers[level_name]
                        receivers.extend(level_numbers)
                    except KeyError:
                        # this happens when alert_numbers[level_X] or
                        # alert_text[level_X] are not
                        # defined and an alert of level X is generated
                        message = 'No alarm numbers or text set for level {}' \
                                  ' alarms'
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
                        if level > StandardAlertLevels.no_alert:
                            self.send_config_error(message)

            # remove duplicates
            receivers = remove_duplicates(receivers)

            if receivers:
                response = self._plivo_send(alert_text, receivers, retry)
                self.responses['main'] = response
            else:
                if alert_level != StandardAlertLevels.no_alert:
                    message = 'No alarm numbers set for {}'
                    message = message.format(alert_text)
                    self.send_config_error(message)

            logging.debug(self.responses)
            return self.responses

        except Exception as e:
            alert_text = 'Fatal Error: {}'.format(str(e))
            raise FatalError(alert_text) from e

    def _plivo_send(self, text, receivers, retry=RETRY):
        """
        Sends an SMS using plivo.com

        :param text:
        :param receivers:
        :param retry:
        :return:
        """

        if retry == 0:
            raise APISendError(text, self.RETRY)

        if not receivers:
            raise FatalError('No receivers were passed')

        if isinstance(receivers, list):
            receivers = '<'.join(receivers)
        if retry == self.RETRY:
            # add the prefix only the first time
            text = '{} - {}'.format(self.config.app_name, text)

        params = {
            'dst': receivers,
            'src': self.config.sender_number,
            'text': text
        }

        logging.debug('Creating request with: {}'.format(params))

        if self.config.fake_api:
            response = self.config.fake_api_return, params
            logging.debug('FAKE SMS response created with {}'.format(response))
        else:
            p = plivo.RestAPI(
                self.config.plivo_auth_id, self.config.plivo_auth_token)
            response = p.send_message(params)

        if response[0] not in ApiStatuses.ok:
            retry = retry - 1
            seconds = (self.RETRY - retry) * self.WAIT_FACTOR
            sleep(seconds)
            self._plivo_send(text, receivers, retry)

        return response

    def send_config_error(self, message):
        """

        :param message:
        :return:
        """
        message = self.config.alert_text[
            'level_{}'.format(StandardAlertLevels.it)].format(message)
        logging.warning(message)
        responses = self.send_alert(StandardAlertLevels.it, message)
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
        super().__init__(text)
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
        super().__init__(message)
        logging.fatal(message)

