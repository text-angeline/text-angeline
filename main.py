### To-do:
# - Add verse numbers before lines
# - Increase robustness of detection algorithmi
#  - RegEx validation?
# - Add translation detection (default: ESV)
#  - Ex: Matthew 1:2 KJV
#  - Add respective dictionary and parsing ability
# - Add verse detection with hyphens
#  - Ex: Matthew 1:3-7
# - Fix verse spacing issue
# - Add robust error exception handling
#  - Send instructional message upon reciept of invalid input
#  - API-side failure message (please try again)
#  - Etc.
### Future aspirations:
# - Add spell correction feature
#  - Book, epistle titles
# - Include reference data

import json
import telnyx
import requests

### Configuration settings
with open("config.json", 'r') as f:
    config = json.load(f)
bible_id = config["bible_id"]
telnyx.api_key = config["TELNYX_KEY"]
API_BIBLE_KEY = config["API_BIBLE_KEY"]
TELNYX_NUMBER = config["TELNYX_NUMBER"]

### API.Bible book dictionary
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

### Development function
def init_dev():
    test_input = input("test_input: ")
    test_number = config["test_number"]
    init(test_input, test_number)

### Initial function
def init(user_input, user_number):
    target_number = user_number
    input_formatting(user_input, user_number)

### Input formatting
def input_formatting(user_input, user_number):
    query = user_input.lower()
    try:
        colon_split = query.split(':')
        print("colon_split:", colon_split)
        verse = colon_split[1]
        unit = "verses"
    except:
        unit = "chapters"
    space_split = colon_split[0].split()
    print("space_split:", space_split)
    # Individual
    if (len(space_split) == 2):
        book = space_split[0]
        chapter = space_split[1]
    # Series
    elif (len(space_split) == 3):
        book = space_split[0] + ' ' + space_split[1]
        chapter = space_split[2]
    
    print(f"Unit: {unit}\nBook: {book}\nChapter: {chapter}")
    if (unit == "verses"):
        print("Verse:", verse)

    # Unit detection
    if (book in book_dict):
        if (unit == "chapters"):
            # Ex: "MAT.1"
            formatted_query = book_dict[book] + '.' + chapter
        if (unit == "verses"):
            # Ex: "MAT.1.3"
            formatted_query = book_dict[book] + '.' + chapter + '.' + verse
        print(formatted_query)
    else:
        print("Could not locate book (is it spelled correctly?).")
        return
    text_request(unit, formatted_query, user_number)

### API.Bible content request
def text_request(unit, formatted_query, user_number):
    url = f"https://api.scripture.api.bible/v1/bibles/{bible_id}/{unit}/{formatted_query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
    headers = {"api-key": API_BIBLE_KEY}
    api_bible_response = requests.request("GET", url, headers=headers)
    # print(response.text)
    api_bible_data = api_bible_response.json()

    ### Text extraction/delivery
    try:
        data_content = api_bible_data["data"]["content"]
        print(data_content)
        text_content = ""
        for item in data_content:
            if "items" in item:
                for sub_item in item["items"]:
                    if "text" in sub_item:
                        text_content += sub_item["text"]
        print(text_content)
        send_message(user_number, text_content)
    except KeyError as e:
        print("Error: Text extraction/delivery failed -", e)

# Send SMS message
def send_message(user_number, text_content):
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=text_content,
    )

### Allow development run (comment when done)
# init_dev()
