import json
import requests

with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['key']

book_dict = {
    "genesis": "GEN",
    "exodus": "EXO",
    "leviticus": "LEV",
    "numbers": "NUM",
    "deutoronomy": "DEU",
    "josiah": "JOS",
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
    "psalms": "PSA",
    "proverbs": "PRO",
    "ecclesiastes": "ECC",
    "song of solomon": "SNG",
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
    "galations": "GAL",
    "ephesians": "EPH",
    "phillipians": "PHP",
    "colossians": "COL",
    "1 thessalonians": "1TH",
    "2 thessalonians": "1TH",
    "1 timothy": "1TI",
    "2 timothy": "2TI",
    "titus": "TIT",
    "philemon": "PHM",
    "hebrew": "HEB",
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
space_split = query.split()
book = space_split[0]
chapter = space_split[1]

try:
    colon_split = query.split(':')
    print(colon_split)
    verse = colon_split[1]
    unit = "verses"
except:
    unit = "chapters"

space_split = colon_split[0].split()
print(space_split)
book = space_split[0]
chapter = space_split[1]

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
    print("Not found!")
    exit()

url = f"https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/{unit}/{formatted_query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
headers = {'api-key': api_key}
response = requests.request("GET", url, headers=headers)
### print(response.text)
data = response.json()

verse_content = data['data']['content']
verse_text = ''
for item in verse_content:
    if 'items' in item:
        for sub_item in item['items']:
            if 'text' in sub_item:
                verse_text += sub_item['text']
print(verse_text)

# query = input("Query: ")
# formatted_query = query.lower()
# if (formatted_query in books):
#     print("Book found!")
# else:
#     print("Not found!")
