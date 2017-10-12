from unittest import TestCase

from config import Config
from utils.message_sender import MessageSender, FatalError


class TestMessageSender(TestCase):
    CONFIG = Config('test_config.yml')

    def test_send(self):
        self.CONFIG.set_fake_api_call(True, 202)
        text = self.CONFIG.alert_text.format('http://berna.io')
        alert_level = 3
        responses = MessageSender(self.CONFIG).send(alert_level, text)
        expected = {'main': (202, {'src': '+41791234566',
                                   'dst': '+41791234569<+41791234568<+41791234567',
                                   'text': 'Alerta Info: http://berna.io'}),
                    'config_errors': [
                        (202, {'src': '+41791234566', 'dst': '+41791234568',
                               'text': 'FaloppiaWarn - IT problem: No alarm numbers set for level 3 alarms'})]}
        self.assertDictEqual(responses, expected)

    def test_failed_send(self):
        self.CONFIG.set_fake_api_call(True, 400)
        ms = MessageSender(self.CONFIG)
        ms.WAIT_FACTOR = 0.01
        with self.assertRaises(FatalError):
            ms.send(1, 'text')
