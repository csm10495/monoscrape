package monoscrapelib

import (
	"fmt"
	"io"
	"math"
	"net/http"
	"strings"

	"github.com/alitto/pond"
	"github.com/anaskhan96/soup"
	"github.com/emirpasic/gods/maps/treemap"
)

func fetchOne(productId int) *Item {
	url := fmt.Sprintf("https://www.monoprice.com/product?p_id=%d", productId)
	resp, err := http.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		panic("Err reading?: " + err.Error())
	}

	doc := soup.HTMLParse(string(body))

	if strings.Contains(doc.FullText(), "looking for is no longer available") {
		return nil
	}

	i := &Item{
		Name:       strings.TrimSpace(doc.Find("div", "class", "product-name").Text()),
		Price:      getPrice(doc),
		Url:        url,
		ProductID:  productId,
		Available:  strings.Contains(doc.FullText(), "Add to Cart"),
		Rating:     getRating(doc),
		NumReviews: getNumReviews(doc),
	}
	fmt.Printf("%+v\n", i)
	return i
}

func fetchX(minProductId, maxProductId int) *treemap.Map {
	items := treemap.NewWithIntComparator()

	pool := pond.New(128, 100)
	channel := make(chan *Item)

	go func() {
		for i := minProductId; i < maxProductId; i++ {
			// copy i to n for closure.
			n := i
			pool.Submit(func() {
				if one := fetchOne(n); one != nil {
					channel <- one
				}
			})
		}

		pool.StopAndWait()
		close(channel)
	}()

	for item := range channel {
		items.Put(item.ProductID, item)
	}

	return items
}

func FetchAll(minProductId, maxProductId, fetchSize int) *treemap.Map {
	items := treemap.NewWithIntComparator()

	for productId := minProductId; productId < maxProductId; productId += fetchSize {
		tempItems := fetchX(productId, int(math.Min(float64(fetchSize+productId), float64(maxProductId))))

		if tempItems.Size() == 0 {
			fmt.Printf("No items found during fetchX(%d, {min(%d, %d)}).. stopping\n", productId, fetchSize+productId, maxProductId)
			break
		}

		for _, key := range tempItems.Keys() {
			x, _ := tempItems.Get(key)
			items.Put(key, x)
		}
	}

	return items
}
