### Let the Lord remind me, day in and day out, that this program is for Him alone.

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

### Send text message
def send_message(message_protocol, text_content, user_number):
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=text_content,
        type_=message_protocol,
    )

### Throw error message
def throw_error(error_content, user_number):
    text_content = f"Error: {error_content}. Please try again."
    print(f"text_content: {text_content}")
    # Allow development halt (uncomment):
    # return
    send_message("SMS", text_content, user_number)
    raise Exception("Aborting")

### Init (Development)
def init_dev():
    dev_input = input("dev_input: ")
    dev_number = config['dev_number']
    init(dev_input, dev_number)

### Init (Production) 
def init(user_input, user_number):
    pattern = r"^(((?P<book_num>[1-3])(?: ))?(?P<book_title>[a-zA-Z]{3,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)(?: (?P<chapter>\d{1,3}))?(?::(?P<verse_beg>\d{1,3}))?(?:-(?P<verse_end>\d{1,3}))?(?: (?P<bible_trans>[a-zA-Z]{,4}))?)$"
    cleaned_user_input = re.sub(r"\s+", ' ', user_input.lower())
    match = re.match(pattern, cleaned_user_input)
    if (match):
        try:
            book_num = match.group("book_num")
            book_title = match.group("book_title")
            chapter = match.group("chapter")
            verse_beg = match.group("verse_beg")
            verse_end = match.group("verse_end")
            bible_trans = match.group("bible_trans")
        except AttributeError:
            throw_error("Could not parse request", user_number)
    else:
        throw_error("Invalid format")

    # Translation (if none specified)
    if (bible_trans is None):
        bible_trans = DEFAULT_TRANS
        bible = trans_dict[bible_trans]
    elif (bible_trans in trans_dict):
        bible = trans_dict[bible_trans]
    else:
        throw_error("Invalid translation", user_number)

    # Book
    if (book_num is None):
        book = str(book_title)
    else:
        # Ex: "1 kings"
        book = str(f"{book_num} {book_title}")
    if (book not in book_dict):
        throw_error("Could not locate book", user_number)
    
    # Unit
    if (chapter is None):
        unit = "books"
    elif (verse_beg is None):
        unit = "chapters"
        # Ex: "MAT.1"
        query = f"{book_dict[book]}.{chapter}"
    else:
        unit = "verses"
        # Ex: "MAT.1.1
        query = f"{book_dict[book]}.{chapter}.{verse_beg}"
    
    # Output (System)
    print(f"""
        Translation:\t\t{bible_trans.upper()}
        Book:\t\t\t{book_title.capitalize()}
        Unit:\t\t\t{unit.capitalize()}
        Chapter:\t\t{chapter}
        Verse (Beginning):\t{verse_beg}
        Verse (Ending):\t\t{verse_end}
    """)

    # Fetch text
    if (chapter is None):
        book_url = f"https://www.biblegateway.com/passage/?search={book}&version={bible_trans}".replace(' ', "%20")
        error_content = f"Payload too large; Consider visiting {book_url}"
        throw_error(error_content, user_number)
    else:
        fetch_text(bible, unit, query, user_number)

### Fetch text
def fetch_text(bible, unit, query, user_number):
    url = f"https://api.scripture.api.bible/v1/bibles/{bible}/{unit}/{query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
    headers = {"api-key": API_BIBLE_KEY}
    api_bible_response = requests.request("GET", url, headers=headers)
    # print(api_bible_response.text)
    api_bible_data = api_bible_response.json()

    # Text extraction/delivery
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
            throw_error("Couldn't fetch text; Consider a different translation", user_number)
        elif (text_content_size <= 160):
            message_protocol = "SMS"
        elif (text_content_size <= 1600):
            message_protocol = "MMS"
        elif (text_content_size > 1600):
            # To-do: Implement chunking function
            throw_error("Payload too large; Consider a smaller request", user_number)
        print(f"text_content: {text_content}")
        # Allow development halt (uncomment):
        # return
        send_message(message_protocol, text_content, user_number)
    except KeyError:
        throw_error("Something went wrong", user_number)

# Allow development run (uncomment):
# init_dev()
