from pathlib import Path
import re
from statistics import fmean
import xml.etree.ElementTree as ET
import json

def parse_city_name(city_name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', city_name)

def parse_weather_data_to_dict():
    source_dir = Path("source_data")
    all_mean_temps = []
    all_mean_winds = []
    coldest_place_val = float('inf')
    warmest_place_val = float('-inf')
    windiest_place_val = float('-inf')
    coldest_place_name = None
    warmest_place_name = None
    windiest_place_name = None
    cities = {}

    for city_dir in source_dir.iterdir():
        json_path = city_dir / "2021_09_25.json"
        with json_path.open(encoding="utf-8") as file:
            data = json.load(file)

        city = {}
        name = parse_city_name(city_dir.name)
        hourly = data["hourly"]
        temps = [h["temp"] for h in hourly]
        winds = [h["wind_speed"] for h in hourly]
        mean_temp = fmean(temps)
        mean_wind = fmean(winds)
        min_temp, max_temp = min(temps), max(temps)
        min_wind, max_wind = min(winds), max(winds)

        all_mean_temps.append(mean_temp)
        all_mean_winds.append(mean_wind)
        
        if mean_temp <= coldest_place_val:
            coldest_place_val, coldest_place_name = mean_temp, name

        if mean_temp >= warmest_place_val:
            warmest_place_val, warmest_place_name = mean_temp, name

        if mean_wind >= windiest_place_val:
            windiest_place_val, windiest_place_name = mean_wind, name
            
        city["mean_temp"] = f"{mean_temp:.2f}"
        city["mean_wind_speed"] = f"{mean_wind:.2f}"
        city["min_temp"] = f"{min_temp:.2f}"
        city["min_wind_speed"] = f"{min_wind:.2f}"
        city["max_temp"] = f"{max_temp:.2f}"
        city["max_wind_speed"] = f"{max_wind:.2f}"
        cities[name] = city

    summary = {}
    summary["mean_temp"]       = f"{fmean(all_mean_temps):.2f}"
    summary["mean_wind_speed"] = f"{fmean(all_mean_winds):.2f}"
    summary["coldest_place"]   = coldest_place_name
    summary["warmest_place"]   = warmest_place_name
    summary["windiest_place"]  = windiest_place_name

    return summary, cities

def parse_weather_data_to_xml():
    summary_data, cities_data = parse_weather_data_to_dict()
    root = ET.Element("weather", attrib={
    "country": "Spain",
    "date": "2021-09-25",
    })
    summary = ET.SubElement(root, "summary", attrib=summary_data)
    cities = ET.SubElement(root, "cities")

    for city, city_data in cities_data.items():
        ET.SubElement(cities, city, attrib=city_data)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write("result.xml", encoding="utf-8", xml_declaration=True)

if __name__ == '__main__':
    parse_weather_data_to_xml()
