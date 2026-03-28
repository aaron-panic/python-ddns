# python-ddns.py - Automatically update DNS records with public IP
# Copyright (C) 2026 Aaron Reichenbach <aaron@scavengers.io>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import configparser
import os
import sys

DEFAULT_FREQUENCY = 15
DEFAULT_CONFIG_PATH = '/etc/python-ddns/'
DEFAULT_CONFIG_FILE = 'ddns.conf'
DEFAULT_STATE_PATH  = '/var/lib/python-ddns/'
DEFAULT_LOG_LEVEL   = 'error'
DEFAULT_SUBDOMAIN_ONLY = False
SUPPORTED_PROVIDERS = ['gandi']

class ConfigurationError(Exception):
    pass

class ConfigDomain:
    def __init__(self, config_data: dict = None):
        if config_data is None:
            config_data = {}
        
        self.frequency = config_data.get('frequency')
        self.dns_provider = config_data.get('dns_provider')
        self.tld = config_data.get('tld')
        self.subdomain_only = config_data.get('subdomain_only')
        self.subdomains = config_data.get('subdomains')
        self.credential_file = config_data.get('credential_file')
        self.api_key = None

        if self.dns_provider is None:
            raise ConfigurationError('DNS Provider not configured.')
        if self.dns_provider not in SUPPORTED_PROVIDERS:
            raise ConfigurationError('DNS Provider not supported.')
        if not self.tld:
            raise ConfigurationError('No TLD specified.')
        
        if self.subdomain_only is None:
            print(f"Warning: subdomain_only not set, defaulting to {DEFAULT_SUBDOMAIN_ONLY}", file=sys.stderr)
            self.subdomain_only = DEFAULT_SUBDOMAIN_ONLY

class ConfigDDNS:
    def __init__(self, config_data: dict = None):
        if config_data is None:
            config_data = {}

        if 'frequency' not in config_data:
            print(f"Warning: frequency not set, defaulting to {DEFAULT_FREQUENCY}", file=sys.stderr)
        self.frequency = config_data.get('frequency', DEFAULT_FREQUENCY)

        if 'config_path' not in config_data:
            print(f"Warning: config_path not set, defaulting to {DEFAULT_CONFIG_PATH}", file=sys.stderr)
        self.config_path = config_data.get('config_path', DEFAULT_CONFIG_PATH)

        if 'config_file' not in config_data:
            print(f"Warning: config_file not set, defaulting to {DEFAULT_CONFIG_FILE}", file=sys.stderr)
        self.config_file = config_data.get('config_file', DEFAULT_CONFIG_FILE)

        if 'state_path' not in config_data:
            print(f"Warning: state_path not set, defaulting to {DEFAULT_STATE_PATH}", file=sys.stderr)
        self.state_path = config_data.get('state_path', DEFAULT_STATE_PATH)

        if 'verbosity' not in config_data:
            print(f"Warning: verbosity not set, defaulting to {DEFAULT_LOG_LEVEL}", file=sys.stderr)
        self.verbosity = config_data.get('verbosity', DEFAULT_LOG_LEVEL)

        self.error_logfile   = config_data.get('error_logfile')
        self.runtime_logfile = config_data.get('runtime_logfile')
        self.domains = []


class ConfigParser:
    def parse(self, filename: str) -> ConfigDDNS:
        if not os.path.isabs(filename):
            raise ConfigurationError(f"Config path must be absolute, got: {filename}")
        if not os.access(filename, os.R_OK):
            raise ConfigurationError(f"Cannot read configuration file: {filename}")

        with open(filename, 'r') as f:
            lines = f.readlines()

        service_data = {}
        logging_data = {}
        domains      = []

        current_section = None
        current_domain  = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1].lower()
                if section == 'domain':
                    if current_domain is not None:
                        domains.append(ConfigDomain(current_domain))
                    current_domain = {}
                    current_section = 'domain'
                else:
                    current_section = section
                continue

            if '=' not in line:
                continue

            key, _, value = line.partition('=')
            key   = key.strip().lower()
            value = value.strip()

            if current_section == 'service':
                if key == 'frequency':
                    try:
                        service_data['frequency'] = int(value)
                    except ValueError:
                        raise ConfigurationError(f"[Service] frequency must be an integer, got: {value}")
                elif key == 'state':
                    if not os.path.isabs(value):
                        raise ConfigurationError(f"[Service] state must be an absolute path, got: {value}")
                    if not os.path.isdir(value):
                        raise ConfigurationError(f"[Service] state directory does not exist: {value}")
                    if not os.access(value, os.W_OK):
                        raise ConfigurationError(f"[Service] state directory is not writable: {value}")
                    service_data['state_path'] = value

            elif current_section == 'logging':
                if key == 'verbosity':
                    if value not in ['error', 'warn', 'all']:
                        raise ConfigurationError(f"[Logging] verbosity must be error, warn, or all, got: {value}")
                    logging_data['verbosity'] = value
                elif key == 'error_logfile':
                    if os.path.isdir(value):
                        raise ConfigurationError(f"[Logging] error_logfile is a directory: {value}")
                    if not os.access(os.path.dirname(value), os.W_OK):
                        raise ConfigurationError(f"[Logging] error_logfile parent directory is not writable: {value}")
                    logging_data['error_logfile'] = value
                elif key == 'runtime_logfile':
                    if os.path.isdir(value):
                        raise ConfigurationError(f"[Logging] runtime_logfile is a directory: {value}")
                    if not os.access(os.path.dirname(value), os.W_OK):
                        raise ConfigurationError(f"[Logging] runtime_logfile parent directory is not writable: {value}")
                    logging_data['runtime_logfile'] = value

            elif current_section == 'domain':
                if key == 'frequency':
                    try:
                        current_domain['frequency'] = int(value)
                    except ValueError:
                        raise ConfigurationError(f"[Domain] frequency must be an integer, got: {value}")
                elif key == 'tld':
                    current_domain['tld'] = value
                elif key == 'dns_provider':
                    current_domain['dns_provider'] = value
                elif key == 'subdomains':
                    stripped = [s.strip() for s in value.split(',')]
                    current_domain['subdomains'] = None if stripped == [''] else stripped
                elif key == 'subdomain_only':
                    if value.lower() not in ['true', 'false']:
                        raise ConfigurationError(f"[Domain] subdomain_only must be true or false, got: {value}")
                    current_domain['subdomain_only'] = value.lower() == 'true'
                elif key == 'credentials':
                    if value == '':
                        pass
                    elif os.path.isabs(value):
                        current_domain['credential_file'] = value
                    elif os.path.dirname(value) != '':
                        raise ConfigurationError(f"[Domain] credentials subdirectory paths are not supported, got: {value}")
                    else:
                        current_domain['credential_file'] = value

        if current_domain is not None:
            domains.append(ConfigDomain(current_domain))

        if not domains:
            raise ConfigurationError("No [Domain] sections found in configuration.")

        config = ConfigDDNS({**service_data, **logging_data})

        config_dir = os.path.dirname(filename)
        for domain in domains:
            if domain.credential_file is None:
                domain.credential_file = os.path.join(config_dir, f"{domain.tld}.conf")
            elif not os.path.isabs(domain.credential_file):
                domain.credential_file = os.path.join(config_dir, domain.credential_file)
            if not os.path.exists(domain.credential_file):
                raise ConfigurationError(f"[Domain] credentials file does not exist: {domain.credential_file}")
            if not os.access(domain.credential_file, os.R_OK):
                raise ConfigurationError(f"[Domain] credentials file is not readable: {domain.credential_file}")
            domain.api_key = self.load_api_key(domain.credential_file)

        config.domains = domains
        return config

    def load_api_key(self, credential_file: str) -> str:
        with open(credential_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('dns_gandi_token'):
                    _, _, value = line.partition('=')
                    token = value.strip().split()[0]
                    if not token:
                        raise ConfigurationError(f"dns_gandi_token is empty in: {credential_file}")
                    return token
        raise ConfigurationError(f"dns_gandi_token not found in: {credential_file}")