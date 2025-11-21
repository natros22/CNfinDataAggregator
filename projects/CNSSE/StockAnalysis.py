
import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# --- Shanghai tickers ---
tickers = [  
"600000",
"600004",
"600006",
"600007",
"600008",
"600009",
"600010",
"600011",
"600012",
"600015",
"600016",
"600017",
"600018",
"600019",
"600020",
"600021",
"600022",
"600023",
"600025",
"600026",
"600027",
"600028",
"600029",
"600030",
"600031",
"600032",
"600033",
"600035",
"600036",
"600037",
"600038",
"600039",
"600048",
"600050",
"600051",
"600052",
"600053",
"600054",
"600055",
"600056",
"600057",
"600058",
"600059",
"600060",
"600061",
"600062",
"600063",
"600064",
"600066"
]

# --- Output file ---
output_file = "shanghai_stock_ceo_company_data_36.csv"

# --- HTTP headers ---
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36"
    )
}

# --- Build URL for company page ---
def get_company_url(ticker):
    return f"https://stockanalysis.com/quote/sha/{ticker}/company"

# --- Extract data from page ---
def extract_company_info(soup):
    info = {
        "company_name": "",
        "ticker": "",
        "ceo_name": "",
        "all_px1_values": "",
        "td_pb3": "",
        "td_px_values": ""
    }

    # --- Company name ---
    name_tag = soup.find("h1")
    if name_tag:
        info["company_name"] = name_tag.get_text(strip=True)
    elif soup.title:
        info["company_name"] = soup.title.get_text(strip=True)

    # --- All <td class="px-1 py-1.5 text-right lg:py-2"> (keep first 6 only) ---
    td_px1s = soup.select("td.px-1.py-1\\.5.text-right.lg\\:py-2")
    px1_values = [td.get_text(strip=True) for td in td_px1s if td.get_text(strip=True)]
    info["all_px1_values"] = "; ".join(px1_values[:6])  # limit to first 6 values

    # --- <td class="pb-3"> ---
    td_pb3 = soup.select_one("td.pb-3")
    info["td_pb3"] = td_pb3.get_text(strip=True) if td_pb3 else ""

    # --- All <td class="px-0.5 py-2 text-right"> ---
    td_px05s = soup.select("td.px-0\\.5.py-2.text-right")
    px05_values = [td.get_text(strip=True) for td in td_px05s if td.get_text(strip=True)]
    info["td_px_values"] = "; ".join(px05_values)

    # --- CEO name (from “Key Executives” table) ---
    try:
        for td in soup.find_all("td"):
            if td.get_text(strip=True).upper() == "CEO":
                prev_td = td.find_previous_sibling("td")
                if prev_td:
                    info["ceo_name"] = prev_td.get_text(strip=True)
                    break
    except Exception as e:
        print(f"CEO parsing error: {e}")

    return info


# --- Main scraping loop ---
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "ticker", "company_name", "ceo_name",
        "all_px1_values", "td_pb3", "td_px_values"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for ticker in tickers:
        url = get_company_url(ticker)
        print(f"Scraping {ticker}: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                data = extract_company_info(soup)
                data["ticker"] = ticker
                writer.writerow(data)
                print(f"Saved {ticker}")
            else:
                print(f"{ticker}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {ticker}: {e}")

        # --- Wait between requests (2–5 seconds) ---
        wait_time = random.uniform(5, 7)
        print(f"Waiting {wait_time:.1f} seconds before next request...")
        time.sleep(wait_time)

print(f"\n Done! Data saved to '{output_file}'")
