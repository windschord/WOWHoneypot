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
        ]
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'consoleFormatter',
            'stream': 'ext://sys.stdout'
        },
    },
    'formatters': {
        'consoleFormatter': {
            'format': '%(asctime)s [%(levelname)-8s] %(funcName)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S%z'
        },
    }
}
