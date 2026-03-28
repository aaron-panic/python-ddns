import unittest
import os
import tempfile
from config import ConfigParser, ConfigurationError, DEFAULT_LOG_LEVEL, DEFAULT_FREQUENCY, DEFAULT_STATE_PATH

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'tests')

class TestServiceFrequency(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_frequency_not_an_integer_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('service_frequency_not_integer.conf')

    def test_frequency_not_set_defaults_to_default_frequency(self):
        config = self.parse('service_frequency_not_set.conf')
        self.assertEqual(config.frequency, DEFAULT_FREQUENCY)

    def test_frequency_empty_value_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('service_frequency_empty.conf')

    def test_frequency_set_correctly(self):
        config = self.parse('service_frequency_set.conf')
        self.assertEqual(config.frequency, 25)

class TestServiceStatePath(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_state_path_not_set_defaults_to_default(self):
        config = self.parse('service_state_default.conf')
        self.assertEqual(config.state_path, DEFAULT_STATE_PATH)

    def test_state_path_exists_and_writable(self):
        config = self.parse('service_state_valid.conf')
        self.assertEqual(config.state_path, '/var/lib/python-ddns/')

    def test_state_path_not_exists_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('service_state_not_exists.conf')

    def test_state_path_not_writable_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('service_state_not_writable.conf')

class TestLoggingVerbosity(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_verbosity_not_set_defaults_to_error(self):
        config = self.parse('logging_verbosity_default.conf')
        self.assertEqual(config.verbosity, DEFAULT_LOG_LEVEL)

    def test_verbosity_set_to_error(self):
        config = self.parse('logging_verbosity_error.conf')
        self.assertEqual(config.verbosity, 'error')

    def test_verbosity_set_to_warn(self):
        config = self.parse('logging_verbosity_warn.conf')
        self.assertEqual(config.verbosity, 'warn')

    def test_verbosity_set_to_all(self):
        config = self.parse('logging_verbosity_all.conf')
        self.assertEqual(config.verbosity, 'all')

    def test_verbosity_invalid_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('logging_verbosity_invalid.conf')

class TestLoggingLogfiles(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_error_logfile_not_set_is_none(self):
        config = self.parse('logging_logfile_default.conf')
        self.assertIsNone(config.error_logfile)

    def test_runtime_logfile_not_set_is_none(self):
        config = self.parse('logging_logfile_default.conf')
        self.assertIsNone(config.runtime_logfile)

    def test_error_logfile_set_correctly(self):
        config = self.parse('logging_error_logfile_valid.conf')
        self.assertEqual(config.error_logfile, '/var/log/ddns/python-ddns.error.log')

    def test_runtime_logfile_set_correctly(self):
        config = self.parse('logging_runtime_logfile_valid.conf')
        self.assertEqual(config.runtime_logfile, '/var/log/ddns/python-ddns.runtime.log')

    def test_error_logfile_is_directory_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('logging_error_logfile_is_dir.conf')

    def test_error_logfile_not_writable_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('logging_error_logfile_not_writable.conf')

    def test_runtime_logfile_is_directory_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('logging_runtime_logfile_is_dir.conf')

    def test_runtime_logfile_not_writable_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('logging_runtime_logfile_not_writable.conf')

class TestDomainFrequency(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_domain_frequency_not_set_is_none(self):
        config = self.parse('domain_frequency_not_set.conf')
        self.assertIsNone(config.domains[0].frequency)

    def test_domain_frequency_set_correctly(self):
        config = self.parse('domain_frequency_set.conf')
        self.assertEqual(config.domains[0].frequency, 25)

    def test_domain_frequency_not_integer_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_frequency_not_integer.conf')

    def test_domain_frequency_empty(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_frequency_empty.conf')
        
class TestDomainDnsProvider(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_dns_provider_gandi_valid(self):
        config = self.parse('domain_dns_provider_gandi.conf')
        self.assertEqual(config.domains[0].dns_provider, 'gandi')

    def test_dns_provider_unsupported_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_dns_provider_unsupported.conf')

    def test_dns_provider_not_set_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_dns_provider_not_set.conf')

    def test_dns_provider_not_set_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_dns_provider_empty.conf')

class TestDomainTld(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_tld_set_correctly(self):
        config = self.parse('domain_tld_set.conf')
        self.assertEqual(config.domains[0].tld, 'test.com')

    def test_tld_not_set_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_tld_not_set.conf')

    def test_tld_empty_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_tld_empty.conf')

class TestDomainSubdomainOnly(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_subdomain_only_not_set_defaults_false(self):
        config = self.parse('domain_subdomain_only_not_set.conf')
        self.assertFalse(config.domains[0].subdomain_only)

    def test_subdomain_only_set_false(self):
        config = self.parse('domain_subdomain_only_false.conf')
        self.assertFalse(config.domains[0].subdomain_only)

    def test_subdomain_only_set_true(self):
        config = self.parse('domain_subdomain_only_true.conf')
        self.assertTrue(config.domains[0].subdomain_only)

    def test_subdomain_only_invalid_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_subdomain_only_invalid.conf')

    def test_subdomain_only_empty_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_subdomain_only_empty.conf')

class TestDomainSubdomains(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_subdomains_not_set_is_none(self):
        config = self.parse('domain_subdomains_not_set.conf')
        self.assertIsNone(config.domains[0].subdomains)

    def test_subdomains_empty_is_none(self):
        config = self.parse('domain_subdomains_empty.conf')
        self.assertIsNone(config.domains[0].subdomains)

    def test_subdomains_comma_delineated(self):
        config = self.parse('domain_subdomains_commas.conf')
        self.assertEqual(config.domains[0].subdomains, ['www', 'mail', 'vpn'])

    def test_subdomains_comma_delineated_whitespace(self):
        config = self.parse('domain_subdomains_whitespace.conf')
        self.assertEqual(config.domains[0].subdomains, ['www', 'mail', 'vpn'])

class TestDomainCredentials(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_credentials_not_set_defaults_to_config_dir(self):
        config = self.parse('domain_credentials_not_set.conf')
        self.assertEqual(config.domains[0].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

    def test_credentials_empty_defaults_to_config_dir(self):
        config = self.parse('domain_credentials_empty.conf')
        self.assertEqual(config.domains[0].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

    def test_credentials_bare_filename_resolves_to_config_dir(self):
        config = self.parse('domain_credentials_bare.conf')
        self.assertEqual(config.domains[0].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

    def test_credentials_absolute_path(self):
        config = self.parse('domain_credentials_absolute.conf')
        self.assertEqual(config.domains[0].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

    def test_credentials_subdir_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_credentials_subdir.conf')

    def test_credentials_file_not_exists_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_credentials_not_exists.conf')

    def test_credentials_file_not_readable_raises_error(self):
        with self.assertRaises(ConfigurationError):
            self.parse('domain_credentials_not_readable.conf')

class TestMultipleDomains(unittest.TestCase):

    def parse(self, filename: str):
        parser = ConfigParser()
        return parser.parse(os.path.join(FIXTURE_DIR, filename))

    def test_two_domains_count(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(len(config.domains), 2)

    def test_two_domains_first_tld(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[0].tld, 'test.com')

    def test_two_domains_second_tld(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[1].tld, 'scavengers.io')

    def test_two_domains_first_frequency(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[0].frequency, 20)

    def test_two_domains_second_frequency(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[1].frequency, 30)

    def test_two_domains_first_subdomains(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[0].subdomains, ['www', 'mail'])

    def test_two_domains_second_subdomains(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[1].subdomains, ['vpn', 'git', 'cloud'])

    def test_two_domains_first_subdomain_only(self):
        config = self.parse('multi_domain.conf')
        self.assertFalse(config.domains[0].subdomain_only)

    def test_two_domains_second_subdomain_only(self):
        config = self.parse('multi_domain.conf')
        self.assertTrue(config.domains[1].subdomain_only)

    def test_two_domains_first_credentials(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[0].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

    def test_two_domains_second_credentials(self):
        config = self.parse('multi_domain.conf')
        self.assertEqual(config.domains[1].credential_file, '/home/ravscav/dev/python-ddns/tests/test.com.conf')

if __name__ == '__main__':
    unittest.main()