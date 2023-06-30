from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd

def get_links(pagesToSearch=1):
    """
    Function that gets links of all houses
    """
    s = requests.Session()
    listOfLinks = []
    listOfLinksFinal = []
    #pagesToSearch = 1 # set the number according to how many pages you want to sarch thru each of properties set
    propertiesToSearch = ["apartment","house"] # fill the list with propertis to search

    for prop in propertiesToSearch:
        for x in range(1,pagesToSearch+1): #houses
            #search_url = f"https://www.immoweb.be/en/search/{prop}/for-sale?countries=BE&priceType=SALE_PRICE&page={x}&orderBy=relevance"
            search_url = f"https://www.immoweb.be/en/search/{prop}/for-sale?countries=BE&isNewlyBuilt=false&isAPublicSale=false&page={x}&orderBy=relevance"
            r = s.get(search_url)
            soup = BeautifulSoup(r.text,"html.parser")
            for elem in soup.find_all("a", attrs = {"class": "card__title-link"}):
                listOfLinks.append(elem.get('href'))
            listOfLinks = listOfLinks[0:len(listOfLinks)-30]
            listOfLinksFinal = listOfLinksFinal + listOfLinks
            listOfLinks.clear()
    return(listOfLinksFinal)
#with open('links.txt','w+') as file:
#    file.write('\n'.join(links))

def get_data(url):
    #url="https://www.immoweb.be/en/classified/house/for-sale/lede/9340/10660142"
    s = requests.Session()
    req= s.get(url)

    soup= BeautifulSoup(req.text, "html.parser")
    data = soup.find('div',attrs={"class":"container-main-content"}).script.text

    Raw_data_InList= re.findall(r"window.classified = (\{.*\})", data)
    Raw_data_InDict = json.loads(Raw_data_InList[0]) # Data dictionary


    property_dict = {}
    property_dict[url] = {}
    
    try:
        property_dict[url]["Locality"] = Raw_data_InDict["customers"][0]['location']['locality']
    except KeyError:
        property_dict[url]["Locality"] = None
        
    try:
        property_dict[url]["Type of property"] = Raw_data_InDict["property"]["type"]
    except KeyError:
        property_dict[url]["Type of property"] = None
    
    try:
        property_dict[url]["Subtype of property"] = Raw_data_InDict["property"]["subtype"]
    except KeyError:
        property_dict[url]["Subtype of property"] = None
    
    try:
        property_dict[url]["Price"] = Raw_data_InDict["price"]["mainValue"]
    except KeyError:
        property_dict[url]["Price"] = None
        
    try:
        property_dict[url]["Type of Transaction"] = Raw_data_InDict["transaction"]["type"]
    except KeyError:
        property_dict[url]["Type of Transaction"] = None
    
    try:
        property_dict[url]["Nº rooms"] = Raw_data_InDict["property"]["bedroomCount"]
    except KeyError:
        property_dict[url]["Nº rooms"] = None    

    try:
        property_dict[url]["Living area"] = Raw_data_InDict["netHabitableSurface"]
    except KeyError:
        property_dict[url]["Living area"] = None

    try:
        if bool(Raw_data_InDict["property"]["kitchen"]['type']):
            property_dict[url]["Equipped kitchen"] = "Yes"
    except KeyError:
        property_dict[url]["Equipped kitchen"] = "No"
        
    try:
        if bool(Raw_data_InDict["transaction"]["sale"]["isFurnished"]):
            property_dict[url]["Furnished"] = "Yes"
    except KeyError:
        property_dict[url]["Furnished"] = "No"
        
    try:
        property_dict[url]["Furnished"] = Raw_data_InDict["transaction"]["sale"]["isFurnished"]
    except KeyError:
        property_dict[url]["Furnished"] = None
    
    try:
        if bool(Raw_data_InDict["fireplaceExists"]):
            property_dict[url]["Fireplace"] = "Yes"
    except KeyError:
        property_dict[url]["Fireplace"] = "No"
    
    try:
        if bool(Raw_data_InDict["property"]["hasTerrace"]):
            property_dict[url]["Terrace"] = "Yes"
            property_dict[url]["Area Terrace"] = Raw_data_InDict["property"]["terraceSurface"]
    except KeyError:
        property_dict[url]["Terrace"] = "No"
    
    try:
        if bool(Raw_data_InDict["property"]["hasGarden"]):
            property_dict[url]["Garden"] = "Yes"
            property_dict[url]["Area Garden"] = Raw_data_InDict["property"]["gardenSurface"]
    except KeyError:
        property_dict[url]["Garden"] = "No"
    
    try:
        property_dict[url]["Land Surface"] = Raw_data_InDict["property"]["land"]["surface"]
    except KeyError:
        property_dict[url]["Land Surface"] = None
    except TypeError: # had to add this otherwise I was getting TypeError 'NoneType' object is not subscriptable
        property_dict[url]["Land Surface"] = None
    
    # surface area of the plot of land
    
    try:
        property_dict[url]["Nº facades"] = Raw_data_InDict["property"]["building"]["facadeCount"]
    except KeyError:
        property_dict[url]["Nº facades"] = None
    
    try:
        if bool(Raw_data_InDict["fhasSwimmingPool"]):
            property_dict[url]["Swimming Pool"] = "Yes"
    except KeyError:
        property_dict[url]["Swimming Pool"] = "No"
        
    try:
        property_dict[url]["State Building"] = Raw_data_InDict["property"]["building"]["condition"]
    except KeyError:
        property_dict[url]["State Building"] = None
            
    return property_dict   

def save(data_immo):
        '''This function saves the information acquired from the previous functions and store them in a csv file in the disk.'''
        #data_immo = get_data()
        dataframe_immo = pd.DataFrame(data_immo)
        dataset_csv = dataframe_immo.to_csv("./dataset-immo.csv", sep=" ", index=False)
        return dataset_csv

links = ['https://www.immoweb.be/en/classified/apartment/for-sale/schaerbeek/1030/10666536',
 'https://www.immoweb.be/en/classified/apartment/for-sale/schaerbeek/1030/10666535',
 'https://www.immoweb.be/en/classified/duplex/for-sale/drongen/9031/10666607']

for link in links:
    print(link)
    dictionary = get_data(link)
    print(dictionary)
    
save(dictionary)