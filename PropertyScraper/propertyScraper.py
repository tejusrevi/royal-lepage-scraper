# Scrapes property data from /property page

import json
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError
import logging

from royalLepageTags import ROYAL_LEPAGE_TAGS
from apiKey import GEOCODING_API_KEY

def getGeocoords(address):
  location = address.replace(" ","+")
  location = location.replace("#", "")
  data = urlopen(Request('https://maps.googleapis.com/maps/api/geocode/json?address={location}+Canada&key={apiKey}'.format(location = location, apiKey = GEOCODING_API_KEY))).read()
  geocode = json.loads(data.decode('utf-8'))
  latitude = geocode["results"][0]["geometry"]["location"]["lat"]
  longitude = geocode["results"][0]["geometry"]["location"]["lng"]
  return [latitude, longitude]

def scrapeData(soup):
  address, postCode, latitude, longitude = scrapeAddress(soup)
  beds= scrapeNumBeds(soup)
  baths= scrapeNumBaths(soup)
  price = scrapePrice(soup)

  buildingStyle = scrapeBuildingFeature(soup, "style")
  buildingType = scrapeBuildingFeature(soup, "type")
  buildingDevelopment = scrapeBuildingFeature(soup, "development")
  buildingExteriorFinish = scrapeBuildingFeature(soup, "exterior-finish")
  buildingFirePlace = scrapeBuildingFeature(soup, "fireplace")
  buildingHeatingType = scrapeBuildingFeature(soup, "heating-type")
  buildingHeatingFuel = scrapeBuildingFeature(soup, "heating-fuel")
  buildingCoolingType = scrapeBuildingFeature(soup, "cooling-type")
  
  propertyOwnershipType = scrapePropertyFeature(soup, "ownershiptype") # Typo in Royal LePage
  propertyType = scrapePropertyFeature(soup, "property-type")
  parkingType = scrapePropertyFeature(soup, "parking-type")
  numParking = scrapePropertyFeature(soup, "no.-of-parking-spaces")

  averageIncome = scrapeAverageIncome(soup)

  return [address, postCode, latitude, longitude, beds, baths, price, 
    buildingStyle, buildingType, buildingDevelopment, buildingExteriorFinish,  buildingFirePlace, buildingHeatingType, buildingHeatingFuel, buildingCoolingType, 
    propertyOwnershipType, propertyType, parkingType, numParking, averageIncome]

def getPropertyData(url):
  listingsData = []
  try:
    secondaryPage = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
    secondarySoup = BeautifulSoup(secondaryPage, 'html.parser')
    listingsData += [url, *scrapeData(secondarySoup)]
  except HTTPError:
    logging.error("Page doesn't exist")
  except URLError:
    logging.error("No internet connection")
  return listingsData

# Scraping  functions 

def scrapeAddress(soup):
  if soup.find(*ROYAL_LEPAGE_TAGS["addressContainer"]).find(*ROYAL_LEPAGE_TAGS["address"]) != None:
    address = soup.find(*ROYAL_LEPAGE_TAGS["addressContainer"]).find(*ROYAL_LEPAGE_TAGS["address"]).getText().strip()
    postCode = address.split(", ")[-1]
    latitude, longitude = 0, 0 #getGeocoords(address)

    return [address, postCode, latitude, longitude]
  else:
    return [None, None, None, None]

def scrapeNumBeds(soup):
  if soup.findAll(*ROYAL_LEPAGE_TAGS["beds"]) != None:
    if len(soup.findAll(*ROYAL_LEPAGE_TAGS["beds"])) > 0:
      beds = soup.findAll(*ROYAL_LEPAGE_TAGS["beds"])[0].getText().split(" ")[0]
      return beds

def scrapeNumBaths(soup):
  if soup.findAll(*ROYAL_LEPAGE_TAGS["baths"]) != None:
    if len(soup.findAll(*ROYAL_LEPAGE_TAGS["baths"])) > 1:
      baths = soup.findAll(*ROYAL_LEPAGE_TAGS["baths"])[1].getText().split(" ")[0]
      return baths

def scrapePrice(soup):
  if soup.find(*ROYAL_LEPAGE_TAGS["price"]).find("span") != None:
    price = int(soup.find(*ROYAL_LEPAGE_TAGS["price"]).find("span").getText().strip()[1:].replace(",",""))
    return price

def scrapeBuildingFeature(soup, feature):
  featureNodeList = soup.findAll(*ROYAL_LEPAGE_TAGS["featureList"])[0].findAll("li")
  for featureNode in featureNodeList:
    if featureNode.find(*ROYAL_LEPAGE_TAGS["featureLabel"]).getText()[0:-1].replace(" ", "-").lower() == feature:
      return featureNode.find(*ROYAL_LEPAGE_TAGS["featureValue"]).getText()

def scrapePropertyFeature(soup, feature):
  featureNodeList = soup.findAll(*ROYAL_LEPAGE_TAGS["featureList"])[1].findAll("li")
  for featureNode in featureNodeList:
    if featureNode.find(*ROYAL_LEPAGE_TAGS["featureLabel"]).getText()[0:-1].replace(" ", "-").lower() == feature:
      return featureNode.find(*ROYAL_LEPAGE_TAGS["featureValue"]).getText()

def scrapeAverageIncome(soup):
  if soup.find(*ROYAL_LEPAGE_TAGS["averageIncomeContainer"]):
    return soup.find(*ROYAL_LEPAGE_TAGS["averageIncomeContainer"]).find("div").find("span").getText().strip()[1:].replace(",","")
