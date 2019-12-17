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
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'logFileFormatter',
            'filename': './log/wowhoneypot.log',
            'mode': 'a',
            'encoding': 'utf-8'
        },
        'AccessLogFileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'AccessLogFileFormatter',
            'filename': './log/access.log',
            'mode': 'a',
            'encoding': 'utf-8',
            'filters': [
                'isAccessLog'
            ]
        },
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
