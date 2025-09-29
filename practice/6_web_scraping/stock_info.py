"""
There is a list of most active Stocks on Yahoo Finance https://finance.yahoo.com/most-active.
You need to compose several sheets based on data about companies from this list.
To fetch data from webpage you can use requests lib. To parse html you can use beautiful soup lib or lxml.
Sheets which are needed:
1. 5 stocks with most youngest CEOs and print sheet to output. You can find CEO info in Profile tab of concrete stock.
    Sheet's fields: Name, Code, Country, Employees, CEO Name, CEO Year Born.
2. 10 stocks with best 52-Week Change. 52-Week Change placed on Statistics tab.
    Sheet's fields: Name, Code, 52-Week Change, Total Cash
3. 10 largest holds of Blackrock Inc. You can find related info on the Holders tab.
    Blackrock Inc is an investment management corporation.
    Sheet's fields: Name, Code, Shares, Date Reported, % Out, Value.
    All fields except first two should be taken from Holders tab.


Example for the first sheet (you need to use same sheet format):
==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |
...

About sheet format:
- sheet title should be aligned to center
- all columns should be aligned to the left
- empty line after sheet

Write at least 2 tests on your choose.
Links:
    - requests docs: https://docs.python-requests.org/en/latest/
    - beautiful soup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - lxml docs: https://lxml.de/
"""
import requests
import re
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
MOST_ACTIVE_STOCKS_URL = "https://finance.yahoo.com/markets/stocks/most-active"
STOCK_PROFILE_TAB_URL = "https://finance.yahoo.com/quote/{code}/profile"

def make_request(url: str) -> BeautifulSoup:
    page = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    if page.status_code == 200:
        return BeautifulSoup(page.content, "html.parser")
    else:
        raise Exception(f"Failed to fetch the data from {url}")

def get_stock_codes_from_page(soup: BeautifulSoup) -> dict:
    rows = soup.find_all("tr", class_="row yf-1m4mc7b")
    stock_codes = {}

    for row in rows:
        code = row.find("span", class_="symbol yf-90gdtp")
        company = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")

        if code and company:
            stock_codes[code.text.strip()] = company.text.strip()

    return stock_codes

def get_stock_codes_from_all_pages() -> dict:
    all_stocks = {}
    start = 0
    count = 200

    while True:
        url = f"{MOST_ACTIVE_STOCKS_URL}?start={start}&count={count}"
        soup = make_request(url)
        page_stocks = get_stock_codes_from_page(soup)

        if not page_stocks:
            break

        all_stocks.update(page_stocks)
        if len(page_stocks) < count:
            break

        start += count

    return all_stocks

def get_youngest_ceos_data(stock_codes: dict) -> int:
    all_data = []
    for code, name in stock_codes.items():
        soup = make_request(STOCK_PROFILE_TAB_URL.format(code=code))
        table = soup.find('table', class_="yf-mj92za")
        CEO = re.compile(r'\bCEO\b', re.I)
        ceo_role = table.find('td', string=lambda s: isinstance(s, str) and CEO.search(s)) if table else None
        data = {}

        if ceo_role:
            ceo_row = ceo_role.find_parent('tr')
            ceo_data = ceo_row.find_all('td')
            ceo_name = ceo_data[0].text.strip()
            ceo_year = ceo_data[-1].text.strip()

            if ceo_year.isdigit():
                country_element = soup.find("div", class_="address yf-wxp4ja")
                country = country_element.find_all("div")[-1].text.strip() if country_element and country_element.find_all("div") else "N/A"

                employees_count = soup.find("dl", class_="company-stats yf-wxp4ja")
                employees = employees_count.find("strong").text.strip() if employees_count and employees_count.find("strong") else "N/A"

                data["Name"] = name
                data["Code"] = code
                data["Employees"] = employees
                data["Country"] = country
                data["CEO Name"] = ceo_name
                data["CEO Year Born"] = ceo_year
                all_data.append(data)

    return sorted(all_data, key=lambda x: int(x["CEO Year Born"]), reverse=True)[:5]


stock = get_stock_codes_from_all_pages()
print(get_youngest_ceos_data(stock))
