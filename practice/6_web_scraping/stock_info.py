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
from typing import Iterable, Mapping

USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
MOST_ACTIVE_STOCKS_URL = "https://finance.yahoo.com/markets/stocks/most-active"
STOCK_PROFILE_TAB_URL = "https://finance.yahoo.com/quote/{code}/profile"
STOCK_WEEK_CHANGE_TAB_URL = "https://finance.yahoo.com/markets/stocks/52-week-gainers"
STOCK_STATISTICS_TAB_URL = "https://finance.yahoo.com/quote/{code}/key-statistics"
STOCK_HOLDERS_TAB_URL = "https://finance.yahoo.com/quote/BLK/holders"

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

def get_youngest_ceos_data() -> list[dict]:
    stock_codes = get_stock_codes_from_all_pages()
    all_data = []
    for code, name in stock_codes.items():
        soup = make_request(STOCK_PROFILE_TAB_URL.format(code=code))
        table = soup.find('table', class_="yf-mj92za")
        CEO = re.compile(r'\bCEO\b', re.I)
        ceo_role = table.find('td', string=lambda s: isinstance(s, str) and CEO.search(s)) if table else None

        if ceo_role:
            ceo_row = ceo_role.find_parent('tr')
            ceo_data = ceo_row.find_all('td')
            ceo_name = ceo_data[0].text.strip()
            ceo_year = ceo_data[-1].text.strip()

            if ceo_year.isdigit():
                country_element = soup.find("div", class_="address yf-wxp4ja")
                country = country_element.find_all("div")[-1].text.strip() if country_element and country_element.find_all("div") else "--"

                employees_count = soup.find("dl", class_="company-stats yf-wxp4ja")
                employees = employees_count.find("strong").text.strip() if employees_count and employees_count.find("strong") else "--"

                data = {
                    "Name": name,
                    "Code": code,
                    "Employees": employees,
                    "Country": country,
                    "CEO Name": ceo_name,
                    "CEO Year Born": ceo_year
                }
                all_data.append(data)

    return sorted(all_data, key=lambda x: int(x["CEO Year Born"]), reverse=True)[:5]

def get_best_52_week_change_data() -> list[dict]:
    soup = make_request(STOCK_WEEK_CHANGE_TAB_URL)
    rows = soup.find_all("tr", class_="row yf-1m4mc7b")
    all_data = []

    for row in rows[:10]:
        code = row.find("span", class_="symbol yf-90gdtp")
        name = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")
        week_change_column = row.find_all("td")[-2]
        week_change = week_change_column.find("span", class_="txt-positive")
        total_cash = None

        if code and name and week_change:
            stats_soup = make_request(STOCK_STATISTICS_TAB_URL.format(code=code.text.strip()))
            all_sections = stats_soup.find_all("section", class_="yf-14j5zka")
            financial_highlights_section = all_sections[0]
            financial_highlights_tables = financial_highlights_section.find_all("table", class_="table yf-vaowmx")
            balance_sheet_table = financial_highlights_tables[-2]

            if balance_sheet_table:
                total_cash_row = balance_sheet_table.find('tr')
                total_cash = total_cash_row.find_all('td')[1].text.strip() if total_cash_row else None

            data = {
                "Name": name.text.strip(),
                "Code": code.text.strip(),
                "52-Week Change": week_change.text.strip(),
                "Total Cash": total_cash if total_cash else "--"
            }
            all_data.append(data)

    return all_data

def get_largest_blackrock_holds_data() -> list[dict]:
    all_data = []
    soup = make_request(STOCK_HOLDERS_TAB_URL)
    top_institutional_holders_section = soup.find("section", attrs={"data-testid": "holders-top-institutional-holders"})
    holders_table = top_institutional_holders_section.find("table", class_="yf-idy1mk")
    holders_table_body = holders_table.find("tbody")
    rows = holders_table_body.find_all("tr", class_="yf-idy1mk")

    for row in rows:
        columns = row.find_all("td")
        if not columns or len(columns) < 5:
            continue
        holder_name = columns[0].text.strip()
        shares = columns[1].text.strip()
        date_reported = columns[2].text.strip()
        out = columns[3].text.strip()
        value = columns[4].text.strip()

        all_data.append({
            "Name": holder_name,
            "Shares": shares,
            "Date Reported": date_reported,
            "% Out": out,
            "Value": value
        })

    return all_data


COLUMNS_CEOS = ["Name", "Code", "Country", "Employees", "CEO Name", "CEO Year Born"]
COLUMNS_WEEK_CHANGE = ["Name", "Code", "52-Week Change", "Total Cash"]
COLUMNS_BLACKROCK = ["Name", "Shares", "Date Reported", "% Out", "Value"]
CEOS_TITLE = "5 stocks with most youngest CEOs"
WEEK_CHANGE_TITLE = "10 stocks with best 52-Week Change"
BLACKROCK_TITLE = "10 largest holds of Blackrock Inc."

def _coerce(val) -> str:
    return "" if val is None else str(val)

def format_sheet(columns: list[str], title: str, rows: Iterable[Mapping[str, object]]) -> str:
    rows = list(rows)
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(_coerce(row.get(col, ""))))

    def render_row(values: Mapping[str, object]) -> str:
        parts = []
        for col in columns:
            parts.append(f"| {_coerce(values.get(col, '')).ljust(widths[col])} ")
        return "".join(parts) + "|"

    header_row = render_row({c: c for c in columns})
    sep_row = "-" * len(header_row)

    title_row = title.center(len(header_row), "=")
    data_rows = [render_row(r) for r in rows]

    sheet = [title_row, header_row, sep_row, *data_rows, ""]
    return "\n".join(sheet) + "\n"
