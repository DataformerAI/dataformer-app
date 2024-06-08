import asyncio
import logging
import signal

from gunicorn import glogging  # type: ignore
from gunicorn.app.base import BaseApplication  # type: ignore
from uvicorn.workers import UvicornWorker

from dfapp.utils.logger import InterceptHandler  # type: ignore


class DataformerAppUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio"}

    def _install_sigint_handler(self) -> None:
        """Install a SIGQUIT handler on workers.

        - https://github.com/encode/uvicorn/issues/1116
        - https://github.com/benoitc/gunicorn/issues/2604
        """

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_exit, signal.SIGINT, None)

    async def _serve(self) -> None:
        # We do this to not log the "Worker (pid:XXXXX) was sent SIGINT"
        self._install_sigint_handler()
        await super()._serve()


class Logger(glogging.Logger):
    """Implements and overrides the gunicorn logging interface.

    This class inherits from the standard gunicorn logger and overrides it by
    replacing the handlers with `InterceptHandler` in order to route the
    gunicorn logs to loguru.
    """

    def __init__(self, cfg):
        super().__init__(cfg)
        logging.getLogger("gunicorn.error").handlers = [InterceptHandler()]
        logging.getLogger("gunicorn.access").handlers = [InterceptHandler()]


class DataformerAppApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}

        self.options["worker_class"] = "dfapp.server.DataformerAppUvicornWorker"
        self.options["logger_class"] = Logger
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
