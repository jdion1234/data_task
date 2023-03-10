import json
import requests
import re

# create a fuction for cleaning text
def text_cleaner(name):

    # make everything lowercase
    name = name.lower()

    # remove possible trailing white space
    name = name.rstrip()

    # remove double spaces and replace with single space
    name = re.sub("\s\s", " ", name)

    #check if name has 3 words
    three_words =   ((len(name.split())-1)==2)

    # if name has 3 words, then if the 2nd word is an initial (with or without a period) remove it
    if (three_words):
        name = re.sub("\s[A-Za-z]\s", " ", name)
        name = re.sub("\s[A-Za-z]\.\s", " ", name)
        # print("hi")
    
    return(name)

# this is the url where we will send an HTTP request to scrape our data
URL = "https://firststop.sos.nd.gov/api/Records/businesssearch"

# content of POST HTTP request to send to url - searches for active businesses that start with 'x'
content = {
            "SEARCH_VALUE": "x", 
            "STARTS_WITH_YN": True, 
            "ACTIVE_ONLY_YN": True
        }

# send the HTTP request
response = requests.post(url =URL, json=content)

# extract data in json format
business_data = response.json()

# create empty dictionary to be filled with scraped data
output = {}

# create variable to track row numbers
row_number = 1

# get owner/commercial registered agent/registered agent info for each business
for business in business_data["rows"]:

    business_name = business_data["rows"][business]["TITLE"][0]

    # filter out businesses that don't start with x in case they got through the query
    if business_name[0]=="x" or business_name[0]=="X":

        # construct urls using the ID numbers of the businesses for GET HTTP request to get ownership data
        URL = "https://firststop.sos.nd.gov/api/FilingDetail/business/" + business + "/false"
        r = requests.get(url=URL, headers={"authorization":"undefined"})
        ownership_data=r.json()
        test=1
        # check if the business is associated with an owner, registered agent, or commercial registered agent
        for dicts in ownership_data["DRAWER_DETAIL_LIST"]:
            
            if dicts["LABEL"] == "Commercial Registered Agent":
                output[business_name]={"Name":[text_cleaner(dicts["VALUE"].partition('\n')[0])], "Type":"Commercial Registered Agent"}
                print(str(row_number) + ". " + business_name)
                test=0
            elif dicts["LABEL"] == "Owner Name":
                output[business_name]={"Name":[text_cleaner(dicts["VALUE"].partition('\n')[0])], "Type":"Owner Name"}
                print(str(row_number) + ". " + business_name)
                test=0
            elif dicts["LABEL"] == "Registered Agent":
                output[business_name]={"Name":[text_cleaner(dicts["VALUE"].partition('\n')[0])], "Type":"Registered Agent"}
                print(str(row_number) + ". " + business_name)
                test=0
            elif dicts["LABEL"] == "Owners":
                name_array = [text_cleaner(dicts["VALUE"].partition('\n')[0]), text_cleaner(ownership_data["DRAWER_DETAIL_LIST"][3]["VALUE"].partition('\n')[0])]
                output[business_name]={"Name":name_array, "Type":"Owners"}
                print(str(row_number) + ". " + business_name)
                test=0                
        
        if(test==1):
            print(str(row_number) + ". --This one is different-- " + business_name)
        test=1
        #print businesses for visual reference for progress of the program
        # print(str(row_number) + ". " + business_name)
        row_number+=1

# write scraped data to json file
json_string = json.dumps(output, indent=2)
with open('scraped_data.json', 'w') as f:
    f.write(json_string)