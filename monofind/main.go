package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"sort"
	"strings"

	"github.com/csm10495/monoscrape/monoscrapelib"
)

func getLatestItems() *monoscrapelib.ItemDocument {
	resp, err := http.Get("https://raw.githubusercontent.com/csm10495/monoscrape/master/items.json")
	if err != nil {
		panic("Err getting latest items (Get): " + err.Error())
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		panic("Err reading latest items (ReadAll): " + err.Error())
	}

	file, err := os.CreateTemp("", "items*.json")
	if err != nil {
		panic("Err creating temp file: " + err.Error())
	}

	defer func() {
		file.Close()
		os.Remove(file.Name())
	}()

	_, err = file.Write(data)
	if err != nil {
		panic("Err writing to temp file: " + err.Error())
	}

	ret := monoscrapelib.NewItemDocumentWithIntComparator()
	ret.UpdateWithItemsFromFile(file.Name())
	return ret
}

type keywordsType []string

func (i *keywordsType) String() string {
	return "my string representation"
}

func (i *keywordsType) Set(value string) error {
	*i = append(*i, value)
	return nil
}

func main() {
	var keywords keywordsType

	flag.Var(&keywords, "k", "Keywords to search for")
	showNonAvailable := flag.Bool("show-non-available", false, "Show non-available matching items too")
	showRatings := flag.Bool("show-ratings", false, "Show ratings in listings too")
	flag.Parse()

	if len(keywords) == 0 {
		panic("No keyword provided")
	}

	latestItems := getLatestItems()
	matchingItems := make([]*monoscrapelib.Item, 0)

	for _, itemAny := range latestItems.Items.Values() {
		item := itemAny.(monoscrapelib.Item)
		if item.Available || *showNonAvailable {
			addItem := true
			for _, keyword := range keywords {
				if !strings.Contains(strings.ToLower(item.Name), strings.ToLower(keyword)) {
					addItem = false
					break
				}
			}

			if addItem {
				matchingItems = append(matchingItems, &item)
			}
		}
	}

	sort.Slice(matchingItems, func(i, j int) bool {
		return matchingItems[i].Price < matchingItems[j].Price
	})

	fmt.Println("Showing", len(matchingItems), "matching item(s)")

	for _, item := range matchingItems {
		if *showRatings {
			fmt.Printf("$%.02f | %.1f stars | %s | %s\n", item.Price, item.Rating, item.Name, item.Url)
		} else {
			fmt.Printf("$%.02f | %s | %s\n", item.Price, item.Name, item.Url)
		}
	}

}
