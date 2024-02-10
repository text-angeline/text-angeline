import json
import base64
import telnyx
import requests

def process_sms(event, context):
    # Extract message content from Pub/Sub event
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    # Process message content and determine response
    response = process_message(pubsub_message)
    # Send response SMS using Telnyx to the sender's phone number
    sender_number = event['attributes']['from']  # Assuming the sender's number is included as an attribute

def process_message(message):
    # Modify the message content as needed
    modified_message = message.upper()  # Example: Convert message to uppercase
    return modified_message

with open('config.json', 'r') as f:
    config = json.load(f)

T_KEY = config["T_KEY"]
A_KEY = config["A_KEY"]

telnyx.api_key = T_KEY

number = "+12193519673"
destination = "+19493573901"

book_dict = {
    "genesis": "GEN",
    "exodus": "EXO",
    "leviticus": "LEV",
    "numbers": "NUM",
    "deutoronomy": "DEU",
    "joshua": "JOS",
    "judges": "JDG",
    "ruth": "RUT",
    "1 samuel": "1SA",
    "2 samuel": "2SA",
    "1 kings": "1KG",
    "2 kings" :"2KG",
    "1 chronicles": "1CH",
    "2 chronicles": "2CH",
    "ezra": "EZR",
    "nehemiah": "NEH",
    "esther": "EST",
    "job": "JOB",
    "psalm": "PSA",
    "proverbs": "PRO",
    "ecclesiastes": "ECC",
    "song of songs": "SNG",
    "isaiah": "ISA",
    "jeremiah": "JER",
    "lamentations": "LAM",
    "ezekiel": "EZK",
    "daniel": "DAN",
    "hosea": "HOS",
    "joel": "JOL",
    "amos": "AMO",
    "obadiah": "OBA",
    "jonah": "JON",
    "micah": "MIC",
    "nahum": "NAM",
    "habakkuk": "HAB",
    "zephaniah": "ZEP",
    "haggai": "HAG",
    "zechariah": "ZEC",
    "malachi": "MAL",
    "matthew": "MAT",
    "mark": "MRK",
    "luke": "LUK",
    "john": "JHN",
    "acts": "ACT",
    "roman": "ROM",
    "1 corinthians": "1CO",
    "2 corinthians": "2CO",
    "galatians": "GAL",
    "ephesians": "EPH",
    "philippians": "PHP",
    "colossians": "COL",
    "1 thessalonians": "1TH",
    "2 thessalonians": "1TH",
    "1 timothy": "1TI",
    "2 timothy": "2TI",
    "titus": "TIT",
    "philemon": "PHM",
    "hebrews": "HEB",
    "james": "JAS",
    "1 peter": "1PE",
    "2 peter": "2PE",
    "1 john": "1JN",
    "2 john": "2JN",
    "3 john": "3JN",
    "jude": "JUD",
    "revelations": "REV"
}

### Example chapter request (Matthew 1 [MAT.1])
# https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/chapters/MAT.1?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false

### Example verse request (Matthew 1:23 [MAT.1.23])
# https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/verses/MAT.1.23?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false&use-org-id=false

# unit = input("Unit (chapters/verses): ")
query = input("Query: ").lower()
try:
    colon_split = query.split(':')
    print(f"colon_split: {colon_split}")
    verse = colon_split[1]
    unit = "verses"
except:
    unit = "chapters"
space_split = colon_split[0].split()
print(f"space_split: {space_split}")
if (len(space_split) == 2):
    book = space_split[0]
    chapter = space_split[1]
elif (len(space_split) == 3):
    book = space_split[0] + " " + space_split[1]
    chapter = space_split[2]

print(f"Unit: {unit}\nBook: {book}\nChapter: {chapter}")
if (unit == "verses"):
    print(f"Verse: {verse}")

if (book in book_dict):
    if (unit == "chapters"):
        formatted_query = book_dict[book] + '.' + chapter
        print(formatted_query)
    if (unit == "verses"):
        formatted_query = book_dict[book] + '.' + chapter + '.' + verse
        print(formatted_query)
else:
    print("Book not found!")
    exit()

url = f"https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/{unit}/{formatted_query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
headers = {'api-key': A_KEY}
response = requests.request("GET", url, headers=headers)
# print(response.text)
data = response.json()

try:
    verse_content = data["data"]["content"]
    verse_text = ""
    for item in verse_content:
        if "items" in item:
            for sub_item in item["items"]:
                if "text" in sub_item:
                    verse_text += sub_item["text"]
    print(verse_text)
    if (len(verse_text) > 1):
        telnyx.Message.create(                                                      from_=number,                                                           to=destination,                                                         text=verse_text,
        )
except KeyError:
    print("Fetch failed!")
