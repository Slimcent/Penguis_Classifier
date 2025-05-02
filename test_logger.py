from Services.logger_service import LoggerService


def test_logger_service():
    logger = LoggerService("test_logger").get_logger()
    logger.info("This is a test info log.")
    logger.error("This is a test error log.")
    print("Logging complete. Check 'training_log.txt'.")


if __name__ == "__main__":
    test_logger_service()
