import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

tickers = ["600000",
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

BASE_URL = "https://markets.ft.com/data/equities/tearsheet/profile?s={}:SHH"
print(BASE_URL)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

profiles = []
peers_all = []

for ticker in tickers:
    print(f"Fetching {ticker} ...")
    url = BASE_URL.format(ticker)
    print(url)
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code != 200:
        print(f"Failed to fetch {ticker} profile page, HTTP {resp.status_code}")
        continue
    
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract company name
    company_name_tag = soup.select_one(".mod-tearsheet-overview__header__name--large")
    company_name = company_name_tag.text.strip() if company_name_tag else "N/A"
    print(company_name)

    data_items = []
    #Extract revenue in cny 
    ul = soup.select_one(".mod-tearsheet-profile-stats")
    if ul:
    # Then select all <li> inside that ul
        list_items = ul.select("li")

        for li in list_items:
            label = li.select_one(".mod-ui-data-list__label")
            value = li.select_one(".mod-ui-data-list__value")
            value_clean = value.text.strip()
            if label and value:
                item = {
                    #value.text.strip().replace("{", "").replace("}", "").replace("'", "").replace('"', '')
                    value.text.strip()
                }
                data_items.append(item)
                print(f"{label.text.strip()} : {value.text.strip()}")
    if len(data_items) < 3:
        print(f"Skipping {ticker} due to missing profile data.")
        continue  # Skip to the next ticker in the loop

    #Extract website 
    website_tag = soup.select_one('.mod-tearsheet-profile-section li.mod-tearsheet-profile__info--stacked a')
    website = website_tag.text.strip() if website_tag else "N/A"
    print(website)

    # Extract overview data (incorporated, employees, revenue, net income, website)
    profile_data = {
        "Ticker": ticker,
        "Company Name": company_name,
        "Revenue (CNY) (TTM)": data_items[0],
        "Net Income (CNY)": data_items[1],
        "Incorporated": data_items[2],
        "Employees": data_items[3],
        "Website": website,
        #"URL": url
    }
    print(type(data_items[0]))
    profiles.append(profile_data)

    # Extract peer data
    peer_table = soup.select_one(".mod-ui-table--freeze-pane__container")
    
    if peer_table:
        peer_rows = peer_table.find_all("tr")[1:]  # skip header
        for row in peer_rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                peers_all.append({
                    "Ticker": ticker,
                    "Peer Company": cols[0].text.strip(),
                    "Revenue (TTM)": cols[1].text.strip(),
                    "Net Income (TTM)": cols[2].text.strip(),
                    "Market Cap": cols[3].text.strip(),
                    "Employees": cols[4].text.strip()
                })
    else:
        print(f"No peer data found for {ticker}")
    print(ticker, cols[0].text.strip())

    time.sleep(1)  # polite delay

# Save to CSV
pd.DataFrame(profiles).to_csv("ft_company_profiles1.csv", index=False)
pd.DataFrame(peers_all).to_csv("ft_peer_analysis1.csv", index=False)

#print("Saved ft_company_profiles.csv and ft_peer_analysis.csv")
