import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, List

import requests
import roman
from bs4 import BeautifulSoup, Tag

headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"}


class Estate:
    def __init__(self, price: int, district: int, street: str, area: int, rooms: int, half_rooms: int,
                 url: str) -> None:
        self.price = price
        self.district = district
        self.street = street
        self.area = area
        self.rooms = rooms
        self.half_rooms = half_rooms
        self.url = url

    def __iter__(self):
        return iter([self.district, self.street, self.price, self.area, self.rooms, self.half_rooms, self.url])


def parse_page(url) -> Tuple[list, Optional[str]]:
    data = requests.get(url, headers=headers).content
    soup = BeautifulSoup(data, "html.parser")
    offers = soup.find_all("div", class_="listing__card")
    next_url = soup.select("a.pagination__button")[-1]
    return offers, next_url.attrs['href'] if next_url and next_url.text.startswith("Következő") else None


def paginate_query(url: str) -> List[Estate]:
    while url:
        print("Parsing {0} ...".format(url))
        estates, url = parse_page(url)
        yield map(convert_estate, estates)


def convert_estate(estate: Tag) -> Estate:
    address = estate.select_one('div.listing__address').text.split(',')
    rooms = list(map(int, re.findall("\d+", estate.select_one('div.listing__data--room-count').text)))
    price_div = estate.select_one('div.price')
    return Estate(
        price=int(float(price_div.text.strip().split()[0]) * 1e6) if price_div else 0,
        district=roman.fromRoman(address[-1].split(".")[0].strip()),
        street=address[0].strip(),
        area=int(estate.select_one('div.listing__data--area-size').text.split()[0]),
        rooms=rooms[0],
        half_rooms=rooms[1] if len(rooms) > 1 else 0,
        url=estate.select_one('a.listing__link').attrs['href']
    )


if len(sys.argv) < 3:
    print("Usage {0} <url> <output dir> [csv_prefix]".format(sys.argv[0]))
    sys.exit(1)

output_dir = Path(sys.argv[2])  
csv_prefix = sys.argv[3] if len(sys.argv) > 3 else "output"
out_file_name = "{0}_{1}.csv".format(csv_prefix, datetime.now().strftime("%Y%m%d_%H%M"))
try:
    with (output_dir / out_file_name).open("w+") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        estates_url = sys.argv[1]
        for estate_chunk in paginate_query(estates_url):
            writer.writerows(list(estate_chunk))
            csv_file.flush()
        print("Done.")
except KeyboardInterrupt:
    print("Aborted.")
