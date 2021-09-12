# Properties page refers to the page with a list of real estate listings. eg. https://www.royallepage.ca/en/on/ottawa/properties/
# Property page refers to single page listing. eg. https://www.royallepage.ca/en/property/ontario/ottawa/3218-uplands-drive/16193440/mls1260681/


import csv

# Importing constants
from locations import LOCATIONS

# Importing properties scraper (to get listing urls)
from PropertiesScraper.propertiesScraper import getPropertiesUrls

# Importing property scraper (to get data about each listing)
from PropertyScraper.propertyScraper import getPropertyData

# Provide menu to user and return a number representing user selection
def getMenu():
  for key in LOCATIONS.keys():
    print(key + " " + LOCATIONS[key][1]) #
  return input("Please select from numbers 1 - {numCities} . Q to quit: ".format(numCities = len(LOCATIONS.keys())))


def writeToCSV(filename, listingUrls):
  with open(filename, 'w',newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['url', 'address', 'postCode', 'latitude', 'longitude', 'NumBeds', 'NumBaths', 'price',
      'buildingStyle', 'buildingType', 'buildingDevelopment', 'buildingExteriorFinish', 'buildingFirePlace', 'buildingHeatingType', 'buildingHeatingFuel', 'buildingCoolingType', 
      'propertyOwnershipType', 'propertyType', 'parkingType', 'numParking', 'averageIncome'])
    for i in listingUrls:
      if i is not None:
        writer.writerows([i])

def main():
  page = 1
  locationToQuery = getMenu()

  while locationToQuery.lower() != "q":
    dataToWrite = []

    listingUrls = [] # List to store all individual listings urls
    lastUrls = [] # List to hold listings urls returned from last page
    while True:
      currentUrls = getPropertiesUrls(LOCATIONS[locationToQuery][0], LOCATIONS[locationToQuery][1], page=page)
      if currentUrls == lastUrls:
        break
      lastUrls = currentUrls
      listingUrls += currentUrls
      print("Scraped all urls from page {pageNum}".format(pageNum = page))
      page+=1
    
    print("\nFinished Scraping all urls\n---------------------------------")
    
    counter = 1
    for url in listingUrls:
      dataToWrite.append(getPropertyData(url))
      print("Scraped data from {numLeft} properties out of {numTotal}".format(numLeft=counter, numTotal=len(listingUrls)))
      counter += 1
    writeToCSV("data/" + LOCATIONS[locationToQuery][1] + "-realestate-listing.csv", dataToWrite)
    locationToQuery = getMenu() 

main()