#Engeto Python Academy
# Třetí projekt - Elections Scraper
# 
#  
# author: Hana Šimečková
# email: simeckova.hana8@gmail.com
# discord: Hanka Š.



# Importy

import sys
import os
import csv
import requests
from bs4 import BeautifulSoup as bs

# Funkce

def region_stranka(adresa):
    # Načte HTML stránku regionu a vrátí BeautifulSoup objekt.

    zdroj_data = requests.get(adresa)
    return bs(zdroj_data.text, "html.parser")

def mesta(regiony_rozdeleno):
    # Získá seznam měst z regionu.
    
    mesta_list = []
    pocet = len(regiony_rozdeleno.find_all("table", {"class": "table"}))
    for cislo in range(1, pocet + 1):
        mesta_list.extend(regiony_rozdeleno.find_all("td", {"headers": f"t{cislo}sa3"}))
    return mesta_list

def uzemni_celky (mesta_list):
    # Získá seznam odkazů na celky.
    return ["https://www.volby.cz/pls/ps2017nss/" + (td_tag.a["href"]) for td_tag in mesta_list]

def argumenty_kontrola (celky_seznam):
    # Zkontroluje, zda jsou vložené argumenty správné.

    if len(sys.argv) != 3:
        print("Vložte dva argumenty pro běh programu.")
        quit()
    if sys.argv[1] not in celky_seznam:
        print("Vložen nesprávný odkaz pro územní celek.")
        quit()

def mesto_data (tr_tag, town):
    # Stáhne a vrátí data pro konkrétní město.

    link = tr_tag.find("td", {"class": "cislo"}).a

    def obec_stranka(link):
        mesto_odkaz = f"https://www.volby.cz/pls/ps2017nss/{link['href']}"
        mesto_stranka = requests.get(mesto_odkaz)
        return bs(mesto_stranka.text, "html.parser")

    def obecna_data(town_tag, link_tag):
        div_tag = obec_stranka(link_tag).find("div", {"id": "publikace"})
        obecne_info = div_tag.table.find_all("td")
        return {
            "Kód obce": link_tag.text,
            "Název obce": town_tag.text,
            "Voliči": obecne_info[3].text,
            "Vydané obálky": obecne_info[4].text,
            "Platné hlasy": obecne_info[7].text
        }

    def politicke_strany():
        inner = obec_stranka(link).find("div", {"id": "inner"})
        strany = [tag.text for tag in inner.find_all("td", {"class": "overflow_name"})]
        hlasy1 = [tag.text for tag in inner.find_all("td", {"headers": "t1sa2 t1sb3"})]
        hlasy2 = [tag.text for tag in inner.find_all("td", {"headers": "t2sa2 t2sb3"})]
        hlasy_soucet = hlasy1 + hlasy2
        return {strany[i]: hlasy_soucet[i] for i in range(len(strany))}

    vysledky = {}
    vysledky.update(obecna_data(town, link))
    vysledky.update(politicke_strany())
    return vysledky

def ulozeni_dat (mesta, soubor):
    # Uloží data do CSV souboru.

    with open(soubor, mode="w", newline="\n") as nove_csv:
        zapisovac = None
        for tr_tag in mesta:
            mesto_tag = tr_tag.find("td", {"class": "overflow_name"})
            if mesto_tag is None:
                continue
            data = mesto_data(tr_tag, mesto_tag)
            if zapisovac is None:
                zapisovac = csv.DictWriter(nove_csv, delimiter=";", fieldnames=data.keys())
                zapisovac.writeheader()
            zapisovac.writerow(data)

def novy_nazev_souboru (soubor):
    # Generuje unikátní název souboru přidáním číselné přípony.

    zadany_nazev, pripona = os.path.splitext(soubor)
    counter = 1
    novy_nazev = f"{zadany_nazev}_{counter}{pripona}"
    while os.path.exists(novy_nazev):
        counter += 1
        novy_nazev = f"{zadany_nazev}_{counter}{pripona}"
    return novy_nazev

def main():
    adresa = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    regiony_rozdeleno = region_stranka(adresa)
    mesta_list = mesta (regiony_rozdeleno)
    celky_seznam = uzemni_celky(mesta_list)
    argumenty_kontrola(celky_seznam)
    vlozeny_odkaz = sys.argv[1]
    region = region_stranka(vlozeny_odkaz)
    inner = region.find("div", {"id": "inner"})
    mesto = inner.find_all("tr")

    # Přidání přípony .csv ke zadanému názvu souboru
    soubor = sys.argv[2] + ".csv" 
    
    if os.path.exists(soubor):
        soubor = novy_nazev_souboru(soubor)
    print("Stahování dat...")
    ulozeni_dat(mesto, soubor)
    print(f"Data uložena do souboru: {soubor}")

if __name__ == "__main__":
    main()
