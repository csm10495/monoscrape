package monoscrapelib

import (
	"encoding/json"
	"os"
	"strconv"
	"time"

	"github.com/emirpasic/gods/maps/treemap"
)

type Item struct {
	Name       string  `json:"name"`
	Price      float32 `json:"price"`
	Url        string  `json:"url"`
	ProductID  int     `json:"product_id"`
	Available  bool    `json:"available"`
	Rating     float32 `json:"rating"`
	NumReviews int     `json:"num_reviews"`
}

type ItemDocumentMeta struct {
	Version   string `json:"version"`
	Timestamp string `json:"timestamp"`
}

func newItemDocumentMeta() *ItemDocumentMeta {
	return &ItemDocumentMeta{
		Version:   "0.0.1",
		Timestamp: time.Now().Format(time.RFC3339),
	}
}

type ItemDocument struct {
	Items *treemap.Map      `json:"items"`
	Meta  *ItemDocumentMeta `json:"meta"`
}

func NewItemDocumentWithIntComparator() *ItemDocument {
	return &ItemDocument{
		Items: treemap.NewWithIntComparator(),
		Meta:  newItemDocumentMeta(),
	}
}

func (id *ItemDocument) Dump(outFile string) {
	data, err := json.MarshalIndent(id, "", "    ")
	if err != nil {
		panic("Err marshaling: " + err.Error())
	}

	os.WriteFile(outFile, data, 0o644)
}

func (id *ItemDocument) RemoveRange(minProductId, maxProductId int) {
	for i := minProductId; i < maxProductId; i++ {
		id.Items.Remove(i)
	}
}

func (id *ItemDocument) UpdateWithItemsFromItemMap(itemMap *treemap.Map) {
	for _, key := range itemMap.Keys() {
		value, _ := itemMap.Get(key)
		keyAsInt, ok := key.(int)
		if !ok {
			// itemMap is using string keys.. make sure the key is an int when putting in id.Itmes
			var err error
			keyAsInt, err = strconv.Atoi(key.(string))
			if err != nil {
				panic("Err converting key to int: " + err.Error())
			}
		}

		id.Items.Put(keyAsInt, value)
	}
}

func (id *ItemDocument) UpdateWithItemsFromFile(inFile string) {
	data, err := os.ReadFile(inFile)
	if err != nil {
		panic("Err reading file: " + err.Error())
	}

	otherItemDocument := ItemDocument{
		// Remember when it comes from the file, keys with be strings
		Items: treemap.NewWithStringComparator(),
		Meta:  newItemDocumentMeta(),
	}

	if json.Unmarshal(data, &otherItemDocument) != nil {
		panic("Err unmarshaling: " + err.Error())
	}

	// i don't really know why, but it doesn't seem to automatically unmarshal each item
	// into an Item struct, so we have to do it manually
	for _, key := range otherItemDocument.Items.Keys() {
		val, _ := otherItemDocument.Items.Get(key)

		data, err := json.Marshal(val)
		if err != nil {
			panic("Err marshaling item: " + err.Error())
		}

		newItem := Item{}
		err = json.Unmarshal(data, &newItem)
		if err != nil {
			panic("Err unmarshaling item: " + err.Error())
		}

		otherItemDocument.Items.Put(key, newItem)
	}

	id.UpdateWithItemsFromItemMap(otherItemDocument.Items)
}
