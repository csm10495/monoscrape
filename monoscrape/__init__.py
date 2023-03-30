from __future__ import annotations
from functools import cache
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
import pathlib

from threading import Lock

_printLock = Lock()
__version__ = '0.0.1'


@dataclass
class Item:
    """
    Represents a single item on monoprice.com
    """
    name: str
    price: float
    url: str
    product_id: int
    available: bool
    rating: float
    num_reviews: int

    @classmethod
    def dump_item_list_to_file(cls, items: list[Item], out_file: str) -> None:
        """
        Takes a list of items and dumps it as json to the given out_file
        """
        pathlib.Path(out_file).write_text(json.dumps([asdict(i) for i in items], indent=4))

    @classmethod
    def load_item_list_from_file(cls, in_file: str) -> list[Item]:
        """
        Takes in an in_file of json and returns a list of items"""
        data = pathlib.Path(in_file).read_text()
        return [Item(**i) for i in json.loads(data)]

@cache
def __fetch(product_id: int) -> Item | None:
    """
    Does a single fetch of info for a given product_id. Will return None, if the product isn't found.
    """
    result = requests.get(f'https://www.monoprice.com/product?p_id={product_id}')
    if result.status_code != 200:
        return None

    soup = BeautifulSoup(result.text, 'html.parser')
    if 'The product you’re looking for is no longer available' in soup.text:
        return None

    try:
        rating = float(soup.find('span', id='TTreviewSummaryAverageRating').text.strip().split('/')[0].strip())
    except:
        rating = 0

    try:
        num_reviews = int(soup.find('div', class_='TTreviewCount').text.strip().split(' ')[0].strip())
    except:
        num_reviews = 0

    try:
        ret = Item(name=soup.find('div', {'class': 'product-name'}).text.strip(),
                    price=float(soup.find('span', {'class': 'sale-price'}).text.strip().replace('$', '').replace(',', '')),
                    url=result.url,
                    product_id=product_id,
                    available=bool(soup.find('a', text='Add to Cart')),
                    rating=rating,
                    num_reviews=num_reviews)
    except AttributeError:
        return None

    return ret

def fetch(product_id: int) -> Item | None:
    """
    Does a single fetch of info for a given product_id. Will return None, if the product isn't found.

    Will print if an item is found.
    """
    ret = __fetch(product_id)
    if ret:
        with _printLock:
            print(f"Found item: {ret}")

    return ret

def fetch_x(starting_product_id: int, num_products: int, workers: int) -> list[Item]:
    """
    Fetches a range of products from starting_product_id to starting_product_id + num_products
    """
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return [a for a in pool.map(fetch, range(starting_product_id, starting_product_id + num_products)) if a]

def fetch_all(fetch_size: int, max_product_id: int, workers: int) -> list[Item]:
    """
    Fetches all items from monoprice.com
    """
    results = []
    try:
        for i in range(0, max_product_id + 1, fetch_size):
            if temp_results := fetch_x(i, min(fetch_size, max_product_id + 1), workers):
                results.extend(temp_results)
            else:
                print(f"No items found during fetch_x({i}, {min(fetch_size, max_product_id + 1)}).. stopping")
                break
    except KeyboardInterrupt:
        print (" -- Keyboard Interrupt -- Stopping --")

    return results
