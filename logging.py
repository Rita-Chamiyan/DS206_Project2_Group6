from pathlib import Path
import importlib.util
import sysconfig


stdlib_logging_path = Path(sysconfig.get_paths()["stdlib"]) / "logging" / "__init__.py"
spec = importlib.util.spec_from_file_location("stdlib_logging", stdlib_logging_path)
stdlib_logging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stdlib_logging)


class ExecutionIdFilter(stdlib_logging.Filter):
    def __init__(self, execution_id: str):
        super().__init__()
        self.execution_id = execution_id

    def filter(self, record):
        record.execution_id = self.execution_id
        return True


def setup_logger(execution_id: str, log_file: str = "logs/logs_dimensional_data_pipeline.txt"):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = stdlib_logging.getLogger(f"dimensional_data_pipeline_{execution_id}")
    logger.setLevel(stdlib_logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = stdlib_logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | execution_id=%(execution_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = stdlib_logging.FileHandler(log_file)
    file_handler.setLevel(stdlib_logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ExecutionIdFilter(execution_id))

    console_handler = stdlib_logging.StreamHandler()
    console_handler.setLevel(stdlib_logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ExecutionIdFilter(execution_id))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
