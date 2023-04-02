from __future__ import annotations

import datetime
import json
import pathlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import asdict, dataclass
from functools import cache
from multiprocessing import Lock

import backoff
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import TimeoutError

_printLock = Lock()
__version__ = "0.0.1"


def _int_keys_hook(obj):
    ret_dict = {}
    for key in obj:
        try:
            ret_dict[int(key)] = obj[key]
        except ValueError:
            ret_dict[key] = obj[key]

    return ret_dict


class ItemDocument:
    def __init__(self, items: dict[int, Item] | None = None):
        self._items = items or dict()

    def update_with_items_from(self, other: ItemDocument | str | pathlib.Path):
        if isinstance(other, ItemDocument):
            self._items.update(other._items)
        else:
            p = pathlib.Path(other)
            json_data = json.loads(p.read_text(), object_hook=_int_keys_hook)
            json_items = json_data["items"]
            self._items.update({k: Item(**v) for k, v in json_items.items()})

    def remove_range(self, start, end):
        for i in range(start, end):
            self._items.pop(i, None)

    def dump(self, out_file: pathlib.Path | str) -> str:
        out_file = pathlib.Path(out_file)

        out_file.write_text(
            json.dumps(
                {
                    "items": {k: asdict(v) for k, v in self._items.items()},
                    "meta": {
                        "version": __version__,
                        "timestamp": str(datetime.datetime.utcnow()),
                    },
                },
                indent=4,
            )
        )


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


@cache
@backoff.on_exception(
    backoff.constant,
    (TimeoutError, requests.exceptions.ConnectionError),
    max_tries=10,
    interval=3,
)
def __fetch(product_id: int) -> Item | None:
    """
    Does a single fetch of info for a given product_id. Will return None, if the product isn't found.
    """
    # with _printLock:
    #    print(f"FETCHING: {product_id}")

    result = requests.get(f"https://www.monoprice.com/product?p_id={product_id}")
    if result.status_code != 200:
        return None

    soup = BeautifulSoup(result.text, "html.parser")
    if "The product you’re looking for is no longer available" in soup.text:
        return None

    try:
        rating = float(
            soup.find("span", id="TTreviewSummaryAverageRating")
            .text.strip()
            .split("/")[0]
            .strip()
        )
    except:
        rating = 0

    try:
        num_reviews = int(
            soup.find("div", class_="TTreviewCount").text.strip().split(" ")[0].strip()
        )
    except:
        num_reviews = 0

    try:
        ret = Item(
            name=soup.find("div", {"class": "product-name"}).text.strip(),
            price=float(
                soup.find("span", {"class": "sale-price"})
                .text.strip()
                .replace("$", "")
                .replace(",", "")
            ),
            url=result.url,
            product_id=product_id,
            available=bool(soup.find("a", text="Add to Cart")),
            rating=rating,
            num_reviews=num_reviews,
        )
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


def fetch_multi(min_product_id: int, max_product_id: int) -> dict[int, Item]:
    """
    Fetches multiple items at once, and returns a dict of product_id to Item
    """
    ret = {}
    for product_id in range(min_product_id, max_product_id):
        item = fetch(product_id)
        if item:
            ret[product_id] = item

    return ret


def fetch_in_process(
    products_per_thread: int,
    min_product_id: int,
    max_product_id: int,
    threads_per_process: int,
) -> dict[int, Item]:
    # with _printLock:
    #    print(f"Fetching {min_product_id} to {max_product_id} in process")

    executions = []
    with ThreadPoolExecutor(max_workers=threads_per_process) as executor:
        for product_id in range(min_product_id, max_product_id, products_per_thread):
            executions.append(
                executor.submit(
                    fetch_multi,
                    min_product_id=product_id,
                    max_product_id=min(
                        product_id + products_per_thread, max_product_id
                    ),
                )
            )

        final_results = {}
        for r in executions:
            final_results.update(r.result())
        return final_results


def fetch_all(
    products_per_thread: int,
    products_per_process: int,
    min_product_id: int,
    max_product_id: int,
    processes: int,
    threads_per_process: int,
) -> dict[int, Item]:
    """
    Fetches all items from monoprice.com
    """
    executions = []
    with ProcessPoolExecutor(max_workers=processes) as executor:
        for product_id in range(min_product_id, max_product_id, products_per_process):
            executions.append(
                executor.submit(
                    fetch_in_process,
                    products_per_thread=products_per_thread,
                    min_product_id=product_id,
                    max_product_id=min(
                        product_id + products_per_process, max_product_id
                    ),
                    threads_per_process=threads_per_process,
                )
            )

        final_results = {}
        for r in executions:
            final_results.update(r.result())
        return final_results


"""
print(f"No items found during fetch_x({i}, {min(fetch_size, max_product_id)}).. stopping")
break
"""
