#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "${SCRIPT_DIR}"

MIN_PRODUCT_ID=$(cat last_product_id.txt)
FETCH_SIZE=100
MAX_PRODUCT_ID=$((MIN_PRODUCT_ID + FETCH_SIZE))

cd monoscrape
go mod tidy
go build -o ../monoscrape-exe .

cd ..

./monoscrape-exe --merge \
    --fetch-size $FETCH_SIZE \
    --max-product-id $MAX_PRODUCT_ID \
    --min-product-id $MIN_PRODUCT_ID | tee log.txt

if [[ ${PIPESTATUS[0]} == 0 ]]; then
    if tail -n 5 log.txt | grep -q "No items found during fetch"; then
        echo "No items found.. resetting last_product_id.txt" >&2
        echo "0" > last_product_id.txt
    else
        echo "Setting last_product_id to: ${MAX_PRODUCT_ID}" >&2
        echo $MAX_PRODUCT_ID > last_product_id.txt
    fi
else
    echo "Monoscrape failed"
    exit 1
fi

#git add last_product_id.txt
#git add items.json

#git commit -m "Update items listings"
pwd
ls -la
rm log.txt
rm monoscrape-exe
#git pull --rebase origin master
#git push origin master

exit 0
