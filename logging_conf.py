conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'isAccessLog': {
            '()': 'CustomLogFilter.AccessLogFilter'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'consoleHandler',
            'logFileHandler',
            'AccessLogFileHandler',
            'AccessLogTCPHandler',
            # 'AccessLogHttpHandler',
            # 'AccessLogSysLogHandler',
        ]
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'consoleFormatter',
            'stream': 'ext://sys.stdout'
        },
        'logFileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'logFileFormatter',
            'filename': './log/wowhoneypot.log',
            'when': 'MIDNIGHT',
            'backupCount': 10,
            'encoding': 'utf-8'
        },
        'AccessLogFileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'AccessLogFileFormatter',
            'filename': './log/access.log',
            'when': 'MIDNIGHT',
            'backupCount': 10,
            'encoding': 'utf-8',
            'filters': [
                'isAccessLog'
            ]
        },
        'AccessLogTCPHandler': {
            'class': 'logging.handlers.SocketHandler',
            'level': 'INFO',
            'formatter': 'AccessLogFileFormatter',
            'host': '127.0.0.1',
            'port': '8888',
            'filters': [
                'isAccessLog'
            ]
        },
        # 'AccessLogHttpHandler': {
        #     'class': 'logging.handlers.HTTPHandler',
        #     'level': 'INFO',
        #     'formatter': 'AccessLogFileFormatter',
        #     'host': '127.0.0.1:8888',
        #     'url': '/',
        #     'method': 'POST',
        #     'secure': False,
        #     'credentials': None,  # ('id', 'password'),
        #     'filters': [
        #         'isAccessLog'
        #     ]
        # },
        # 'AccessLogSysLogHandler': {
        #     'class': 'logging.handlers.SysLogHandler',
        #     'address': ('127.0.0.1', 514),
        #     'facility': "local0",
        #     'filters': [
        #         'isAccessLog'
        #     ]
        # },
    },
    'formatters': {
        'consoleFormatter': {
            'format': '[%(levelname)-8s] %(funcName)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
        'logFileFormatter': {
            'format': '%(asctime)s|%(levelname)-8s|%(name)s|%(funcName)s|%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
        'AccessLogFileFormatter': {
            'format': '%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
    }
}
