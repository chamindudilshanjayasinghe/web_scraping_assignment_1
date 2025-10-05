import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

BASE_URL = "https://www.geeksforgeeks.org"

def get_article_links():
    """
    Scrape all article links and titles from the AI intro page's popular grid container
    using only requests + BeautifulSoup.
    """
    url = "https://www.geeksforgeeks.org/introduction-to-artificial-intelligence/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.select(".popular-grid-container .popular-grid-item a")
    article_list = []
    for link in links:
        title = link.get_text(strip=True)
        href = link["href"]
        if not href.startswith("http"):
            href = BASE_URL + href
        article_list.append((title, href))
    return article_list


def scrape_article_details(url):
    """
    Scrape headline, last updated, and description from an article page.
    """
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    # Headline
    headline_tag = soup.find("h1")
    headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"

    # Last updated
    last_updated = "Not found"
    parent = soup.find("div", class_="last_updated_parent")
    if parent:
        spans = parent.find_all("span")
        if len(spans) >= 2:
            last_updated = spans[1].get_text(strip=True)

    # Description
    ps = soup.find_all("p", attrs={"dir": "ltr"})
    description = " ".join([p.get_text(" ", strip=True) for p in ps])

    return {
        "headline": headline,
        "last_updated": last_updated,
        "description": description
    }


def save_to_file(filename, articles):
    """
    Save scraped results into a text file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for title, link, details in articles:
            f.write(f"Link text: {title}\n")
            f.write(f"URL: {link}\n")
            f.write(f"Article headline: {details['headline']}\n")
            f.write(f"Last updated: {details['last_updated']}\n")
            f.write(f"Description: {details['description']}\n")
            f.write("=" * 70 + "\n\n")


if __name__ == "__main__":
    article_links = get_article_links()
    print(f"✅ Found {len(article_links)} articles in the grid section.")

    scraped_articles = []
    for (title, link) in article_links:
        print(f"➡️ Scraping: {title}")
        details = scrape_article_details(link)
        scraped_articles.append((title, link, details))

    save_to_file("task1.txt", scraped_articles)
    print("🎉 Task 1 completed. Results saved to task1.txt")
