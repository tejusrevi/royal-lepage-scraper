# Scrapes listing urls from /properties page

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

from royalLepageTags import ROYAL_LEPAGE_TAGS

# Function to find and return url for individual listings 
def scrapeUrls(soup):
  urls = []
  listings = soup.findAll(*ROYAL_LEPAGE_TAGS["listings"]) #asterisk is used to unpack list
  for listing in listings: 
    urls.append(listing.find("a")["href"])
  return urls

# Function to request listings page. Returns a list of all real estate listings in that page
def getPropertiesUrls(province, city, page):
  listingsUrls = []
  primaryPage = urlopen(Request('https://www.royallepage.ca/en/{province}/{city}/properties/{page}'.format(province=province, city=city, page=page), headers={'User-Agent': 'Mozilla/5.0'})).read()
  primarySoup = BeautifulSoup(primaryPage, 'html.parser')
  listingsUrls += scrapeUrls(primarySoup)
  return listingsUrls