import pytest
from loguru import logger


@pytest.fixture(autouse=True)
def propagate_logs(request):
    """Propagate Loguru logs to standard logging handlers used by Pytest."""
    plugin = request.config.pluginmanager.getplugin("logging-plugin")

    # Remove all existing Loguru handlers, including the default one.
    logger.remove()

    handler_ids = []

    for handler in [plugin.caplog_handler, plugin.log_cli_handler, plugin.report_handler]:
        # Note that, by default, all log levels are propagated to standard handlers.
        # You can adjust the `level` here, modify the handler's level, or use `caplog.set_level()`.
        handler_id = logger.add(handler, format="{message}", level=0)
        handler_ids.append(handler_id)

    yield

    for handler_id in handler_ids:
        logger.remove(handler_id)
