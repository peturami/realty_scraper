from database import Database
from report import ReportHTML
from scraper import BezrealitkyScraper
from supported_functions import init_config
from time import perf_counter
import logging


# basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Appliaction starts.")

start_time = perf_counter()

if __name__ == '__main__':

    config = init_config("config", "config.yaml")
    sql = init_config("config", "sql.yaml")

    scraper = BezrealitkyScraper(config["url"], config["typ_nemovitosti"])
    data = scraper.main()

    if config['report'] == 'Y' and 'byt' in config["typ_nemovitosti"]:
        report = ReportHTML(data)
        report.create_report()

    db = Database(data, sql)
    db.save_to_db()

end_time = perf_counter()
logger.info(f"Application finished successfuly. Total time was {(end_time-start_time):.2f}s.")
