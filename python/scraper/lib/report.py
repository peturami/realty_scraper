from datetime import datetime
import logging
import os
from typing import Dict
import jinja2
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
from pandas import DataFrame, Series
from lib.support_functions import get_path, running_script_name

logger = logging.getLogger(running_script_name(__name__))


class ReportHTML:
    """Class for rendering html reports based on data from web scraper
    """

    def __init__(self, data: DataFrame) -> None:
        self.data = data[(data["typ_nemovistosti"] == "Byt")]
        self.tmp_dir = get_path("output", "temp")
        self.template_dir = get_path("templates")
        self.template_file = "report.html"
        self.output_dir = get_path("output")


    def create_report(self) -> None:
        # create horizontal chart
        sq_m_avg = self.get_avg_price_sq_m()

        self.horizontal_bar_chart(sq_m_avg, "prumer.png")

        # create pie charts
        # number of displayed items in pie charts + create group of other
        n = 6

        flats_ttl = self.get_total_flats_by_region(n)
        self.make_pie(flats_ttl, color='Pastel1', head='Počet nabídek podle kraje', graph_name='kraje.png')

        flat_disp = self.get_flats_structure_prague(n)
        self.make_pie(flat_disp, color='Pastel2', head="Struktura bytů v Praze", graph_name='struktura.png')

        # generate final report
        template_vars = self.prepare_template_vars(sq_m_avg, flats_ttl, flat_disp)
        self.generate_html(template_vars)
        self.save_report(self.generate_html(template_vars))

    def get_avg_price_sq_m(self) -> Series:
        sq_m_avg = self.data.set_index('region')
        sq_m_avg['price_4_m2'] = sq_m_avg['cena_nemovitosti'] / sq_m_avg['rozloha']
        sq_m_avg = sq_m_avg['price_4_m2'].groupby('region').median().round().astype(int)
        return sq_m_avg

    def get_total_flats_by_region(self, n: int) -> DataFrame:
        flats_ttl = self.data.groupby('region').size().sort_values(
            ascending=False).reset_index()
        flats_ttl.loc[flats_ttl.index >= n, 'region'] = 'ostatní'
        flats_ttl.columns = ["Region", 'Počet bytů']
        flats_ttl = flats_ttl.groupby('Region').sum().sort_values(ascending=False, by='Počet bytů')
        return flats_ttl

    def get_flats_structure_prague(self, n: int) -> DataFrame:
        flat_disp = self.data[self.data["region"] == "Praha"].groupby(
            'dispozice_nemovitosti').size().sort_values(ascending=False).reset_index()
        flat_disp.loc[flat_disp.index >= n, 'dispozice_nemovitosti'] = 'jiné'
        flat_disp.columns = ["Dispozice", 'Počet bytů']
        flat_disp = flat_disp.groupby('Dispozice').sum().sort_values(ascending=False, by='Počet bytů')
        return flat_disp

    @staticmethod
    def get_sum(df: DataFrame) -> int:
        return int(np.sum(df))

    def prepare_template_vars(self, sq_m_avg: Series, flats_ttl: DataFrame, flat_disp: DataFrame) -> Dict:
        # final report variables
        pocet_bytu = len(self.data.index)
        nejdrazsi_region = sq_m_avg.idxmax()
        nejvyssi_cena = sq_m_avg.loc[nejdrazsi_region]
        nejlevnejsi_region = sq_m_avg.idxmin()
        nejnizsi_cena = sq_m_avg.loc[nejlevnejsi_region]
        nejvice_bytu = flats_ttl.idxmax()['Počet bytů']
        nejvice_bytu_pct = int(flats_ttl.loc[nejvice_bytu]['Počet bytů'] / pocet_bytu * 100)
        nejcastejsi_dispozice = flat_disp.idxmax()['Počet bytů']
        total = self.get_sum(flat_disp)
        nejcastejsi_dispozice_pct = int(flat_disp.loc[nejcastejsi_dispozice]['Počet bytů'] / total * 100)

        return {
            "pocet_bytu": pocet_bytu,
            "nejdrazsi_region": nejdrazsi_region.upper(),
            "nejvyssi_cena": "{:,}".format(nejvyssi_cena).replace(',', ' '),
            "nejlevnejsi_region": nejlevnejsi_region.upper(),
            "nejnizsi_cena": "{:,}".format(nejnizsi_cena).replace(',', ' '),
            "nejvice_bytu": nejvice_bytu,
            "nejvice_bytu_pct": nejvice_bytu_pct,
            "nejcastejsi_dispozice": nejcastejsi_dispozice,
            "nejcastejsi_dispozice_pct": nejcastejsi_dispozice_pct,
            "vygenerovano": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

    def horizontal_bar_chart(self, data: Series, graph_name: str) -> None:
        ax = data.sort_values().plot(kind='barh', figsize=(8, 8), color='#86bf91', zorder=2, width=0.75)

        # Despine
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Switch off ticks
        ax.tick_params(labelsize="10", axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False,
                       right=False, labelleft=True)

        # Draw vertical axis lines
        vals = ax.get_xticks()
        for tick in vals:
            ax.axvline(x=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)

        # Set y-axis label
        ax.set_ylabel("Region", labelpad=20, weight='bold', size=12)

        # Set x-axis label
        ax.set_xlabel("Průměrná cena za m²", labelpad=20, weight='bold', size=12)

        # Format x-axis label
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,g} Kč'))

        graph_path = os.path.join(self.tmp_dir, graph_name)
        plt.savefig(graph_path, dpi=85, bbox_inches='tight')

    def make_pie(self, df: DataFrame, color: str, head: str, graph_name: str) -> None:

        total = self.get_sum(df)

        fig, ax = plt.subplots()
        ax.axis('equal')

        theme = plt.get_cmap(color)
        ax.set_prop_cycle("color", [theme(1. * i / len(df)) for i in range(len(df))])

        outside, _ = ax.pie(df.iloc[:, 0], radius=1.1, startangle=180)

        plt.setp(outside, width=0.2, edgecolor='white')

        ax.text(0, 0, total, ha='center', va='center', size=30)
        ax.legend(['{:.0f}%: {}'.format(int(row.values) / total * 100, index) for index, row in df.iterrows()],
                  frameon=False, bbox_to_anchor=(0.75, 0.02), labelspacing=0.7)
        ax.annotate(head, size=14, fontweight="semibold", xy=(1, 1), xycoords='data',
                    horizontalalignment='center', verticalalignment='top', xytext=(0.1, 1.4))

        graph_path = os.path.join(self.tmp_dir, graph_name)
        plt.savefig(graph_path, dpi=80, bbox_inches='tight')

    def generate_html(self, template_vars: Dict[str, str]) -> str:
        templateLoader = jinja2.FileSystemLoader(self.template_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(self.template_file)
        rendered_report = template.render(template_vars)
        return rendered_report

    def save_report(self, rendered_report: str) -> None:
        output_file = os.path.join(self.output_dir, self.template_file)
        with open(output_file, "w", encoding="utf8") as report:
            report.write(rendered_report)
