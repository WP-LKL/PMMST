
import json
import csv    

from collections import defaultdict
from contextlib import suppress


EXPANDNOTES    = True                      # Merge incompatible fields into notes.
FILE           = 'passwords.json'          # Password backup/export file.
CSVNAME        = 'passwordsProcessed.csv'  # Processed passwords output file.
REMOVE         = []                        # Fields to remove.
VALID          = []                        # Only use fields that are valid for KeePass.


# Example configuration:
REMOVE += [
            "color", 
            "tags", 
            "secure_item_type_name",
            "subtitle"
        ]
VALID  += [
            "name",  # Or title
            "type",  # Or category
            "username",
            "password",
            "url",
            "notes",
            "totp"
        ]

def readFile(file):
    with open(file, 'r') as file:
        content = json.load(file)
    return content

def cleanText(text):
    text = str.join(" <BR> ", text.splitlines())
    return text

def mergeToNotes(row):
    mergedNotes = ""
    for (k, v) in row.items():
        if k not in VALID:
            mergedNotes += " <BR> " + k + ": " + v
    
    row["notes"] += mergedNotes

def getFields(dictionary):
    assert type(dictionary) == dict, "must be a dictionary"
    keys = []
    for key in dictionary.keys():
        if type(dictionary[key]) == dict:
            keys += getFields(dictionary[key])
        else:
            keys += [key]
            relevance[key] += 1
    return keys

def getValues(dictionary):
    assert type(dictionary) == dict, "must be a dictionary"
    keyValues = defaultdict(lambda: "")
    for key in dictionary.keys():
        if type(dictionary[key]) == dict:
            keyValues = {**keyValues, **getValues(dictionary[key])}
        else: 
            keyValues[key] = cleanText(str(dictionary[key]))
    return keyValues


# Run
# 1.1 Get all fields
allFields = []
relevance=defaultdict(lambda: 0)
content = readFile(FILE)

for item in content["items"]:
    # Return not needed, all is stored in relevance
    allFields = getFields(item)  

# 1.2 Create ordered set of fields
#allFields = list(dict.fromkeys(allFields)) 
lsd = sorted( ((v,k) for k,v in relevance.items()), reverse=True)
allFields = [v for k,v in lsd]
[allFields.remove(k) for k in REMOVE]  # TODO: Try, Except.

# 2. Write to .csv 
with open(CSVNAME, 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
    filewriter.writerow([VALID])

    for item in content['items']:
        row = []
        values = getValues(item)
        
        with suppress(KeyError): 
            for key in REMOVE: del values[key] 
            
        values = defaultdict(lambda: "", values)
        
        if EXPANDNOTES: mergeToNotes(values)
        
        if VALID != []: iterator = VALID
        else:           iterator = allFields
        
        for field in iterator:
            row += [values[field]]
            
            
        filewriter.writerow(row)

