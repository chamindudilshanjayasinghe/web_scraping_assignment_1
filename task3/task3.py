import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from datetime import datetime

# Cities you want to track
CITIES = [
    "stockholm", "gothenburg", "malmo", "uppsala", "orebro",
    "vasteras", "linkoping", "helsingborg", "jonkoping", "norrkoping",
    "falun", "borlange"
]

def scrape_timeanddate(city):
    """Try to scrape weather from timeanddate.com"""
    try:
        url = f"https://www.timeanddate.com/weather/sweden/{city}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if response.status_code == 404:
            raise ValueError("404 Not Found")

        soup = BeautifulSoup(response.text, "html.parser")

        temp_tag = soup.find("div", class_="h2")
        cond_tag = soup.find("div", id="qlook")

        if not temp_tag or not cond_tag:
            raise ValueError("No weather data found")

        temp = temp_tag.get_text(strip=True)
        condition = cond_tag.find("p").get_text(strip=True)

        return {"site": "TimeAndDate", "city": city, "temperature": temp, "condition": condition}
    except Exception as e:
        return {"site": "TimeAndDate", "city": city, "error": str(e)}

def scrape_wunderground(city):
    """Scrape weather from wunderground.com"""
    try:
        url = f"https://www.wunderground.com/weather/se/{city}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if response.status_code == 404:
            raise ValueError("404 Not Found")

        soup = BeautifulSoup(response.text, "html.parser")

        temp_tag = soup.find("span", class_="wu-value wu-value-to")
        cond_tag = soup.find("div", class_="condition-icon")

        if not temp_tag or not cond_tag:
            raise ValueError("No weather data found")

        temp = temp_tag.get_text(strip=True)
        condition = cond_tag.get_text(strip=True)

        return {"site": "Wunderground", "city": city, "temperature": temp, "condition": condition}
    except Exception as e:
        return {"site": "Wunderground", "city": city, "error": str(e)}

def get_weather(city):
    """Try TimeAndDate first, fallback to Wunderground if error"""
    result = scrape_timeanddate(city)
    if "error" in result:
        print(f"⚠️ {city.capitalize()}: TimeAndDate failed ({result['error']}). Trying Wunderground...")
        result = scrape_wunderground(city)
    return result

def save_to_file(filename, weather_data):
    """Save results to text file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Weather Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        for data in weather_data:
            f.write(f"City: {data['city'].capitalize()}\n")
            f.write(f"Source: {data['site']}\n")
            if "error" in data:
                f.write(f"Error: {data['error']}\n")
            else:
                f.write(f"Temperature: {data['temperature']}\n")
                f.write(f"Condition: {data['condition']}\n")
            f.write("-"*50 + "\n")
    print(f"✅ Task 3 completed. Results saved to {filename}")

if __name__ == "__main__":
    results = []
    for city in CITIES:
        print(f"🌍 Scraping {city.capitalize()}...")
        results.append(get_weather(city))

    save_to_file("task3.txt", results)
