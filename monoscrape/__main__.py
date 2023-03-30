import argparse
import pathlib

from monoscrape import fetch_all, Item

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape monoprice.com for info on all items', prog='monoscrape', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fetch-size', '-s', type=int, default=10000, help='How many items to fetch at a time. Also used as a cue to know when we have run out of items.')
    parser.add_argument('--max-product-id', '-m', type=int, default=1000000, help='Max product id to scrape.')
    parser.add_argument('--out-file', '-o', type=pathlib.Path, default='items.json', help='The file to overwrite our results to.')
    parser.add_argument('--max-workers', '-w', type=int, default=8, help='The number of workers to use.')
    args = parser.parse_args()

    results = fetch_all(args.fetch_size, args.max_product_id, args.max_workers)
    print(f"Found: {len(results)} items.. dumping them to: {args.out_file}")
    Item.dump_item_list_to_file(results, args.out_file)
