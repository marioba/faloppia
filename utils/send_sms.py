import logging
import plivo

from utils import StandardAlertLevels


class MessageSender(object):
    def __init__(self, config):
        self.config = config

    def send(self, alert_level, alert_text):
        p = plivo.RestAPI(
            self.config.plivio_auth_id, self.config.plivio_auth_token)

        destinations = ''
        if alert_level == StandardAlertLevels.it:
            destinations += '<'.join(self.config.it_alert_numbers)
        else:
            for level in range(alert_level + 1):
                level_name = 'level_{}'.format(level)
                try:
                    level_numbers = self.config.alert_numbers[level_name]
                    destinations += '<'.join(level_numbers)
                except KeyError:
                    # this happens when alert_numbers[level_X] is not defined
                    # and an for an alert of level X is generated
                    message = '{} - IT problem: No alarm numbers set for '\
                              'level {} alarms'
                    message = message.format(self.config.app_name, level)
                    # if there was an alert with higher level than the
                    # available alert_numbers levels, we need to warn IT
                    logging.warn(message)
                    if level > StandardAlertLevels.no_alert:
                        self.send(StandardAlertLevels.it, message)
                except TypeError:
                    # this happens when alert_numbers[level_X] is defined
                    # but empty
                    message = 'No alarm numbers set for level {} alarms'
                    message = message.format(level)
                    logging.info(message)

        if destinations == '':
            if level > StandardAlertLevels.no_alert:
                message = '{} - IT problem: No alarm numbers set for {}'
                message = message.format(self.config.app_name, alert_text)
                self.send(StandardAlertLevels.it, message)

        params = {
            'dst': destinations,
            'src': self.config.sender_number,
            'text': alert_text
        }
        logging.debug(params)
        # response = p.send_message(params)
        response = "SENDING DISABLED in send_sms.py"
        logging.debug(response)
        return params, response
