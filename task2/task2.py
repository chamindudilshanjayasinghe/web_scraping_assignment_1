import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

def scrape_elgiganten():
    """
    Scrape product names and prices from Elgiganten search results.
    Uses <a data-testid="product-card"> and parses the 'data-item' attribute.
    """
    url = "https://www.elgiganten.se/datorer-kontor/datorer/laptop?redirectquery=laptop"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Select all product cards
    products = soup.find_all("a", {"data-testid": "product-card"})

    results = []
    for product in products:
        data_item = product.get("data-item", "")
        if not data_item:
            continue

        # Parse querystring style data-item
        parsed = urllib.parse.parse_qs(data_item)

        # Extract name and price
        name = parsed.get("item_name", ["No name"])[0].replace("+", " ")
        price = parsed.get("price", ["No price"])[0]

        results.append([name, price])

    # Save to CSV
    with open("task2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product Name", "Price"])
        writer.writerows(results)

    print(f"✅ Task 2 completed. {len(results)} products saved to task2.csv")


if __name__ == "__main__":
    scrape_elgiganten()
