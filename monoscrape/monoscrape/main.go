package main

import (
	"flag"

	"github.com/csm10495/monoscrape/monoscrapelib"
)

func main() {
	fetchSize := flag.Int("fetch-size", 10000, "How many items to fetch at a time. Also used as a cue to know when we have run out of items")
	minProductId := flag.Int("min-product-id", 0, "The minimum product id to fetch (inclusive)")
	maxProductId := flag.Int("max-product-id", 1000, "The maximum product id to fetch (non-inclusive)")
	outFile := flag.String("out-file", "items.json", "The file to write the output to")
	var merge bool
	flag.BoolVar(&merge, "merge", false, "Merge the items from the input file with the items from the fetch")
	flag.BoolVar(&merge, "m", false, "Merge the items from the input file with the items from the fetch")
	flag.Parse()

	items := monoscrapelib.FetchAll(*minProductId, *maxProductId, *fetchSize)

	i := monoscrapelib.NewItemDocumentWithIntComparator()
	if merge {
		i.UpdateWithItemsFromFile(*outFile)
	}

	i.RemoveRange(*minProductId, *maxProductId)
	i.UpdateWithItemsFromItemMap(items)

	i.Dump(*outFile)
}
