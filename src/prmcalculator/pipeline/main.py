import logging
from os import environ

from prmcalculator.pipeline.config import PipelineConfig
from prmcalculator.pipeline.metrics_calculator import MetricsCalculator
from prmcalculator.utils.io.json_formatter import JsonFormatter

logger = logging.getLogger("prmcalculator")


def _setup_logger():
    logger.setLevel(logging.INFO)
    formatter = JsonFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    _setup_logger()
    config = PipelineConfig.from_environment_variables(environ)
    pipeline = MetricsCalculator(config)
    pipeline.run()


if __name__ == "__main__":
    main()
