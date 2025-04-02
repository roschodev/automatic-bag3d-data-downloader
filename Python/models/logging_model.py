import logging

class LogHandler:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        
        # Create a file handler and set it up
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # Create a console handler and set it up
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(formatter)

        # Get the root logger and set its level to DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Ensure logging level is set
        logger.addHandler(self.file_handler)  # Add file handler to root logger
        logger.addHandler(self.console_handler)  # Add console handler to root logger

    def log_message(self, level, message, toFile=False, toConsole=True, includeMetaData=True):
        # Dictionary to map level strings to logging functions

        base_format = '%(asctime)s - %(levelname)s - %(message)s'
        if not includeMetaData:
            base_format = '%(message)s'

        self.formatter = logging.Formatter(base_format)
        self.file_handler.setFormatter(self.formatter)
        self.console_handler.setFormatter(self.formatter)

        switcher = {
            'info': logging.info,
            'warning': logging.warning,
            'error': logging.error,
            'debug': logging.debug,
            'critical': logging.critical
        }

        # Log the message with the appropriate logging function
        log_func = switcher.get(level.lower(), logging.info)
        
        # Optionally disable logging to file
        if not toFile:
            logging.getLogger().removeHandler(self.file_handler)
        
        # Optionally disable logging to console
        if not toConsole:
            logging.getLogger().removeHandler(self.console_handler)
        
        # Log the message
        log_func(message)

        # Re-add handlers if needed after logging
        if toFile and self.file_handler not in logging.getLogger().handlers:
            logging.getLogger().addHandler(self.file_handler)
        
        if toConsole and self.console_handler not in logging.getLogger().handlers:
            logging.getLogger().addHandler(self.console_handler)




