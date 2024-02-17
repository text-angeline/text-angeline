### Let the Lord remind me, day in and day out, that this program is for Him alone.

### To-do:
# - Determine if API supports verse ranges with hyphens
#  - Ex: Matthew 1:3-7
# - Add robust error exception handling
#  - Send instructional message upon reciept of invalid input
#  - API-side failure message (please try again)
### Future aspirations:
# - Add spell correction feature
#  - Book, epistle, etc. titles
# - Include reference data
# - Create dedicated website

### Example requests:
# Under 160 characters: Psalm 117
# Under 1600 characters: Psalm 23
# Exceeds 1600 characters: Psalm 119

import re
import json
import time
import telnyx
import requests

### Configuration settings
with open("config.json", 'r') as f:
    config = json.load(f)

telnyx.api_key = config["TELNYX_KEY"]
API_BIBLE_KEY = config["API_BIBLE_KEY"]
DEFAULT_TRANS = config["DEFAULT_TRANS"]
TELNYX_NUMBER = config["TELNYX_NUMBER"]

### API.bible translation dictionary
trans_dict = {
    "asv": "06125adad2d5898a-01",
    "fbv": "65eec8e0b60e656b-01",
    "kjv": "de4e12af7f28f599-02",
    "web": "9879dbb7cfe39e4d-04",
}

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
    "galatians": "GAL",
    "ephesians": "EPH",
    "philippians": "PHP",
    "colossians": "COL",
    "1 thessalonians": "1TH",
    "2 thessalonians": "2TH",
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
    test_number = config['test_number']
    init(test_input, test_number)

### Initial function
def init(user_input, user_number):
    target_number = user_number
    input_formatting(user_input, user_number)

### Input formatting
def input_formatting(user_input, user_number):
    pattern = r"^(((?P<book_num>[1-3])(?: ))?(?P<book_title>[a-zA-Z]{3,}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)(?: (?P<chapter>\d{1,3}))(?::(?P<verse_beg>\d{1,3}))?(?:-(?P<verse_end>\d{1,3}))?(?: (?P<bible_trans>[a-zA-Z]{,4}))?)$"
    match = re.match(pattern, user_input.lower())
    if (match):
        try:
            book_num = match.group("book_num")
            book_title = match.group("book_title")
            chapter = match.group("chapter")
            verse_beg = match.group("verse_beg")
            verse_end = match.group("verse_end")
            bible_trans = match.group("bible_trans")
        except AttributeError:
            print("Error: Couldn't parse input.")
            return
    else:
        print("Error: Invalid format.")
        return

    # Default translation (if not specified)
    if (bible_trans is None):
        bible = trans_dict[DEFAULT_TRANS]
        print(f"Translation: {DEFAULT_TRANS}")
    elif (bible_trans in trans_dict):
        bible = trans_dict[bible_trans]
        print(f"Translation: {bible_trans}")

    # Check for series
    if (book_num is None):
        book = str(book_title)
    else:
        # Ex: "1 kings"
        book = str(f"{book_num} {book_title}")

    if (book in book_dict):
        if (verse_beg is None):
            unit = "chapters"
            # Ex: "MAT.1"
            query = f"{book_dict[book]}.{chapter}"
        else:
            unit = "verses"
            # Ex: "MAT.1.1
            query = f"{book_dict[book]}.{chapter}.{verse_beg}"
        
        # System output
        print(f"Unit: {unit}\nBook: {book}\nChapter: {chapter}")
        if (unit == "verses"):
            print(f"Beginning Verse: {verse_beg}\nEnding Verse: {verse_end}")
    else:
        print("Error: Could not locate book (is it spelled correctly?).")
        return
    text_request(bible, unit, query, user_number)

### API.Bible content request
def text_request(bible, unit, query, user_number):
    url = f"https://api.scripture.api.bible/v1/bibles/{bible}/{unit}/{query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
    headers = {"api-key": API_BIBLE_KEY}
    api_bible_response = requests.request("GET", url, headers=headers)
    # print(api_bible_response.text)
    api_bible_data = api_bible_response.json()

    ### Text extraction/delivery
    try:
        data_content = api_bible_data['data']['content']
        # print(data_content)
        text_content = ""
        for item in data_content:
            if 'items' in item:
                for sub_item in item['items']:
                    # Only prepends verse numbers when necessary
                    if (unit == "chapters"):
                        if 'attrs' in sub_item and 'number' in sub_item['attrs']:
                            verse_number = sub_item['attrs']['number']
                            text_content += f" {verse_number}"
                    if "text" in sub_item:
                        verse_text = sub_item['text'].strip()
                        text_content += f" {verse_text}"
        
        # Determine message type based on payload size
        text_content = text_content.strip()
        text_content_size = len(text_content)
        if (text_content_size <= 0):
            print("Error: API returned missing text content.")
            return
        elif (text_content_size <= 160):
            message_protocol = "SMS"
        elif (text_content_size <= 1600):
            message_protocol = "MMS"
        elif (text_content_size > 1600):
            # Implement chunking function
            print("Error: Text content missing/too large.")
            return
        print(f"Text Content: {text_content}") 
        # Prevent send_message (development)
        # return
        send_message(message_protocol, text_content, user_number)
    except KeyError as e:
        print("Error: Text extraction/delivery failed: ", e)

# Send SMS message
def send_message(message_protocol, text_content, user_number):
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=text_content,
        type_=message_protocol,
    )

### Allow development run (comment when done)
init_dev()
