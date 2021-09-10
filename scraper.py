# Primary page refers to the page with a list of real estate listings. eg. https://www.royallepage.ca/en/on/ottawa/properties/
# Secondary page refers to single page listing. eg. https://www.royallepage.ca/en/property/ontario/ottawa/3218-uplands-drive/16193440/mls1260681/

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import csv
import json

import logging

dataToWrite = []

GEOCODING_API_KEY=""

LOCATIONS = {
  "1": ["on", "toronto"],
  "2": ["qc", "montreal"],
  "3": ["bc", "vancouver"],
  "4": ["ab", "calgary"],
  "5": ["ab", "edmonton"],
  "6": ["on", "ottawa"],
  "7": ["mb", "winnipeg"],
  "8": ["qc", "quebec"],
  "9": ["on", "hamilton"],
  "10": ["on", "kitchener"]
}

ROYAL_LEPAGE_TAGS = {
  "listings":["li", {"class":"card-group__item"}] # Used to get individual listing urls from primary page
}

# Provide menu to user and return a number representing user selection
def getMenu():
  for key in LOCATIONS.keys():
    print(key + " " + LOCATIONS[key][1]) #
  return input("Please select from numbers 1 - 10. Q to quit: ")

# Function to find and return url for individual listings 
def getListingUrl(soup):
  urls = []
  listings = soup.findAll(*ROYAL_LEPAGE_TAGS["listings"]) #asterisk is used to unpack list
  for listing in listings: 
    urls.append(listing.find("a")["href"])
  return urls

# Function to request listings page. Returns a list of all real estate listings in that page
def getPrimaryPageData(province, city, page):
  listingsUrls = []
  homepage = urlopen(Request('https://www.royallepage.ca/en/{province}/{city}/properties/{page} '.format(province=province, city=city, page=page), headers={'User-Agent': 'Mozilla/5.0'})).read()
  primarySoup = BeautifulSoup(homepage, 'html.parser')
  listingsUrls += getListingUrl(primarySoup)
  return listingsUrls

def writeToCSV(filename, listingUrls):
  with open(filename, 'w',newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['url'])
    for i in listingUrls:
      if i is not None:
        writer.writerow([i])

def main():
  page = 20
  locationToQuery = getMenu()

  while locationToQuery.lower() != "q":
    listingUrls = [] # List to store all individual listings urls
    lastUrls = [] # List to hold listings urls returned from last page
    while True:
      try:
        currentUrls = getPrimaryPageData(LOCATIONS[locationToQuery][0], LOCATIONS[locationToQuery][1], page=page)
        if currentUrls == lastUrls:
          break
        lastUrls = currentUrls
        listingUrls += currentUrls

      except HTTPError:
        break
      except URLError:
        logging.error("No internet connection")
        break
      page+=1
    writeToCSV(LOCATIONS[locationToQuery][1] + "-realestate-listing",listingUrls)
    locationToQuery = getMenu() 

main()