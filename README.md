# Monoscrape

A scraper to json for monoprice.com.

## Note
I am not affiliated with monoprice.com. This was just a pet project of mine since their search seems to miss items.

# Example

```
python -m monoscrape --help
usage: monoscrape [-h] [--fetch-size FETCH_SIZE] [--max-product-id MAX_PRODUCT_ID] [--out-file OUT_FILE]
                  [--max-threads MAX_THREADS]

Scrape monoprice.com for info on all items

options:
  -h, --help            show this help message and exit
  --fetch-size FETCH_SIZE, -s FETCH_SIZE
                        How many items to fetch at a time. Also used as a cue to know when we have run out of items.
                        (default: 10000)
  --max-product-id MAX_PRODUCT_ID, -m MAX_PRODUCT_ID
                        Max product id to scrape. (default: 1000000)
  --out-file OUT_FILE, -o OUT_FILE
                        The file to overwrite our results to. (default: items.json)
  --max-threads MAX_THREADS, -t MAX_THREADS
                        The number of threads to use. (default: 8)
```
