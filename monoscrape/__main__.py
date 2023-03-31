import argparse
import pathlib

from monoscrape import ItemDocument, fetch_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape monoprice.com for info on all items",
        prog="monoscrape",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--fetch-size",
        "-s",
        type=int,
        default=10000,
        help="How many items to fetch at a time. Also used as a cue to know when we have run out of items.",
    )
    parser.add_argument(
        "--max-product-id",
        "-m",
        type=int,
        default=1000000,
        help="Max product id to scrape.",
    )
    parser.add_argument(
        "--out-file",
        "-o",
        type=pathlib.Path,
        default="items.json",
        help="The file to overwrite our results to.",
    )
    parser.add_argument(
        "--max-workers", "-w", type=int, default=8, help="The number of workers to use."
    )
    parser.add_argument(
        "--merge",
        "-M",
        action="store_true",
        help="Merge the results with whatever is in the existing output file.",
    )
    parser.add_argument(
        "--update-range-start",
        "-us",
        type=int,
        default=None,
        help="Start (inclusive) of the range to update. The update range works with --merge to clear an existing range from the file before adding the new results.",
    )
    parser.add_argument(
        "--update-range-end",
        "-ue",
        type=int,
        default=None,
        help="End (non inclusive) of the range to update. The update range works with --merge to clear an existing range from the file before adding the new results.",
    )
    args = parser.parse_args()

    if (
        args.update_range_start is not None
        and args.update_range_end is None
        or args.update_range_start is None
        and args.update_range_end is not None
    ):
        raise ValueError(
            "If you specify a update range start or end, you must specify both"
        )

    results = fetch_all(args.fetch_size, args.max_product_id, args.max_workers)
    print(f"Found: {len(results)} items.. dumping them to: {args.out_file}")

    i = ItemDocument()
    if args.merge:
        i.update_with_items_from(args.out_file)

    if args.update_range_start is not None:
        i.remove_range(args.update_range_start, args.update_range_end)
    i.update_with_items_from(ItemDocument(results))

    i.dump(args.out_file)
