import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from typing import List
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from datetime import date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scraper')))
from lib.support_functions import get_folder_path
from lib.scraper import BezrealitkyScraper


class TestBezrealitkyScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.soup_homepage = cls.get_fixtures("base_url.html")
        cls.soup = cls.get_fixtures("url_praha.html")

    def setUp(self):
        self.base_url = r"https://www.bezrealitky.cz/vypis/nabidka-prodej/"
        self.prop_type = ["byt", "dum"]

    @staticmethod
    def get_fixtures(file):
        file_path = get_folder_path("python", "tests", "unit", "fixtures", file)
        with open(file_path, encoding="utf8") as html:
            return BeautifulSoup(html, "html.parser")

    def test_extract_content(self):
        soup = BezrealitkyScraper.extract_content(self.soup, "byt", "Praha")

        self.assertIsInstance(soup, List)
        self.assertEqual(len(soup), 10)

        result = {'typ_nemovistosti': 'byt',
                  'region': 'Praha',
                  'dispozice_nemovitosti': '2+kk',
                  'rozloha': '60',
                  'cena_nemovitosti': '6700000',
                  'odkaz': 'https://www.bezrealitky.cz/nemovitosti-byty-domy/649688-nabidka-prodej-bytu-kurta-konrada-praha'}
        self.assertEqual(soup[0], result)

    def test_get_property_type(self):
        property_type = BezrealitkyScraper.get_property_type(self, self.soup_homepage)

        for i in self.prop_type:
            self.assertIn(i, property_type.values())

        self.assertEqual(property_type, {'Byt': 'byt', 'Dům': 'dum'})

    def test_get_regions(self):
        regions = BezrealitkyScraper.get_regions(self.soup_homepage)

        regions_result = [{'id': '499', 'name': 'Plzeňský kraj', 'uri': 'plzensky-kraj', '__typename': 'Region'},
                  {'id': '498', 'name': 'Královéhradecký kraj', 'uri': 'kralovehradecky-kraj', '__typename': 'Region'},
                  {'id': '497', 'name': 'Moravskoslezský kraj', 'uri': 'moravskoslezsky-kraj', '__typename': 'Region'},
                  {'id': '496', 'name': 'Pardubický kraj', 'uri': 'pardubicky-kraj', '__typename': 'Region'},
                  {'id': '495', 'name': 'Olomoucký kraj', 'uri': 'olomoucky-kraj', '__typename': 'Region'},
                  {'id': '494', 'name': 'Liberecký kraj', 'uri': 'liberecky-kraj', '__typename': 'Region'},
                  {'id': '493', 'name': 'Kraj Vysočina', 'uri': 'kraj-vysocina', '__typename': 'Region'},
                  {'id': '492', 'name': 'Ústecký kraj', 'uri': 'ustecky-kraj', '__typename': 'Region'},
                  {'id': '491', 'name': 'Zlínský kraj', 'uri': 'zlinsky-kraj', '__typename': 'Region'},
                  {'id': '490', 'name': 'Středočeský kraj', 'uri': 'stredocesky-kraj', '__typename': 'Region'},
                  {'id': '489', 'name': 'Jihočeský kraj', 'uri': 'jihocesky-kraj', '__typename': 'Region'},
                  {'id': '488', 'name': 'Karlovarský kraj', 'uri': 'karlovarsky-kraj', '__typename': 'Region'},
                  {'id': '487', 'name': 'Jihomoravský kraj', 'uri': 'jihomoravsky-kraj', '__typename': 'Region'},
                  {'id': '486', 'name': 'Praha', 'uri': 'praha', '__typename': 'Region'}]

        self.assertEqual(regions, regions_result)

    def test_get_lastpage(self):
        lp = BezrealitkyScraper.get_lastpage(self.soup)
        self.assertIsInstance(lp, int)
        self.assertEqual(lp, 57)

    def test_url(self):
        region = {'id': '499', 'name': 'Plzeňský kraj', 'uri': 'plzensky-kraj', '__typename': 'Region'}
        property_type = {'Byt': 'byt'}
        page_str = "?page="
        page_nbr = 2

        for prop_type, prop_type_url in property_type.items():
            url = self.base_url + prop_type_url + "/" + region['uri'] + page_str + str(page_nbr)
            self.assertEqual(url, "https://www.bezrealitky.cz/vypis/nabidka-prodej/byt/plzensky-kraj?page=2")

    def test_create_df(self):
        soup = BezrealitkyScraper.extract_content(self.soup, "byt", "Praha")
        df = BezrealitkyScraper.create_df(soup)

        self.assertEqual(len(df.index), 10)
        self.assertEqual(df.dtypes.get("cena_nemovitosti"), "int32")
        self.assertEqual(df.dtypes.get("rozloha"), "int32")

        result = [{'typ_nemovistosti': 'byt',
                  'region': 'Praha',
                  'dispozice_nemovitosti': '2+kk',
                  'rozloha': '60',
                  'cena_nemovitosti': '6700000',
                  'odkaz': 'https://www.bezrealitky.cz/nemovitosti-byty-domy/649688-nabidka-prodej-bytu-kurta-konrada-praha',
                  'datum_stazeni': date.today()}]

        df_result = DataFrame(result)
        df_result = df_result.astype({'cena_nemovitosti': 'int32', 'rozloha': 'int32'})

        self.assertFalse(df.empty)
        assert_frame_equal(df_result, df.head(1), check_dtype=True)

if __name__ == '__main__':
    unittest.main()


# https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
# test folder
#  python -m unittest discover -s python\tests\unit\
# single module
# python -m unittest python\tests\unit\test_scraper.py
# test class
# python -m unittest python.tests.unit.test_scraper.TestBezrealitkyScraper
# single test
# python -m unittest python.tests.unit.test_scraper.TestBezrealitkyScraper.test_create_df
