from lxml import html
import csv,os,json
import requests
from time import sleep
from bs4 import BeautifulSoup
import urllib.request
import ssl
import re
import xlsxwriter
import datetime
import time


bad_amazon_links = {}
bad_value_amazon_links = {}
without_result = []
pages_without_links = []

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'alt']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


class AppURLopener(urllib.request.FancyURLopener):
    context = ssl._create_unverified_context()
    # verify = False
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


    def http_error_default(self, url, fp, errcode, errmsg, headers):
        if errcode == 403:
            raise ValueError("403")
        return super(AppURLopener, self).http_error_default(
            url, fp, errcode, errmsg, headers)

# list_with_cloodjo_pages = ''
#  list_with_cloodjo_pages = ''
list_with_cloodjo_pages = []
domain = ''

opener = AppURLopener
ssl._create_default_https_context = ssl._create_unverified_context
posts_html = opener(verify=False).open('{0}{1}'.format(domain, '/post-sitemap.xml'))
posts_soup = BeautifulSoup(posts_html, "lxml")
for loc in posts_soup.findAll('loc'):
    list_with_cloodjo_pages.append(loc.text)

posts_html = opener(verify=False).open('{0}{1}'.format(domain, '/page-sitemap.xml'))
posts_soup = BeautifulSoup(posts_html, "lxml")
for loc in posts_soup.findAll('loc'):
    list_with_cloodjo_pages.append(loc.text)

for one_page in list_with_cloodjo_pages:
    time.sleep(2)
    try:
        opener = AppURLopener
        ssl._create_default_https_context = ssl._create_unverified_context
        html = opener(verify=False).open(one_page)
        soup = BeautifulSoup(html, "lxml")
    except:
        without_result.append(one_page)

    crawl_domain = ''
    amazon_links = []
    for a in soup.findAll('a'):
        try:
            if a['href'].find('amzn.to') != -1:
                amazon_links.append(a['href'])
        except:
            pages_without_links.append(one_page)
    print('Page: ', one_page)
    print('Amazon Links: ', amazon_links)

    for one_link in amazon_links:
        opener = AppURLopener
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            amazon_html = opener(verify=False).open(one_link)
            amazon_soup = BeautifulSoup(amazon_html, "lxml")
        except ValueError:
            if one_page in bad_amazon_links:
                bad_amazon_links[one_page].append(one_link)
            else:
                bad_amazon_links[one_page] = [one_link]

        for h1 in amazon_soup.findAll('h1'):
            h1_for_check = h1.text
            if h1_for_check.find('We found 0 results') != -1:
                if one_page in bad_amazon_links:
                    bad_amazon_links[one_page].append(one_link)
                else:
                    bad_amazon_links[one_page] = [one_link]

        print('One Link', one_link)
        print('Bad Results: ', bad_amazon_links)
        print('Without Results: ', without_result)

print(without_result)
print(pages_without_links)

workbook = xlsxwriter.Workbook('text.xlsx')
worksheet = workbook.add_worksheet('Site_data')

col = 0
row = 0
# bad_amazon_links = ''
header_template = ["URL", "Broken Links"]
for header_name in header_template:
    worksheet.write(row, col, header_name)
    col += 1


for one_page in bad_amazon_links:
    col = 0
    row += 1
    worksheet.write(row, col, one_page)
    for link in bad_amazon_links[one_page]:
        col += 1
        worksheet.write(row, col, link)

workbook.close()