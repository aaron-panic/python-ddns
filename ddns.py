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

import os
import time
import json
import urllib.request
import urllib.error
from config import ConfigParser, ConfigurationError
from logger import Logger


DEFAULT_CONFIG = '/etc/python-ddns/ddns.conf'
DEFAULT_STATE_FILE = '/var/lib/ddns/ip_addr'
DEFAULT_TTL = 300

def fetch_public_ip(log: Logger) -> str:
    log.msg('msg', 'Fetching public IP address...')
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=10) as response:
            return response.read().decode('utf-8').strip()
    except urllib.error.URLError as e:
        log.msg('warn', f'Failed to fetch public IP: {e.reason}')
        return None
    except Exception as e:
        log.msg('warn', f'Unexpected error fetching public IP: {e}')
        return None

def read_cached_ip(log: Logger) -> str:
    if not os.path.exists(DEFAULT_STATE_FILE):
        log.msg('warn', f'State file not found: {DEFAULT_STATE_FILE}')
        return None
    try:
        with open(DEFAULT_STATE_FILE, 'r') as f:
            return f.read().strip()
    except Exception as e:
        log.msg('warn', f'Failed to read state file: {e}')
        return None

def write_cached_ip(ip: str, log: Logger) -> bool:
    try:
        with open(DEFAULT_STATE_FILE, 'w') as f:
            f.write(ip)
        return True
    except Exception as e:
        log.msg('error', f'Failed to write state file: {e}')
        return False

def update_domain(domain: ConfigDomain, ip: str, log: Logger) -> bool:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {domain.api_key}'
    }
    payload = json.dumps({
        'rrset_values': [ip],
        'rrset_ttl': DEFAULT_TTL
    }).encode('utf-8')

    all_succeeded = True

    if not domain.subdomain_only:
        # Placeholder: update root record
        pass

    if domain.subdomains is not None:
        for subdomain in domain.subdomains:
            url = f'https://api.gandi.net/v5/livedns/domains/{domain.tld}/records/{subdomain}/A'
            try:
                request = urllib.request.Request(url, data=payload, headers=headers, method='PUT')
                with urllib.request.urlopen(request) as response:
                    body = response.read().decode('utf-8')
                    if 'DNS Record Created' in body:
                        log.msg('msg', f'Updated {subdomain}.{domain.tld} -> {ip}')
                    else:
                        log.msg('warn', f'Unexpected response for {subdomain}.{domain.tld}: {body}')
                        all_succeeded = False
            except urllib.error.HTTPError as e:
                log.msg('error', f'HTTP error updating {subdomain}.{domain.tld}: {e.code} {e.reason}')
                all_succeeded = False
            except urllib.error.URLError as e:
                log.msg('error', f'URL error updating {subdomain}.{domain.tld}: {e.reason}')
                all_succeeded = False

    return all_succeeded

def main():
    try:
        parser = ConfigParser()
        config = parser.parse(DEFAULT_CONFIG)
    except ConfigurationError as e:
        print(f"[ERR] Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    log = Logger(
        verbosity=config.verbosity,
        error_logfile=config.error_logfile,
        err_tofile=config.error_logfile is not None
    )

    cached_ip = read_cached_ip(log)

    while True:
        current_ip = fetch_public_ip(log)

        if current_ip is not None:
            
            if current_ip is not None:
                if current_ip != cached_ip:
                    log.msg('msg', f'IP address changed: {cached_ip} -> {current_ip}')
                    if write_cached_ip(current_ip, log):
                        cached_ip = current_ip
                        for domain in config.domains:
                            update_domain(domain, current_ip, log)
                    else:
                        # Failure mode placeholder
                        pass
                else:
                    log.msg('msg', current_ip + ': IP address unchanged, nothing to do.')

        time.sleep(config.frequency * 60)

if __name__ == '__main__':
    main()