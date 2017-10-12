from unittest import TestCase

from config import Config


class TestConfig(TestCase):
    def test___init__(self):
        mandatory_keys = [
            'alert_numbers',
            'alert_text',
            'app_name',
            'it_alert_numbers',
            'log_level',
            'plivio_auth_id',
            'plivio_auth_token',
            'sender_number'
        ]
        c = Config()
        for key in mandatory_keys:
            self.assertTrue(hasattr(c, key), '{} is not in config'.format(key))

    def test___setattr__(self):
        c = Config()
        with self.assertRaises(AttributeError):
            c.sender_number = 123456789
        with self.assertRaises(AttributeError):
            c.new_attr = 123456789
