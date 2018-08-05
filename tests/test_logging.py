import logging
import structlog
import os


logging.basicConfig(format='%(message)s')
print(os.getenv("LOG_LEVEL", "INFO").upper())



if os.getenv("LOG_MODE", "PROD").upper() == 'LOCAL':
	chain = [
		structlog.stdlib.add_log_level,
		structlog.stdlib.add_logger_name,
		structlog.stdlib.PositionalArgumentsFormatter(),
		structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
		structlog.processors.StackInfoRenderer(),
		structlog.processors.format_exc_info,
		structlog.dev.ConsoleRenderer()
	]
else:
	chain = [
		structlog.stdlib.filter_by_level,
		structlog.stdlib.add_logger_name,
		structlog.stdlib.add_log_level,
		structlog.stdlib.PositionalArgumentsFormatter(),
		structlog.processors.TimeStamper(fmt="iso"),
		structlog.processors.StackInfoRenderer(),
		structlog.processors.format_exc_info,
		structlog.processors.UnicodeDecoder(),
		structlog.processors.JSONRenderer()
	]


structlog.configure(
	processors=chain,
	context_class=dict,
	logger_factory=structlog.stdlib.LoggerFactory(),
	wrapper_class=structlog.stdlib.BoundLogger,
	cache_logger_on_first_use=True,
    )


log = structlog.getLogger()


level_env = os.getenv("LOG_LEVEL", "INFO").upper()
log_levels = {"CRITICAL" : logging.CRITICAL, "ERROR" : logging.ERROR, "WARNING" : logging.WARNING, "INFO" : logging.INFO, "DEBUG" : logging.DEBUG}
log.setLevel(log_levels[level_env])

log.critical("critical message")
log.warning("warning message")
log.info("info message")
