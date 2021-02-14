from lib.database import Database
from lib.report import ReportHTML
from lib.scraper import BezrealitkyScraper
from lib.support_functions import init_config, running_script_name, get_path
from time import perf_counter
import logging
import argparse
import os


# basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(running_script_name(__name__))
logger.info("Appliaction starts.")

start_time = perf_counter()

# parse arguments provided by CLI
parser = argparse.ArgumentParser(prog="Bezrealitky_Scraper", description="HTML scraper bezrealitky.cz")
# add args
parser.add_argument(
    '-conf', '--config_path',
    dest='config_path',
    required=False,
    help='path to application config file (default in config in src)'
)
parser.add_argument(
    '-report', '--generate_report',
    dest='generate_report',
    required=False,
    choices=['Y', 'N'],
    help='generate report [Y/N] (default: Y)'
)
# parse input args
args = parser.parse_args()

# assign default config file - first use conf provided via CLI args otherwise use default
if args.config_path is not None and os.path.isfile(args.config_path):
    default_config = init_config(args.config_path)
    logger.info(f"Using config from args.config_path {default_config}")
else:
    default_config = init_config(get_path("config", "config.yaml"))
    logger.info(f"Using default config {default_config}")

# assign default value for generate report option
if args.generate_report is not None:
    report = args.generate_report
    logger.info(f"Overwrite generate report option to: {report}")
else:
    report = default_config["report"]

sql = init_config(get_path("config", "sql.yaml"))

if __name__ == '__main__':

    scraper = BezrealitkyScraper(default_config["url"], default_config["typ_nemovitosti"])
    data = scraper.main()

    # generate in case property type include "byt" and report option is Y
    if report == 'Y' and 'byt' in default_config["typ_nemovitosti"]:
        report = ReportHTML(data)
        report.create_report()

    db = Database(data, sql)
    db.save_to_db()

end_time = perf_counter()
logger.info(f"Application finished successfuly. Total time was {(end_time-start_time):.2f}s.")
