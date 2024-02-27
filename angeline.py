### Let the Ghost remind me, day in and day out, that this program is for Him alone.

import re
import json
import telnyx
import requests
import xml.etree.ElementTree as ET

### Configuration settings
with open("config.json", 'r') as f:
    config = json.load(f)

telnyx.api_key = config["TELNYX_KEY"]
DEFAULT_TRANS = config["DEFAULT_TRANS"]
TELNYX_NUMBER = config["TELNYX_NUMBER"]

### Translation dictionary
trans_dict = {
    "asv": "asv.xml",
    "kjv": "kjv.xml",
    "web": "web.xml",
}

### Book dictionary
book_dict = {
    "genesis": "Gen",
    "exodus": "Exod",
    "leviticus": "Lev",
    "numbers": "Num",
    "deutoronomy": "Deut",
    "joshua": "Josh",
    "judges": "Judg",
    "ruth": "Ruth",
    "1 samuel": "1Sam",
    "2 samuel": "2Sam",
    "1 kings": "1Kgs",
    "2 kings" :"2Kgs",
    "1 chronicles": "1Chr",
    "2 chronicles": "2Chr",
    "ezra": "Ezra",
    "nehemiah": "Neh",
    "esther": "Esth",
    "job": "Job",
    "psalm": "Ps",
    "proverbs": "Prov",
    "ecclesiastes": "Eccl",
    "song of songs": "Song",
    "song of solomon": "Song",
    "isaiah": "Isa",
    "jeremiah": "Jer",
    "lamentations": "Lam",
    "ezekiel": "Ezek",
    "daniel": "Dan",
    "hosea": "Hos",
    "joel": "Joel",
    "amos": "Amos",
    "obadiah": "Obad",
    "jonah": "Jonah",
    "micah": "Mic",
    "nahum": "Nah",
    "habakkuk": "Hab",
    "zephaniah": "Zeph",
    "haggai": "Hah",
    "zechariah": "Zech",
    "malachi": "Mal",
    "matthew": "Matt",
    "mark": "Mark",
    "luke": "Luke",
    "john": "John",
    "acts": "Acts",
    "romans": "Rom",
    "1 corinthians": "1Cor",
    "2 corinthians": "2Cor",
    "galatians": "Gal",
    "ephesians": "Eph",
    "philippians": "Phil",
    "colossians": "Col",
    "1 thessalonians": "1Thess",
    "2 thessalonians": "2Thess",
    "1 timothy": "1Tim",
    "2 timothy": "2Tim",
    "titus": "Titus",
    "philemon": "Phlm",
    "hebrews": "Heb",
    "james": "Jas",
    "1 peter": "1Pet",
    "2 peter": "2Pet",
    "1 john": "1John",
    "2 john": "2John",
    "3 john": "3John",
    "jude": "Jude",
    "revelations": "Rev"
}

### Send text message
def send_message(message_protocol, text_content, user_number):
    # Allow development halt (uncomment):
    # return
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=text_content,
        type_=message_protocol,
    )

### Throw error message
def throw_error(error_content, user_number):
    text_content = f"Error: {error_content}. Please try again."
    print(f"Text: {text_content}")
    send_message("SMS", text_content, user_number)
    raise Exception("Aborting")

### Init (Development)
def init_dev():
    dev_input = input("dev_input: ")
    dev_number = config['dev_number']
    init(dev_input, dev_number)

### Init (Production) 
def init(user_input, user_number):
    pattern = r"^(((?P<book_num>[1-9])(?: ))?(?P<book_title>[a-zA-Z]{3,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)(?: (?P<chapter>\d{1,3}))?(?::(?P<verse_beg>\d{1,3}))?(?:-(?P<verse_end>\d{1,3}))?(?: (?P<bible_trans>[a-zA-Z]{,4}))?)$"
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
            throw_error("Couldn't parse request", user_number)
    else:
        throw_error("Invalid format", user_number)

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
        throw_error("Couldn't locate book", user_number)
    
    # Unit
    if (chapter is None):
        unit = "books"
    elif (verse_beg is None):
        unit = "chapters"
        # Ex: "Gen.1"
        query = f"{book_dict[book]}.{chapter}"
    else:
        unit = "verses"
        # Ex: "Gen.1.1
        query = f"{book_dict[book]}.{chapter}.{verse_beg}"
    
    # Output (System)
    print(
        f"""Translation:\t\t{bible_trans.upper()}
Book:\t\t\t{book_title.capitalize()}
Unit:\t\t\t{unit.capitalize()}
Chapter:\t\t{chapter}
Verse (Beginning):\t{verse_beg}
Verse (Ending):\t\t{verse_end}"""
    )

    # Fetch text
    if (chapter is None):
        book_url = f"https://www.biblegateway.com/passage/?search={book}&version={bible_trans}".replace(' ', "%20")
        error_content = f"Payload too large; Consider visiting {book_url}"
        throw_error(error_content, user_number)
    else:
        fetch_text(bible, unit, query, user_number)

### Fetch text
def fetch_text(bible, unit, query, user_number, retries = 0):
    url = "https://raw.githubusercontent.com/bzerangue/osis-bibles/master/en/asv.xml"
    response = requests.get(url)
    # tree = ET.parse(bible)
    root = ET.fromstring(response.content)
    # root = tree.getroot()
    
    ns = {'osis': 'http://www.bibletechnologies.net/2003/OSIS/namespace'} 
    text_element = root.find(f".//osis:verse[@osisID='{query}']", namespaces=ns)

    if text_element is not None:
        text_content = text_element.text
    else:
        throw_error("Text not found", user_number)

    # Determine message type based on payload size
    text_content_size = len(text_content)
    if (text_content_size <= 0):
        throw_error("Text returned empty; Consider a different translation", user_number)
    elif (text_content_size <= 160):
        message_protocol = "SMS"
    elif (text_content_size <= 1600):
        message_protocol = "MMS"
    elif (text_content_size > 1600):
        # To-do: Implement chunking function
        throw_error("Payload too large; Consider a smaller request", user_number)
    print(f"Text: {text_content}")
    send_message(message_protocol, text_content, user_number)

# Allow development run (uncomment):
# init_dev()
