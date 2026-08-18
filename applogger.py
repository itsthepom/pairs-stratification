###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Activity log
###############################################################################
import io
import os
import logging

global applog

class applogger:
    def __init__(self, name: str = __name__, level: int = logging.INFO):
        global applog
        self._logger = logging.getLogger(name)

        # Basic setup if no handlers exist yet
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

            # Define a specific path for the log file
            log_dir = os.path.expanduser("~/stratlogs")
            os.makedirs(log_dir, exist_ok=True)
            filehandler = logging.FileHandler(os.path.join(log_dir, "stratlog.log"), mode="a", encoding="utf-8")
            filehandler.setFormatter(formatter)
            self._logger.addHandler(filehandler)

            self._logger.setLevel(level)
        applog = self

    def __getattr__(self, name: str):
        """Delegate missing calls directly to the underlying logger."""
        return getattr(self._logger, name)
