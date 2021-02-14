from lib.support_functions import running_script_name
from datetime import date
import json
import logging
import time
from typing import List, Dict, Optional, Union
from bs4 import BeautifulSoup
import pandas as pd
import requests

logger = logging.getLogger(running_script_name(__name__))


class BezrealitkyScraper:
    """Class for handling web scraping
    """

    def __init__(self, base_url: str, prop_type: List[str]) -> None:
        """
        Args:
            base_url (str): homepage url
            prop_type (List[str]): property types list
        """
        self.base_url = base_url
        self.prop_type = prop_type

    def __str__(self):
        return "BezrealitkyScraper, args(url:{}, type:{})".format(self.base_url, self.prop_type)

    def __repr__(self):
        return "<BezrealitkyScraper({}, {})>".format(self.base_url, self.prop_type)

    def get_content(self, url: str) -> BeautifulSoup:
        """Method that requests the page and returns html code as BeautifulSoup object

        Args:
            url (str): url of scraping web page

        Returns:
            BeautifulSoup: final page result as BeautifulSoup
        """

        try:
            response = requests.get(url)
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.HTTPError as e:
            logger.exception("Exception HTTPError occurred:")
            raise SystemError(1)

    @staticmethod
    def extract_content(soup: BeautifulSoup, prop_type: str, region: str) -> List[Dict[str, Optional[str]]]:
        """Method for extracting data from ads

        Args:
            soup (BeautifulSoup): page to parse
            prop_type (str): type of the property
            region (str): region

        Returns:
            List[Dict[str, Optional[str]]]: List of parsed ads from one page
        """
        parsed_page: List[Dict[str, Optional[str]]] = []
        for item in soup.find_all("div", {"class": "product__body-new"}):
            price_tag = (item.find('strong', {"class": "product__value"}).text
                         .replace(" ", "")
                         .replace("\n", "")
                         .replace(".", "")
                         .replace("Kč", "")
                         )

            disposition_x_square = (item.find('p', {"class": "product__note"}).text
                                    .replace(" ", "")
                                    .replace("Prodejbytu", "")
                                    .replace("Prodejpozemku,", "")
                                    .replace("Prodejdomu,", "")
                                    .replace("Prodejgaráže,", "")
                                    .replace("Prodejkanceláře,", "")
                                    .replace("Prodejnebytovéhoprostoru,", "")
                                    .replace("Prodejchaty,chalupy,", "")
                                    .replace("m²", "")
                                    .replace(".", "")
                                    .replace("\n", ""))

            if prop_type.lower() == "byt":
                rooms, _, square = disposition_x_square.partition(",")
            else:
                square, rooms = (disposition_x_square, None)

            ad_link = item.find('a', {"class": "product__link js-product-link"}).get("href")

            parsed_page.append({
                    "typ_nemovistosti": prop_type,
                    "region": region,
                    "dispozice_nemovitosti": rooms,
                    "rozloha": square,
                    "cena_nemovitosti": price_tag,
                    "odkaz": "https://www.bezrealitky.cz{}".format(ad_link)
                })
        return parsed_page

    def get_property_type(self, soup: BeautifulSoup) -> Dict:
        """Return types of property and its URI

        Args:
            soup (BeautifulSoup): home page to parse

        Returns:
            Dict: Property types and its URI
        """
        property_type = soup.find_all("div", {"class": "dropdown-menu select-menu no-js-hide"})[1].find_all("span", {
            "class": "dropdown-item select-item"})

        # get uri for all types of property in config file - create dictionary
        # property_type_dict = {i.text: i.get('for') for i in property_type}
        property_type_dict = {}
        for prop in self.prop_type:
            property_type_dict.update({i.text: i.get('for') for i in property_type if i.get('for') == prop})

        return property_type_dict

    @staticmethod
    def get_regions(soup: BeautifulSoup) -> List[Dict]:
        """Return all regions in country

        Args:
            soup (BeautifulSoup): home page to parse

        Returns:
            List[Dict]: List of parsed regions and its URI
        """        
        # get all countries first, then find Czech Republic ID a get all regions
        countries = json.loads(soup.find("div", {"id": "regionSelector"}).get('data-countries'))
        coutry_id = {country['uri']: country['id'] for country in countries}['ceska-republika']
        regions = json.loads(soup.find("div", {"id": "regionSelector"}).get('data-region-children'))[coutry_id]['children']
        return regions

    @staticmethod
    def get_lastpage(soup: BeautifulSoup) -> int:
        """Return number of pages

        Args:
            soup (BeautifulSoup): html to parse

        Returns:
            int: total nbr of pages for property type in region
        """
        return int(max([page.text for page in soup.find_all("a", {"class": "page-link pagination__page"}) if page.text.isnumeric()]))

    @staticmethod
    def create_df(json_data: List[Dict]) -> pd.DataFrame:
        """Method for cleaning and converting input data in json to pandas dataframe

        0.Convert data to pandas dataframe.
        1.Add new column with current date.
        2.Remove all ads that are missing values such as price or size of the property.
        3.Cast price and size from string to int32.

        Args:
            json_data (List[dict]): input data from scraper

        Returns:
            pd.DataFrame: converted data in pandas dataframe format
        """
        today = date.today()
        df = pd.DataFrame(json_data)
        df["datum_stazeni"] = today
        # DataFrame cleaning
        df = df[~((df["rozloha"] == "") | (df["rozloha"].isna()))]
        df = df[~((df["dispozice_nemovitosti"] == "") | (df["dispozice_nemovitosti"].isna()) & (df["typ_nemovistosti"] == "Byt"))]
        df = df[~((df["cena_nemovitosti"] == "1") | (df["cena_nemovitosti"] == "") | (df["cena_nemovitosti"].isna()) | (df["cena_nemovitosti"].str.contains('+', regex=False)))]

        # Data type casting
        df = df.astype({'cena_nemovitosti': 'int32', 'rozloha': 'int32'})
        return df

    def main(self) -> pd.DataFrame:
        """Main function

        Returns:
            pd.DataFrame: pandas dataframe containing parsed data
        """

        soup_homepage = self.get_content(self.base_url)
        property_type_dict = self.get_property_type(soup_homepage)

        regions = self.get_regions(soup_homepage)

        result_json: List[Dict] = []

        for prop_type, prop_type_url in property_type_dict.items():
            for region in regions:
                # extract data from every section to find total nbr of pages - avoid requesting the same page twice
                url = self.base_url + prop_type_url + "/" + region['uri']

                soup = self.get_content(url)

                result_json.extend(self.extract_content(soup, prop_type, region["name"]))

                last_page = self.get_lastpage(soup)
                
                logger.info(f"Parsing data from region: {region['name']}, type: {prop_type}. Total pages: {last_page}, url: {url}.")
                i = 1
                while last_page > 1 and i <= (last_page - 1):
                    i += 1
                    url_for_loop = url + '?page=' + str(i)
                    soup = self.get_content(url_for_loop)

                    result_json.extend((self.extract_content(soup, prop_type, region["name"])))

                    time.sleep(0.5)
        return self.create_df(result_json)
