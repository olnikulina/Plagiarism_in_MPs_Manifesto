### Scrape MP's data and file with manifesto from website of Central Election Commission of Ukraine

#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import re, requests, time
from bs4 import BeautifulSoup


def get_links_for_okrugs():
    request = requests.get('https://www.cvk.gov.ua/pls/vnd2019/wp032pt001f01=919.html')
    request.encoding = 'UTF-8'
    soup = BeautifulSoup(request.content, 'lxml')
    tds = soup.find_all('td', {'class':'td2'})
    okrugs = ['https://www.cvk.gov.ua/pls/vnd2019/' + td.a['href'] for td in tds if td.a is not None]
    return okrugs

def parse_candidates_info(url):
    request = requests.get(url)
    request.encoding = 'UTF-8'
    soup_okrug = BeautifulSoup(request.content, 'lxml')
    info = pd.read_html(str(soup_okrug),header=0)[5]
    info['Округ'] = soup_okrug.find('p').text
    return info

def get_csv_with_candidates(info_tables):
    cands_info = pd.concat(info_tables, ignore_index = True)
    cands_info = cands_info.drop('Передвиборна програма', 1)
    cands_info['Область'] = cands_info['Округ'].str.extract('\(([^)]+)')
    cands_info['Округ'] = cands_info['Округ'].str.extract('(\d+)')
    cands_info["Прізвище, ім'я та по батькові кандидата в депутати"] = [re.sub(r'([Є-ЯҐ]\w+)([Є-ЯҐ]\w+)', r'\1 \2', row) for row in cands_info["Прізвище, ім'я та по батькові кандидата в депутати"]]
    cands_info.to_csv('output.csv', sep=',')

def parse_candidates_programs(url):
    request = requests.get(url)
    request.encoding = 'UTF-8'
    soup_okrug = BeautifulSoup(request.content, 'lxml')
#    name of the candidate is used as the name of file with the program
    name = pd.read_html(str(soup_okrug),header=0)[5].iloc[:,0][0]
    tds = soup_okrug.find_all('td', {'class':'td3'})
    for td in tds:
        if td.a is not None:
            link = 'https://www.cvk.gov.ua/pls/vnd2019/' + td.a['href']
            response = requests.get(link)
            with open(('/home/olena/Desktop/parse_cvk_2019/programs/' + name), 'wb') as f:
                f.write(response.content)
            time.sleep(5)

def parse_program_links(url):
    request = requests.get(url)
    request.encoding = 'UTF-8'
    soup_okrug = BeautifulSoup(request.content, 'lxml')
    program_links = soup_okrug.find_all('a', href=re.compile(r".doc"))
    if program_links is not None:
        for program_link in program_links:
            program_link = 'https://www.cvk.gov.ua/pls/vnd2019/' + program_link['href']
            return program_link
            time.sleep(1)

program_links_list = []
info_tables = []

okrugs = get_links_for_okrugs()
for okrug in okrugs:
    info_tables.append(parse_candidates_info(okrug))
    # parse_candidates_programs(okrug)
    program_links_list.append(program_links(okrug))
get_csv_with_candidates(info_tables)

