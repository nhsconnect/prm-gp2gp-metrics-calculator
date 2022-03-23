import logging
import sys
from dataclasses import asdict
from typing import Dict, List

import pyarrow as pa
from botocore.exceptions import ClientError

from prmcalculator.domain.gp2gp.transfer import Transfer, convert_table_to_transfers
from prmcalculator.domain.national.construct_national_metrics_presentation import (
    NationalMetricsPresentation,
)
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.utils.io.dictionary import camelize_dict
from prmcalculator.utils.io.s3 import S3DataManager

logger = logging.getLogger(__name__)


class PlatformMetricsIO:
    def __init__(
        self,
        s3_data_manager: S3DataManager,
        ssm_manager,
        output_metadata: Dict[str, str],
    ):
        self._ssm_manager = ssm_manager
        self._s3_manager = s3_data_manager
        self._output_metadata = output_metadata

    @staticmethod
    def _create_platform_json_object(platform_data) -> dict:
        content_dict = asdict(platform_data)
        return camelize_dict(content_dict)

    def read_ods_metadata(self, s3_uri: str) -> OrganisationMetadata:
        ods_metadata_dict = self._s3_manager.read_json(s3_uri)
        return OrganisationMetadata.from_dict(ods_metadata_dict)

    def read_transfers_as_dataclass(self, s3_uris: List[str]) -> List[Transfer]:
        transfer_table = self.read_transfers_as_table(s3_uris)
        return convert_table_to_transfers(transfer_table)

    # TODO: would this be a private method?
    def read_transfers_as_table(self, s3_uris: List[str]) -> pa.Table:
        return pa.concat_tables(
            [self._s3_manager.read_parquet(s3_path) for s3_path in s3_uris],
        )

    def write_national_metrics(
        self, national_metrics_presentation_data: NationalMetricsPresentation, s3_uri: str
    ):
        self._s3_manager.write_json(
            object_uri=s3_uri,
            data=self._create_platform_json_object(national_metrics_presentation_data),
            metadata=self._output_metadata,
        )

    def store_national_metrics_uri_ssm_param(self, s3_uri: str):
        try:
            logger.info(
                "Attempting to store national metrics URI SSM param for NATIONAL_METRICS_LOCATION: "
                + s3_uri
            )
            self._ssm_manager.put_parameter(
                Name="NATIONAL_METRICS_LOCATION", Value=s3_uri, Type="String"
            )
            logger.info(
                "Successfully stored national metrics URI SSM param for NATIONAL_METRICS_LOCATION"
            )
        except ClientError as e:
            logger.error(e)
            sys.exit(1)

    def write_practice_metrics(self, practice_metrics_presentation_data, s3_uri: str):
        self._s3_manager.write_json(
            object_uri=s3_uri,
            data=self._create_platform_json_object(practice_metrics_presentation_data),
            metadata=self._output_metadata,
        )
