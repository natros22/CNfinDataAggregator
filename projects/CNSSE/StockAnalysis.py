
import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# --- Shanghai tickers ---
tickers = [  

"688776", 
"688777", 
"688778", 
"688779", 
"688786", 
"688787", 
"688788", 
"688789", 
"688798", 
"688799", 
"688800", 
"688819", 
"688981", 
"689009", 
"900901", 
"900902", 
"900903", 
"900904", 
"900905", 
"900906", 
"900908", 
"900909", 
"900910", 
"900911", 
"900912", 
"900913", 
"900914", 
"900915", 
"900916", 
"900917", 
"900918", 
"900920", 
"900921", 
"900922", 
"900923", 
"900924", 
"900925", 
"900926", 
"900927", 
"900929", 
"900932", 
"900934", 
"900936", 
"900937", 
"900938", 
"900939", 
"900940", 
"900941", 
"900942", 
"900943", 
"900945", 
"900946", 
"900947", 
"900948"
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
