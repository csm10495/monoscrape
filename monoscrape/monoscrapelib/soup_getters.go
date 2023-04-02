package monoscrapelib

import (
	"strconv"
	"strings"

	"github.com/anaskhan96/soup"
)

func getRating(doc soup.Root) float32 {
	node := doc.Find("span", "id", "TTreviewSummaryAverageRating")
	if node.Error != nil {
		return 0.0
	}

	ratingStr := strings.TrimSpace(strings.Split(strings.TrimSpace(node.Text()), "/")[0])
	rating, err := strconv.ParseFloat(ratingStr, 32)
	if err != nil {
		panic("Err parsing rating: " + err.Error())
	}

	return float32(rating)
}

func getNumReviews(doc soup.Root) int {
	node := doc.Find("div", "class", "TTreviewCount")
	if node.Error != nil {
		return 0
	}

	numReviewStr := strings.TrimSpace(strings.Split(strings.TrimSpace(node.Text()), " ")[0])
	numReviews, err := strconv.Atoi(strings.ReplaceAll(numReviewStr, ",", ""))
	if err != nil {
		panic("Err parsing num reviews: " + err.Error())
	}
	return numReviews
}

func getPrice(doc soup.Root) float32 {
	node := doc.Find("span", "class", "sale-price")
	if node.Error != nil {
		panic("No price found?")
	}

	priceTrimd := strings.TrimSpace(node.Text())
	noDolla := strings.ReplaceAll(priceTrimd, "$", "")
	noComma := strings.ReplaceAll(noDolla, ",", "")
	price, err := strconv.ParseFloat(noComma, 32)
	if err != nil {
		panic("Err parsing price: " + err.Error())
	}
	return float32(price)
}
