# python-ddns TODO

## Configuration
- Move domain blocks into their own files, conf.d pattern, with credentials attached — removes chicken-and-egg logger problem on config load
- Configurable TTL per domain
- SMTP credentials and email alerting on failure/crash
- Default configuration file for new installs

## Logger
- `always_flush` as a config option rather than programmatic only
- SMTP email integration for failure screaming
- Logger initialized before config so config warnings/errors go through it properly

## Service Behaviour
- Boot retry loop for initial IP fetch rather than waiting a full frequency cycle
- Root record updates when `subdomain_only=false` (placeholder exists in code)
- Failure mode handling when `write_cached_ip()` returns false
- Restart behaviour and failure notification via systemd

## DNS Providers
- Additional provider support beyond Gandi

## Installation
- Default configuration file
- Full installation instructions in README

## Testing
- Tests were written against hardcoded paths on your machine — needs cleanup before this is useful to anyone else
- Permission-based test fixtures (unreadable files, unwritable directories) are currently owned by you to allow git push — need a setup/teardown mechanism that creates and destroys these fixtures with the correct permissions programmatically so the test suite is portable and self-contained without manual `chmod` and `chown` steps outside the repo
- `unittest` `setUpClass` and `tearDownClass` are the correct mechanism for this