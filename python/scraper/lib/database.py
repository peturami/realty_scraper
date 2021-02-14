import os
import logging
import sqlite3
from typing import Dict
from pandas import DataFrame
from lib.support_functions import get_path, running_script_name

logger = logging.getLogger(running_script_name(__name__))


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
        self.scraper_database = get_path("output", "scraper_data.db")

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
                logger.info(f"{len(self.df.index)} rows have been inserted to stage.")
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
