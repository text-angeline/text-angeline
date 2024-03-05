### "What hath God wrought"

import re
import json
import telnyx
import string
import requests
import xml.etree.ElementTree as ET

### Configuration settings
with open("config.json", 'r') as file:
    config = json.load(file)

telnyx.api_key = config["TELNYX_KEY"]
DEFAULT_TRANS = config["DEFAULT_TRANS"]
TELNYX_NUMBER = config["TELNYX_NUMBER"]

### Translation dictionary
temp_request_url = "https://raw.githubusercontent.com/text-angeline/text-angeline/main"
trans_dict = {
    "esv": f"{temp_request_url}/trans/en/esv.xml",
    "kjv": f"{temp_request_url}/trans/en/kjv.xml",
    "nasb": f"{temp_request_url}/trans/en/nasb-strong.xml",
    "nasu": f"{temp_request_url}/trans/en/nasu.xml",
    "nkjv": f"{temp_request_url}/trans/en/nkjv.xml",
    "nlt": f"{temp_request_url}/trans/en/nlt.xml",
    "nrsv": f"{temp_request_url}/trans/en/nrsv.xml",
    "rsv": f"{temp_request_url}/trans/en/rsv.xml",
    "web": f"{temp_request_url}/trans/en/web.xml"
}

### Book dictionary
book_dict = {
    "gen": "Genesis",
    "genesis": "Genesis",
    "exo": "Exodus",
    "exodus": "Exodus",
    "lev": "Leviticus",
    "leviticus": "Leviticus",
    "num": "Numbers",
    "numbers": "Numbers",
    "deu": "Deutoronomy",
    "deutoronomy": "Deutoronomy",
    "jos": "Joshua",
    "joshua": "Joshua",
    "jdg": "Judges",
    "judges": "Judges",
    "rut": "Ruth",
    "ruth": "Ruth",
    "1 sa": "1 Samuel",
    "1 samuel": "1 Samuel",
    "2 sa": "2 Samuel",
    "2 samuel": "2 Samuel",
    "1 ki": "1 Kings",
    "1 kings": "1 Kings",
    "2 ki": "2 Kings",
    "2 kings" :"2 Kings",
    "1 ch": "1 Chronicles",
    "1 chronicles": "1 Chronicles",
    "2 ch": "2 Chronicles",
    "2 chronicles": "2 Chronicles",
    "ezr": "Ezra",
    "ezra": "Ezra",
    "neh": "Nehemiah",
    "nehemiah": "Nehemiah",
    "est": "Esther",
    "esther": "Esther",
    "job": "Job",
    "psa": "Psalm",
    "psalm": "Psalm",
    "pro": "Proverbs",
    "proverbs": "Proverbs",
    "ecc": "Ecclesiastes",
    "ecclesiastes": "Ecclesiastes",
    "son": "Song of Solomon",
    "song of songs": "Song of Solomon",
    "song of solomon": "Song of Solomon",
    "isa": "Isaiah",
    "isaiah": "Isaiah",
    "jer": "Jeremiah",
    "jeremiah": "Jeremiah",
    "lam": "Lamentations",
    "lamentations": "Lamentations",
    "eze": "Ezekiel",
    "ezekiel": "Ezekiel",
    "dan": "Daniel",
    "daniel": "Daniel",
    "hos": "Hosea",
    "hosea": "Hosea",
    "joe": "Joel",
    "joel": "Joel",
    "amo": "Amos",
    "amos": "Amos",
    "oba": "Obadiah",
    "obadiah": "Obadiah",
    "jon": "Jonah",
    "jonah": "Jonah",
    "mic": "Micah",
    "micah": "Micah",
    "nah": "Nahum",
    "nahum": "Nahum",
    "hab": "Habakkuk",
    "habakkuk": "Habakkuk",
    "zep": "Zephaniah",
    "zephaniah": "Zephaniah",
    "hag": "Haggai",
    "haggai": "Haggai",
    "zec": "Zechariah",
    "zechariah": "Zechariah",
    "mal": "Malachi",
    "malachi": "Malachi",
    "mat": "Matthew",
    "matthew": "Matthew",
    "mar": "Mark",
    "mark": "Mark",
    "luk": "Luke",
    "luke": "Luke",
    "jhn": "John",
    "john": "John",
    "act": "Acts",
    "acts": "Acts",
    "rom": "Romans",
    "romans": "Romans",
    "1 co": "1 Cortinthians",
    "1 corinthians": "1 Corinthians",
    "2 co": "2 Corinthians",
    "2 corinthians": "2 Corinthians",
    "gal": "Galatians",
    "galatians": "Galatians",
    "eph": "Ephesians",
    "ephesians": "Ephesians",
    "phi": "Philippians",
    "philippians": "Philippians",
    "col": "Colossians",
    "colossians": "Colossians",
    "1 th": "1 Thessalonians",
    "1 thessalonians": "1 Thessalonians",
    "2 th": "2 Thessalonians",
    "2 thessalonians": "2 Thessalonians",
    "1 ti": "1 Timothy",
    "1 timothy": "1 Timothy",
    "2 ti": "2 Timothy",
    "2 timothy": "2 Timothy",
    "tit": "Titus",
    "titus": "Titus",
    "phm": "Philemon",
    "philemon": "Philemon",
    "heb": "Hebrews",
    "hebrews": "Hebrews",
    "jam": "James",
    "james": "James",
    "1 pe": "1 Peter",
    "1 peter": "1 Peter",
    "2 pe": "2 Peter",
    "2 peter": "2 Peter",
    "1 jn": "1 John",
    "1 john": "1 John",
    "2 jn": "2 John",
    "2 john": "2 John",
    "3 jn": "3 jhn",
    "3 john": "3 John",
    "jud": "Jude",
    "jude": "Jude",
    "rev": "Revelation",
    "revelation": "Revelation"
}

### Send text message
def send_message(message_protocol, text_content, user_number):
    # Allow development halt (uncomment):
    # return
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=text_content,
        type_=message_protocol
    )

### Throw error message
def throw_error(error_message, user_number):
    error_content = f"Error: {error_message}. Please try again."
    print(f"Text:\n{error_content}#")
    send_message("SMS", error_content, user_number)
    raise Exception("Aborting")

### Init (Development)
def init_dev():
    dev_input = input("⫺ ")
    dev_number = config['dev_number']
    init(dev_input, dev_number)

### Init (Production)
def init(user_input, user_number):
    pattern = r"^(((?P<book_num>[1-9])(?: )?)?(?P<book_title>[a-zA-Z]{2,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)(?: (?P<chapter>\d{1,3}))?(?:(?::(?P<verse_beg>\d{1,3}))(?:-(?P<verse_end>\d{1,3}))?)?(?: (?P<bible_trans>[a-zA-Z]{,4}))?)$"
    cleaned_user_input = re.sub(r"\s+", ' ', user_input.strip().lower())
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
    try:
        if (book_num is None):
            # Ex: "John"
            book = book_dict[book_title]
        else:
            # Ex: "1 John"
            book = book_dict[f"{book_num} {book_title}"]
    except KeyError:
        throw_error("Couldn't locate book", user_number)

    # Output (System)
    print(
        f"""Translation:\t\t{bible_trans.upper()}
Book:\t\t\t{book}
Chapter:\t\t{chapter}
Verse (Beginning):\t{verse_beg}
Verse (Ending):\t\t{verse_end}"""
    )

    # Fetch text
    # Try passing a dictionary of values?
    fetch_text(bible, bible_trans, book, chapter, verse_beg, verse_end, user_number)

### Fetch text
def fetch_text(bible, bible_trans, book, chapter, verse_beg, verse_end, user_number):
    try:
        ## Local XML:
        # tree = ET.parse(bible)
        # root = tree.getroot()
        ## Remote XML:
        response = requests.get(bible)
        root = ET.fromstring(response.content)
    except Exception:
        throw_error("Couldn't fetch text", user_number)

    query_base = f".//BIBLEBOOK[@bname='{book}']/CHAPTER[@cnumber='{chapter}']"
    try:
        # Book
        if (chapter is None):
            # Unsupported Bible Gateway translation(s)
            if (bible_trans == "nasu"):
                bible_trans = "nasb"
            book_url = f"https://www.biblegateway.com/passage/?search={book}%201&version={bible_trans.upper()}".replace(' ', "%20")
            throw_error(f"Payload too large; Consider visiting {book_url}", user_number)
        # Chapter
        elif (verse_beg is None):
            text_content = ""
            chapter = root.find(query_base)
            for verse in chapter.findall(".//VERS"):
                verse_number = verse.attrib.get("vnumber")
                verse_text = verse.text
                text_content += f"{verse_number} {verse_text}\n"
        # Passage
        elif (verse_end is not None):
            if (int(verse_beg) > int(verse_end)):
                throw_error("Invalid range", user_number)
            elif ((int(verse_end) - int(verse_beg)) <= 12):
                text_content = ""
                for verse_num in range(int(verse_beg), int(verse_end) + 1):
                    text_element = root.find(f"{query_base}/VERS[@vnumber='{verse_num}']")
                    verse_text = text_element.text
                    text_content += f"{verse_num} {verse_text}\n"
            else:
                throw_error("Range request too large", user_number)
        # Verse
        elif (verse_beg is not None):
            path = f"{query_base}/VERS[@vnumber='{verse_beg}']"
            text_element = root.find(path)
            text_content = text_element.text
    except AttributeError:
        throw_error("Text doesn't exist", user_number)

    # Cleanup extranneous whitespace/Psalm titles
    text_content = re.sub(r'[^\n\S]+', ' ', text_content.rsplit("Psalm", 2)[0].replace("`", "'").strip())

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
        throw_error("Request too large; Consider a smaller request", user_number)
    print(f"Text:\n{text_content}#")
    send_message(message_protocol, text_content, user_number)

# Allow development run (uncomment):
# init_dev()
