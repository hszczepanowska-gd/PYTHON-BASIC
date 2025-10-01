import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup
import sys, pathlib, importlib.util

MODULE_PATH = pathlib.Path(__file__).with_name("stock_info.py")
spec = importlib.util.spec_from_file_location("stock_info", MODULE_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")

def _profile_html(country: str, employees: str, ceo_name: str, ceo_year: str) -> str:
    return f"""
    <html>
      <body>
        <table class="yf-mj92za">
          <tr><td>{ceo_name}</td><td>CEO</td><td>{ceo_year}</td></tr>
        </table>
        <div class="address yf-wxp4ja"><div>Some addr</div><div>{country}</div></div>
        <dl class="company-stats yf-wxp4ja"><strong>{employees}</strong></dl>
      </body>
    </html>
    """

def _week_gainers_html() -> str:
    return """
    <table><tbody>
      <tr class="row yf-1m4mc7b">
        <td><span class="symbol yf-90gdtp">AAA</span></td>
        <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">AAA Inc.</div></td>
        <td>...</td>
        <td><span class="txt-positive">+12.34%</span></td>
        <td>last</td>
      </tr>
      <tr class="row yf-1m4mc7b">
        <td><span class="symbol yf-90gdtp">BBB</span></td>
        <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">BBB Ltd.</div></td>
        <td>...</td>
        <td><span class="txt-positive">+3,799.21%</span></td>
        <td>last</td>
      </tr>
    </tbody></table>
    """

def _stats_html(total_cash: str) -> str:
    return f"""
    <section class="yf-14j5zka">
      <table class="table yf-vaowmx"><tr><td>RowLabel</td><td>{total_cash}</td></tr></table>
      <table class="table yf-vaowmx"><tr><td>Other</td><td>ignored</td></tr></table>
    </section>
    """

def _blk_holders_html() -> str:
    return """
    <section data-testid="holders-top-institutional-holders">
      <table class="yf-idy1mk">
        <tbody>
          <tr class="yf-idy1mk">
            <td>Vanguard Group</td><td>100,000,000</td><td>2025-06-30</td><td>5.00%</td><td>$10,000,000,000</td>
          </tr>
          <tr class="yf-idy1mk">
            <td>State Street</td><td>80,000,000</td><td>2025-06-30</td><td>4.00%</td><td>$8,000,000,000</td>
          </tr>
        </tbody>
      </table>
    </section>
    """

def test_get_youngest_ceos_data():
    codes = {"AAA": "AAA Inc.", "BBB": "BBB Ltd.", "CCC": "CCC SA"}
    def fake_make_request(url: str):
        if "/quote/AAA/profile" in url:
            return soup(_profile_html("USA", "100", "Alice A.", "1995"))
        if "/quote/BBB/profile" in url:
            return soup(_profile_html("Poland", "200", "Bob B.", "1980"))
        if "/quote/CCC/profile" in url:
            return soup(_profile_html("Germany", "150", "Carol C.", "1990"))
        raise AssertionError(f"Unexpected URL in test: {url}")

    with patch.object(m, "get_stock_codes_from_all_pages", return_value=codes), \
         patch.object(m, "make_request", side_effect=fake_make_request):
        rows = m.get_youngest_ceos_data()

    assert [r["Code"] for r in rows] == ["AAA", "CCC", "BBB"]
    assert rows[0]["Name"] == "AAA Inc."
    assert rows[0]["Country"] == "USA"
    assert rows[0]["Employees"] == "100"
    assert rows[0]["CEO Name"] == "Alice A."
    assert rows[0]["CEO Year Born"] == "1995"


def test_get_best_52_week_change_data():
    def fake_make_request(url: str):
        if url == m.STOCK_WEEK_CHANGE_TAB_URL:
            return soup(_week_gainers_html())
        if "/quote/AAA/key-statistics" in url:
            return soup(_stats_html("$1.20B"))
        if "/quote/BBB/key-statistics" in url:
            return soup(_stats_html("$987.0M"))
        raise AssertionError(f"Unexpected URL in test: {url}")

    with patch.object(m, "make_request", side_effect=fake_make_request):
        rows = m.get_best_52_week_change_data()

    assert len(rows) == 2
    assert rows[0]["Name"] == "AAA Inc."
    assert rows[0]["Code"] == "AAA"
    assert rows[0]["52-Week Change"] == "+12.34%"
    assert rows[0]["Total Cash"] == "$1.20B"
    assert rows[1]["Code"] == "BBB"
    assert rows[1]["52-Week Change"] == "+3,799.21%"
    assert rows[1]["Total Cash"] == "$987.0M"

def test_get_largest_blackrock_holds_data():
    with patch.object(m, "make_request", return_value=soup(_blk_holders_html())):
        rows = m.get_largest_blackrock_holds_data()

    assert len(rows) == 2
    assert rows[0] == {
        "Name": "Vanguard Group",
        "Shares": "100,000,000",
        "Date Reported": "2025-06-30",
        "% Out": "5.00%",
        "Value": "$10,000,000,000",
    }
    assert rows[1]["Name"] == "State Street"
