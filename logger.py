import sys
from datetime import datetime

VALID_VERBOSITY = ['error', 'warn', 'all']

class Logger:
    def __init__(self,
                 verbosity: str = 'error',
                 error_logfile: str = None,
                 runtime_logfile: str = None,
                 err_tofile: bool = False,
                 warn_tofile: bool = False,
                 msg_tofile: bool = False,
                 always_flush: bool = False):

        self.verbosity      = verbosity if verbosity in VALID_VERBOSITY else 'error'
        self.err_tofile     = err_tofile
        self.warn_tofile    = warn_tofile
        self.msg_tofile     = msg_tofile
        self.always_flush   = always_flush

        self.error_logfile   = open(error_logfile, 'w') if error_logfile else None
        self.runtime_logfile = open(runtime_logfile, 'w') if runtime_logfile else None

    def _timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def msg(self, level: str, message: str):
        level = level.lower()

        if level == 'error':
            print(f"[ERR] {message}", file=sys.stderr)
            if self.err_tofile and self.error_logfile:
                self.error_logfile.write(f"[ERR] [{self._timestamp()}] {message}\n")
                self.error_logfile.flush()

        elif level == 'warn':
            if self.verbosity not in ['warn', 'all']:
                return
            print(f"[WRN] {message}", file=sys.stderr)
            if self.warn_tofile and self.runtime_logfile:
                self.runtime_logfile.write(f"[WRN] [{self._timestamp()}] {message}\n")
                if self.always_flush:
                    self.runtime_logfile.flush()

        elif level == 'msg':
            if self.verbosity != 'all':
                return
            print(f"[MSG] {message}", file=sys.stdout)
            if self.msg_tofile and self.runtime_logfile:
                self.runtime_logfile.write(f"[MSG] [{self._timestamp()}] {message}\n")
                if self.always_flush:
                    self.runtime_logfile.flush()

    def __del__(self):
        if self.error_logfile:
            self.error_logfile.close()
        if self.runtime_logfile:
            self.runtime_logfile.close()