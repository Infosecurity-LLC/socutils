import unittest

@unittest.skip
class SettingTestCase(unittest.TestCase):
    settings_dict = {
        'setting_one': 1,
        'setting_two': '2',
        'some_stuff': ['hey', 'ho'],
        'another_one': {'b': 'c', 'd': ['tic', 'tac']}
    }

    def test_get_settings(self):
        # self.assertRaises(SettingsFileNotExistError, socutils.get_settings, 'test_data/settings.yml')
        settings = socutils.get_settings('../test_data/settings.yml')
        self.assertEqual(settings, self.settings_dict)


    def test_get_parent_settings(self):
        pass


    def test_get_parent_settings_bad_cwd(self):
        pass

    """
        Add tests with different paths and cwds
    """


if __name__ == '__main__':
    unittest.main()