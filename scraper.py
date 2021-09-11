# Primary page refers to the page with a list of real estate listings. eg. https://www.royallepage.ca/en/on/ottawa/properties/
# Secondary page refers to single page listing. eg. https://www.royallepage.ca/en/property/ontario/ottawa/3218-uplands-drive/16193440/mls1260681/

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import csv
import json
import logging

from royalLepageTags import ROYAL_LEPAGE_TAGS
from locations import LOCATIONS
from apiKey import GEOCODING_API_KEY

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
  primaryPage = urlopen(Request('https://www.royallepage.ca/en/{province}/{city}/properties/{page} '.format(province=province, city=city, page=page), headers={'User-Agent': 'Mozilla/5.0'})).read()
  primarySoup = BeautifulSoup(primaryPage, 'html.parser')
  listingsUrls += getListingUrl(primarySoup)
  return listingsUrls

def getGeocoords(address):
  location = address.replace(" ","+")
  location = location.replace("#", "")
  data = urlopen(Request('https://maps.googleapis.com/maps/api/geocode/json?address={location}+Canada&key={apiKey}'.format(location = location, apiKey = GEOCODING_API_KEY))).read()
  geocode = json.loads(data.decode('utf-8'))
  latitude = geocode["results"][0]["geometry"]["location"]["lat"]
  longitude = geocode["results"][0]["geometry"]["location"]["lng"]
  return [latitude, longitude]

def getListingData(soup):
  address = ""
  postCode = ""
  beds = ""
  baths = ""
  price = 0

  if soup.find(*ROYAL_LEPAGE_TAGS["addressContainer"]).find(*ROYAL_LEPAGE_TAGS["address"]) != None:
    address = soup.find(*ROYAL_LEPAGE_TAGS["addressContainer"]).find(*ROYAL_LEPAGE_TAGS["address"]).getText().strip()
    postCode = address.split(", ")[-1]
    latitude, longitude = getGeocoords(address)

  if soup.findAll(*ROYAL_LEPAGE_TAGS["beds"]) != None:
    if len(soup.findAll(*ROYAL_LEPAGE_TAGS["beds"])) > 0:
      beds = soup.findAll(*ROYAL_LEPAGE_TAGS["beds"])[0].getText().split(" ")[0]
    if len(soup.findAll(*ROYAL_LEPAGE_TAGS["beds"])) > 1:
      baths = soup.findAll(*ROYAL_LEPAGE_TAGS["baths"])[1].getText().split(" ")[0]
  if soup.find(*ROYAL_LEPAGE_TAGS["price"]).find("span") != None:
    price = int(soup.find(*ROYAL_LEPAGE_TAGS["price"]).find("span").getText().strip()[1:].replace(",",""))
  ##############################
  return [address, postCode, latitude, longitude, beds, baths, price]

def getSecondaryPageData(url):
  listingsData = []
  secondaryPage = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
  secondarySoup = BeautifulSoup(secondaryPage, 'html.parser')
  listingsData += [url, *getListingData(secondarySoup)]
  return listingsData

def writeToCSV(filename, listingUrls):
  with open(filename, 'w',newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['url', 'address', 'postCode', 'latitude', 'longitude', 'NumBeds', 'NumBaths', 'price'])
    for i in listingUrls:
      if i is not None:
        writer.writerows([i])

def main():
  page = 22
  locationToQuery = getMenu()

  while locationToQuery.lower() != "q":
    dataToWrite = []
    
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
    
    counter = 0
    for url in listingUrls:
      dataToWrite.append(getSecondaryPageData(url))
      counter += 1
      if counter % 5 == 0:
        print("Wrote {numLeft} out of {numTotal}".format(numLeft=counter, numTotal=len(listingUrls)))
    writeToCSV("data/" + LOCATIONS[locationToQuery][1] + "-realestate-listing.csv", dataToWrite)
    locationToQuery = getMenu() 

main()