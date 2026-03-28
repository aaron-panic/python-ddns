# python-ddns

A lightweight DDNS (Dynamic DNS) updater service written in Python. Monitors your public IP address and automatically updates DNS records when it changes, avoiding unnecessary API calls by only contacting your DNS provider when an actual change is detected.

Currently supports Gandi LiveDNS only. If you would like support added for another DNS provider, email aaron@scavengers.io with the provider's API details and I will look at adding it.

## License

GNU Affero General Public License v3.0 (AGPL-3.0). See LICENSE for details.

## Requirements

- Python 3.11+
- A Gandi account with LiveDNS enabled
- systemd

## Installation

TODO: Installation instructions and default configuration file pending.

## Configuration

Configuration is split across several files:

### /etc/python-ddns/python-ddns.conf

The main configuration file. A default configuration file will be provided in a future release.

**[Service]**
- `frequency` — How often to check for IP changes, in minutes. Default: 15.
- `state` — Path to the state directory. Default: `/var/lib/ddns/`.

**[Logging]**
- `verbosity` — Log level. Accepted values: `error`, `warn`, `all`. Default: `error`.
- `error_logfile` — Path to error log file. Optional, defaults to stderr only.
- `runtime_logfile` — Path to runtime log file. Optional, defaults to stdout only.

**[Domain]**
Multiple `[Domain]` blocks are supported, one per domain.
- `tld` — The top level domain to manage. Required.
- `dns_provider` — DNS provider. Currently only `gandi` is supported. Required.
- `subdomains` — Comma separated list of subdomains to update. Optional.
- `subdomain_only` — If `true`, only update subdomains, not the root record. Default: `false`.
- `frequency` — Override global frequency for this domain. Optional.
- `credentials` — Path to credentials file. Defaults to `/etc/python-ddns/<tld>.conf`.

### /etc/python-ddns/\<tld\>.conf

Per-domain credentials file, compatible with certbot dns-gandi authentication credentials for dual use with SSL certificate renewal.
```
dns_gandi_token = YOUR_API_TOKEN
```

## Service Management

Enable and start the service:
```bash
systemctl enable --now python-ddns
```

Check service status:
```bash
systemctl status python-ddns
```

View logs:
```bash
journalctl -u python-ddns -f
```

## Contributing

Pull requests welcome. If you want to add support for a DNS provider, email aaron@scavengers.io with the provider API details first so we can discuss the implementation.