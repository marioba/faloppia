from unittest import TestCase

from config import Config
from utils.message_sender import MessageSender, FatalError


class TestMessageSender(TestCase):

    def test_send(self):
        config = Config('test_config.yml')
        config.set_fake_api_call(True, 202)
        ms = MessageSender(config)
        ms.WAIT_FACTOR = 0.01
        alert_level = 3
        text = config.alert_text.format('http://berna.io')
        responses = ms.send(alert_level, text)
        expected = {'main': (202, {'src': '+41791234566',
                                   'dst': '+41791234568<+41791234567',
                                   'text': 'Alerta Info: http://berna.io'}),
                    'config_errors': [
                        (202, {'src': '+41791234566', 'dst': '+41791234568',
                               'text': 'FaloppiaWarn - IT problem: No alarm numbers set for level 3 alarms'})]}
        self.assertDictEqual(responses, expected)

    def test_failed_send(self):
        config = Config('test_config.yml')
        config.set_fake_api_call(True, 400)
        ms = MessageSender(config)
        ms.WAIT_FACTOR = 0.01
        with self.assertRaises(FatalError):
            ms.send(1, 'text')

    def test_no_receivers(self):
        config = Config('test_config.yml')
        ms = MessageSender(config)
        with self.assertRaises(FatalError):
            ms._plivio_send('text', receivers=[])
