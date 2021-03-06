from unittest import TestCase

from app.config import Config
from app.utils.message_sender import MessageSender, FatalError


class TestMessageSender(TestCase):

    def test_send(self):
        config = Config(config_file='test_config.yml')
        config.set_fake_api_call(True, 202)
        ms = MessageSender(config)
        ms.WAIT_FACTOR = 0.01
        alert_level = 2
        text = 'strong rains coming'
        responses = ms.send_alert(alert_level, text)
        expected = {
            'main': (
                202,
                {'dst': '+41791234567<+41791234568',
                 'text': 'faloppia.opengis.ch - ALLARME, strong rains coming',
                 'src': '+41791234566'}),
            'config_errors': [(
                202,
                {'dst': '+41791234568',
                 'text': 'faloppia.opengis.ch - IT Problem, No alarm numbers set for level 2 alarms',
                 'src': '+41791234566'})]}

        self.assertDictEqual(responses, expected)

    def test_send_wrong_alert_level(self):
        config = Config(config_file='test_config.yml')
        config.set_fake_api_call(True, 202)
        ms = MessageSender(config)
        ms.WAIT_FACTOR = 0.01
        alert_level = 3
        with self.assertRaises(KeyError):
            # alert level 3 does not exist in our config
            config.alert_text['level_%s' % alert_level]

        text = 'strong rains coming'
        responses = ms.send_alert(alert_level, text)
        expected = {'config_errors': [(202, {'src': '+41791234566',
                                             'text': 'faloppia.opengis.ch - IT Problem, No alarm numbers set for level 2 alarms',
                                             'dst': '+41791234568'}), (202, {
            'src': '+41791234566',
            'text': 'faloppia.opengis.ch - IT Problem, No alarm numbers or text set for level 3 alarms',
            'dst': '+41791234568'})], 'main': (202, {'src': '+41791234566',
                                                     'text': 'faloppia.opengis.ch - ALLARME, strong rains coming',
                                                     'dst': '+41791234567<+41791234568'})}

        print(responses)
        self.assertDictEqual(responses, expected)

    def test_failed_send(self):
        config = Config(config_file='test_config.yml')
        config.set_fake_api_call(True, 400)
        ms = MessageSender(config)
        ms.WAIT_FACTOR = 0.01
        with self.assertRaises(FatalError):
            ms.send_alert(1, 'text')

    def test_no_receivers(self):
        config = Config(config_file='test_config.yml')
        ms = MessageSender(config)
        with self.assertRaises(FatalError):
            ms._plivo_send('text', receivers=[])
