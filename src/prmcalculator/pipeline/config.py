from datetime import datetime
from dataclasses import dataclass
import logging

from typing import Optional

from dateutil.parser import isoparse

logger = logging.getLogger(__name__)


class MissingEnvironmentVariable(Exception):
    pass


class EnvConfig:
    def __init__(self, env_vars):
        self._env_vars = env_vars

    def _read_env(self, name: str, optional: bool, converter=None, default=None):
        try:
            env_var = self._env_vars[name]
            if converter:
                return converter(env_var)
            else:
                return env_var
        except KeyError:
            if optional:
                return default
            else:
                raise MissingEnvironmentVariable(
                    f"Expected environment variable {name} was not set, exiting..."
                )

    def read_str(self, name: str) -> str:
        return self._read_env(name, optional=False)

    def read_optional_int(self, name: str, default) -> int:
        return self._read_env(name, optional=True, converter=int, default=default)

    def read_optional_str(self, name: str) -> Optional[str]:
        return self._read_env(name, optional=True)

    def read_datetime(self, name: str) -> datetime:
        return self._read_env(name, optional=False, converter=isoparse)


@dataclass
class PipelineConfig:
    input_transfer_data_bucket: str
    organisation_metadata_bucket: str
    output_metrics_bucket: str
    date_anchor: datetime
    number_of_months: int = 1
    s3_endpoint_url: Optional[str] = None

    @classmethod
    def from_environment_variables(cls, env_vars):
        env = EnvConfig(env_vars)
        return cls(
            input_transfer_data_bucket=env.read_str("INPUT_TRANSFER_DATA_BUCKET"),
            organisation_metadata_bucket=env.read_str("ORGANISATION_METADATA_BUCKET"),
            output_metrics_bucket=env.read_str("OUTPUT_METRICS_BUCKET"),
            date_anchor=env.read_datetime("DATE_ANCHOR"),
            number_of_months=env.read_optional_int(
                name="NUMBER_OF_MONTHS", default=cls.number_of_months
            ),
            s3_endpoint_url=env.read_optional_str("S3_ENDPOINT_URL"),
        )
