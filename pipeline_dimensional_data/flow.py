from typing import Any, Dict

from utils import generate_execution_id
from logging import setup_logger
from pipeline_dimensional_data import config
from pipeline_dimensional_data.tasks import (
    update_dimensions_task,
    update_fact_error_task,
    update_fact_task,
)


class DimensionalDataFlow:
    """
    Dimensional data pipeline flow.

    This class sequentially executes the dimensional data pipeline tasks.

    The regular pipeline order is:
        1. Update dimension tables
        2. Insert faulty fact rows into FactOrdersError
        3. Insert valid fact rows into FactOrders
    """

    def __init__(
        self,
        database_name: str = config.DATABASE_NAME,
        schema_name: str = config.SCHEMA_NAME,
    ) -> None:
        """
        Initializes a dimensional data flow instance.

        A unique execution_id is generated for each flow instance.
        This execution_id is passed into all SQL scripts for tracking.

        Args:
            database_name (str): Dimensional database name.
            schema_name (str): Schema name.
        """
        self.database_name = database_name
        self.schema_name = schema_name
        self.execution_id = generate_execution_id()
        self.logger = setup_logger(self.execution_id)

    def exec(
        self,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Executes the dimensional data pipeline sequentially.

        Args:
            start_date (str): Start date for fact/fact error ingestion.
            end_date (str): End date for fact/fact error ingestion.

        Returns:
            Dict[str, Any]: Pipeline execution result.
        """
        dimensions_result = update_dimensions_task(
            database_name=self.database_name,
            schema_name=self.schema_name,
            execution_id=self.execution_id,
        )

        fact_error_result = update_fact_error_task(
            database_name=self.database_name,
            schema_name=self.schema_name,
            start_date=start_date,
            end_date=end_date,
            execution_id=self.execution_id,
            previous_task_result=dimensions_result,
        )

        fact_result = update_fact_task(
            database_name=self.database_name,
            schema_name=self.schema_name,
            start_date=start_date,
            end_date=end_date,
            execution_id=self.execution_id,
            previous_task_result=fact_error_result,
        )

        self.logger.info("Dimensional data flow completed successfully")

        return {
            "success": fact_result["success"],
            "execution_id": self.execution_id,
            "start_date": start_date,
            "end_date": end_date,
            "tasks": {
                "dimensions": dimensions_result,
                "fact_error": fact_error_result,
                "fact": fact_result,
            },
        }