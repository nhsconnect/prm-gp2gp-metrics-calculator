import logging
from os import environ

from prmcalculator.pipeline.config import PipelineConfig
from prmcalculator.pipeline.metrics_calculator import MetricsCalculator
from prmcalculator.pipeline.monthly_metrics_calculator import MonthlyMetricsCalculator
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

    MetricsCalculator(
        config
    ).run() if config.read_daily_transfer_files == 1 else MonthlyMetricsCalculator(config).run()


if __name__ == "__main__":
    main()
