conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'isAccessLog': {
            '()': 'utils.CustomLogFilter.AccessLogFilter'
        },
        'isHuntLog': {
            '()': 'utils.CustomLogFilter.HuntLogFilter'
        },
        'isHuntResultLog': {
            '()': 'utils.CustomLogFilter.HuntResultLogFilter'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'consoleHandler',
            'logFileHandler',
            'AccessLogFileHandler',
            # 'AccessLogTCPHandler',
            'AccessLogHttpHandler',
            # 'AccessLogSysLogHandler',
            'HuntLogFileHandler',
            'HuntResultLogFileHandler',
            'HuntResultLogHttpHandler',
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
        # 'AccessLogTCPHandler': {
        #     'class': 'logging.handlers.SocketHandler',
        #     'level': 'INFO',
        #     'formatter': 'AccessLogFileFormatter',
        #     'host': '127.0.0.1',
        #     'port': '8888',
        #     'filters': [
        #         'isAccessLog'
        #     ]
        # },
        'AccessLogHttpHandler': {
            'class': 'logging.handlers.HTTPHandler',
            'level': 'INFO',
            'formatter': 'AccessLogFileFormatter',
            'host': '127.0.0.1:8888',
            'url': '/',
            'method': 'POST',
            'secure': False,
            'credentials': ('demo', 'demo'),
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
        'HuntLogFileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'HuntLogFileFormatter',
            'filename': './log/hunting.log',
            'when': 'MIDNIGHT',
            'backupCount': 10,
            'encoding': 'utf-8',
            'filters': [
                'isHuntLog'
            ]
        },
        'HuntResultLogFileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'HuntLogFileFormatter',
            'filename': './log/hunt_result.log',
            'when': 'MIDNIGHT',
            'backupCount': 10,
            'encoding': 'utf-8',
            'filters': [
                'isHuntResultLog'
            ]
        },
        'HuntResultLogHttpHandler': {
            'class': 'logging.handlers.HTTPHandler',
            'level': 'INFO',
            'formatter': 'HuntResultLogFileFormatter',
            'host': '127.0.0.1:8888',
            'url': '/',
            'method': 'POST',
            'secure': False,
            'credentials': ('demo', 'demo'),
            'filters': [
                'isHuntResultLog'
            ]
        },
    },
    'formatters': {
        'consoleFormatter': {
            'format': '%(asctime)s [%(levelname)-8s] %(funcName)s - %(message)s',
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
        'HuntLogFileFormatter': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
        'HuntResultLogFileFormatter': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
    }
}
