from datetime import datetime
from dataclasses import dataclass
import logging

from typing import Optional

from dateutil.parser import isoparse

logger = logging.getLogger(__name__)


class MissingEnvironmentVariable(Exception):
    pass


class InvalidEnvironmentVariableValue(Exception):
    pass


class EnvConfig:
    def __init__(self, env_vars):
        self._env_vars = env_vars

    def _read_env(self, name: str, optional: bool, converter=None, default=None):  # noqa: C901
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
        except ValueError:
            if optional:
                return default
            else:
                raise InvalidEnvironmentVariableValue(
                    f"Expected environment variable {name} value is invalid, exiting..."
                )

    def read_str(self, name: str) -> str:
        return self._read_env(name, optional=False)

    def read_optional_int(self, name: str, default: int) -> int:
        return self._read_env(name, optional=True, converter=int, default=default)

    def read_optional_str(self, name: str) -> Optional[str]:
        return self._read_env(name, optional=True)

    def read_datetime(self, name: str) -> datetime:
        return self._read_env(name, optional=False, converter=isoparse)

    def read_optional_bool(self, name: str, default: bool) -> bool:
        return self._read_env(
            name, optional=True, converter=lambda string: string.lower() == "true", default=default
        )


@dataclass
class PipelineConfig:
    build_tag: str
    input_transfer_data_bucket: str
    organisation_metadata_bucket: str
    output_metrics_bucket: str
    date_anchor: datetime
    number_of_months: int
    s3_endpoint_url: Optional[str]
    hide_slow_transferred_records_after_days: Optional[int]

    @classmethod
    def from_environment_variables(cls, env_vars):
        env = EnvConfig(env_vars)
        return cls(
            build_tag=env.read_str("BUILD_TAG"),
            input_transfer_data_bucket=env.read_str("INPUT_TRANSFER_DATA_BUCKET"),
            organisation_metadata_bucket=env.read_str("ORGANISATION_METADATA_BUCKET"),
            output_metrics_bucket=env.read_str("OUTPUT_METRICS_BUCKET"),
            date_anchor=env.read_datetime("DATE_ANCHOR"),
            number_of_months=env.read_optional_int("NUMBER_OF_MONTHS", default=1),
            s3_endpoint_url=env.read_optional_str("S3_ENDPOINT_URL"),
            hide_slow_transferred_records_after_days=env.read_optional_int(
                "HIDE_SLOW_TRANSFERRED_RECORDS_AFTER_DAYS", default=1
            ),
        )
