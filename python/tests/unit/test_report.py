import unittest
from unittest.mock import patch
from typing import Dict
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal, assert_series_equal
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scraper')))

from lib.support_functions import get_folder_path
from lib.report import ReportHTML


class TestReportHTML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        df = cls.get_fixtures("df_scraper_data.txt")
        cls.data = df[(df["typ_nemovistosti"] == "Byt")]
        cls.itemsPie = 4
        cls.output_dir = get_folder_path("python", "tests")
        cls.template_dir = get_folder_path("templates")
        cls.template_file = "report.html"

    @staticmethod
    def get_fixtures(file):
        file_path = get_folder_path("python", "tests", "unit", "fixtures", file)
        df = pd.read_csv(file_path)
        return df

    def test_get_avg_price_sq_m(self):
        sq_m_avg = ReportHTML.get_avg_price_sq_m(self)

        index = ['Jihomoravský kraj', 'Jihočeský kraj', 'Karlovarský kraj', 'Kraj Vysočina', 'Královéhradecký kraj',
                 'Liberecký kraj', 'Moravskoslezský kraj', 'Olomoucký kraj', 'Pardubický kraj', 'Plzeňský kraj',
                 'Praha', 'Středočeský kraj', 'Zlínský kraj', 'Ústecký kraj']
        data = [76343, 40932, 22846, 40692, 46875, 42632, 30833, 35593, 44939, 48438, 103927, 55035, 41842, 17308]
        result_series = pd.Series(data=data, index=index, dtype='int64')
        result_series.index.name = 'region'
        result_series.name = 'price_4_m2'

        # check if result is pandas Series
        self.assertIsInstance(sq_m_avg, pd.Series)
        # compare value for Prague
        self.assertEqual(sq_m_avg.filter(like='Praha').values[0], 103927)
        # compare final series
        assert_series_equal(sq_m_avg, result_series)

    def test_get_total_flats_by_region(self):
        flats_ttl = ReportHTML.get_total_flats_by_region(self, self.itemsPie)
        index = ['Praha', 'ostatní', 'Jihomoravský kraj', 'Středočeský kraj', 'Ústecký kraj']
        data = [679, 201, 52, 50, 47]
        result_df = pd.DataFrame({'Region': index, 'Počet bytů': data}).set_index('Region')

        self.assertIsInstance(flats_ttl, pd.DataFrame)
        self.assertEqual(flats_ttl.loc['Praha'].values[0], 679)
        assert_frame_equal(flats_ttl, result_df)

    def test_get_flats_structure_prague(self):
        flat_disp = ReportHTML.get_flats_structure_prague(self, self.itemsPie)
        index = ['2+kk', 'jiné', '3+kk', '1+kk', '4+kk']
        data = [201, 154, 135, 131, 58]
        result_df = pd.DataFrame({'Dispozice': index, 'Počet bytů': data}).set_index('Dispozice')

        self.assertIsInstance(flat_disp, pd.DataFrame)
        self.assertEqual(flat_disp.loc['2+kk'].values[0], 201)
        assert_frame_equal(flat_disp, result_df)

    def test_sum(self):
        total = ReportHTML.get_sum(self.data['rozloha'])
        self.assertIsInstance(total, int)
        self.assertEqual(total, 134016)

    def test_prepare_template_vars(self):
        sq_m_avg = ReportHTML.get_avg_price_sq_m(self)
        flats_ttl = ReportHTML.get_total_flats_by_region(self, self.itemsPie)
        flat_disp = ReportHTML.get_flats_structure_prague(self, self.itemsPie)

        #total = ReportHTML.get_sum(flat_disp)
        #with patch('lib.report.ReportHTML.get_sum') as mocked_total:
        #    report = ReportHTML(self.data)
        #    mocked_total.return_value = total
        #    template_vars = report.prepare_template_vars(sq_m_avg, flats_ttl, flat_disp)

        #works the same as the above
        report = ReportHTML(self.data)
        template_vars = report.prepare_template_vars(sq_m_avg, flats_ttl, flat_disp)

        result_dict = {'pocet_bytu': 1029,
                       'nejdrazsi_region': 'PRAHA',
                       'nejvyssi_cena': '103 927',
                       'nejlevnejsi_region': 'ÚSTECKÝ KRAJ',
                       'nejnizsi_cena': '17 308',
                       'nejvice_bytu': 'Praha',
                       'nejvice_bytu_pct': 65,
                       'nejcastejsi_dispozice': '2+kk',
                       'nejcastejsi_dispozice_pct': 29,
                       'vygenerovano': datetime.now().strftime("%d.%m.%Y %H:%M")}

        self.assertIsInstance(template_vars, Dict)
        self.assertEqual(template_vars, result_dict)

    def test_generate_html(self):
        sq_m_avg = ReportHTML.get_avg_price_sq_m(self)
        flats_ttl = ReportHTML.get_total_flats_by_region(self, self.itemsPie)
        flat_disp = ReportHTML.get_flats_structure_prague(self, self.itemsPie)

        # mocked datetime, because "vygenerovano" variable is generate from datetime.now()
        with patch('lib.report.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = datetime(2020, 11, 16, 22, 42, 00)
            report = ReportHTML(self.data)
            template_vars = report.prepare_template_vars(sq_m_avg, flats_ttl, flat_disp)

        report = ReportHTML.generate_html(self, template_vars)

        with open(get_folder_path("python", "tests", "unit", "fixtures", "report.html"), "r", encoding="utf8") as rep:
            expected_report = rep.read()

        self.assertEqual(report, expected_report)


if __name__ == '__main__':
    unittest.main()


# test folder
#  python -m unittest discover -s python\tests\unit\
# test module
# python -m unittest python\tests\unit\test_report.py
# test class
# python -m unittest python.tests.unit.test_report.TestReportHTML
# single test
# python -m unittest python.tests.unit.test_report.TestReportHTML.test_generate_html
