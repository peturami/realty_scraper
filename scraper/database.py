import os
import logging
import sqlite3
from typing import Dict
from pandas import DataFrame
from supported_functions import get_folder_path

logger = logging.getLogger(__name__)


class Database:
    """Class for saving and historisation of scraper data.
    """

    def __init__(self, df: DataFrame, sql: Dict) -> None:
        self.df = df
        self.ddl = sql['ddl']
        self.h_ddl = sql['h_ddl']
        self.deleted_dml = sql['deleted_dml']
        self.changed_dml = sql['changed_dml']
        self.new_dml = sql['new_dml']
        self.scraper_database = os.path.join(get_folder_path("output"), "scraper_data.db")

    def create_table(self) -> None:
        try:
            with sqlite3.connect(self.scraper_database) as conn:
                cur = conn.cursor()
                cur.execute(self.ddl)
                cur.execute(self.h_ddl)
        except Exception as ex:
            logger.exception("Exception occurred:")

    def insert(self) -> None:
        logger.info(f"Inserting new records to stage table: scraper_data.Realty_stg.")
        try:
            with sqlite3.connect(self.scraper_database) as conn:
                cur = conn.cursor()
                cur.execute("delete from Realty_stg")
                self.df.to_sql("Realty_stg", conn, index=False, if_exists="append")
        except Exception as ex:
            logger.exception("Exception occurred:")

    def historisation(self) -> None:
        logger.info("Historization starts scraper_data.H_Realty.")
        try:
            with sqlite3.connect(self.scraper_database) as conn:
                cur = conn.cursor()
                row_count=cur.execute(self.deleted_dml).rowcount
                logger.info(f"{row_count} ad(s) was deleted from web.")
                row_count=cur.execute(self.changed_dml).rowcount
                logger.info(f"{row_count} ad(s) changed the price.")
                row_count=cur.execute(self.new_dml).rowcount
                logger.info(f"{row_count} new ad(s) was published.")
        except Exception as ex:
            logger.exception("Exception occurred:")

    def save_to_db(self) -> None:
        self.create_table()
        self.insert()
        self.historisation()
