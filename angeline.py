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

### Language dictionary
lang_def = "en"
lang_dict = {
    "en": "en",
    "eng": "en",
    "english": "en"
}

### Translation dictionary
trans_url_base = f"https://raw.githubusercontent.com/text-angeline/text-angeline/main/trans/{lang_def}/"
trans_dict = {
    "esv": f"{trans_url_base}esv.xml",
    "kj21": f"{trans_url_base}kj21.xml",
    "nasb": f"{trans_url_base}nasb-strong.xml",
    "nasu": f"{trans_url_base}nasu.xml",
    "niv": f"{trans_url_base}niv.xml",
    "nkjv": f"{trans_url_base}nkjv.xml",
    "nlt": f"{trans_url_base}nlt.xml",
    "nrsv": f"{trans_url_base}nrsv.xml",
    "rsv": f"{trans_url_base}rsv.xml",
    "web": f"{trans_url_base}web.xml"
}

### Book dictionary
book_dict = {
    # Controls
    "start": "START",
    "help": "HELP",
    # Books
    "gen": "Genesis",
    "genesis": "Genesis",
    "exo": "Exodus",
    "exodus": "Exodus",
    "lev": "Leviticus",
    "leviticus": "Leviticus",
    "num": "Numbers",
    "numbers": "Numbers",
    "deu": "Deuteronomy",
    "deuteronomy": "Deuteronomy",
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
    "psalms": "Psalm",
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
def send_message(protocol, payload, user_number):
    # Allow development halt (uncomment):
    # return
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=payload,
        type_=protocol
    )

### Throw error message
def raise_exception(is_error, text_content, user_number):
    if (is_error):
        payload = f"Error: {text_content}. Please try again."
    else:
        payload = text_content
    print(f"Text:\n{payload}#")
    if (text_content):
        send_message("SMS", payload, user_number)
    raise Exception("Aborting")

### Init (Development)
def init_dev():
    dev_input = input("dev_input: ")
    dev_number = config['dev_number']
    init(dev_input, dev_number)

### Init (Production)
def init(user_input, user_number):
    pattern = r"^(((?P<book_num>[1-9])(?: )?)?(?P<book_title>[a-zA-Z]{2,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)(?: (?P<chapter>\d{1,3}))?(?:(?::(?P<fir_verse_beg>\d{1,3}))?(?:-(?P<fir_verse_end>\d{1,3}))?(?:,(?P<sec_verse_beg>\d{1,3}))?)(?:-(?P<sec_verse_end>\d{1,3}))?(?: (?P<bible_trans>[0-9a-zA-Z]{,4}))?)$"
    cleaned_user_input = re.sub(r"\s+", ' ', user_input.strip().lower())
    match = re.match(pattern, cleaned_user_input)
    if (match):
        try:
            book_num = match.group("book_num")
            book_title = match.group("book_title")
            chapter = match.group("chapter")
            fir_verse_beg = match.group("fir_verse_beg")
            fir_verse_end = match.group("fir_verse_end")
            sec_verse_beg = match.group("sec_verse_beg")
            sec_verse_end = match.group("sec_verse_end")
            bible_trans = match.group("bible_trans")
        except AttributeError:
            raise_exception(True, "Couldn't parse request", user_number)
    else:
        raise_exception(True, "Invalid format", user_number)

    # Translation (if none specified)
    if (bible_trans is None):
        bible_trans = DEFAULT_TRANS
        bible = trans_dict[bible_trans]
    elif (bible_trans in trans_dict):
        bible = trans_dict[bible_trans]
    else:
        raise_exception(True, "Invalid translation", user_number)

    # Controls/Book
    try:
        if (book_num is None):
            if (book_dict[book_title] == "START"):
                raise_exception(False, "", user_number)
            elif (book_dict[book_title] == "HELP"):
                raise_exception(False, "AngeLine\n\nThe text-messenger of God.\n\nOfficial website: Text-AngeLine.org\nContact support: support@text-angeline.org\nUsage guidelines: github.com/text-angeline\n\n⫺ Reply STOP to block.", user_number)
            else:
                # Ex: "John"
                book = book_dict[book_title]
        else:
            # Ex: "1 John"
            book = book_dict[f"{book_num} {book_title}"]
    except KeyError:
        raise_exception(True, "Couldn't locate book", user_number)

    # Output (System)
    print(
        f"""Translation:\t\t {bible_trans.upper()}
Book:\t\t\t {book}
Chapter:\t\t {chapter}
Verse (Beginning):\t {fir_verse_beg}
Verse (Ending):\t\t {fir_verse_end}
Verse (Beginning [New]): {sec_verse_beg}
Verse (End [New]):\t {sec_verse_end}"""
    )

    # Fetch text
    # Try passing a dictionary of values?
    fetch_text(bible, bible_trans, book, chapter, fir_verse_beg, fir_verse_end, sec_verse_beg, sec_verse_end, user_number)

### Fetch text
def fetch_text(bible, bible_trans, book, chapter, fir_verse_beg, fir_verse_end, sec_verse_beg, sec_verse_end, user_number):
    try:
        ## Local XML:
        # tree = ET.parse(bible)
        # root = tree.getroot()
        ## Remote XML:
        response = requests.get(bible)
        root = ET.fromstring(response.content)
    except Exception:
        raise_exception(True, "Couldn't fetch text", user_number)

    query_base = f".//BIBLEBOOK[@bname='{book}']/CHAPTER[@cnumber='{chapter}']"
    try:
        # Book
        payload = ""
        if (chapter is None):
            # Unsupported Bible Gateway translation(s)
            if (bible_trans == "nasu"):
                bible_trans = "nasb"
            book_url = f"https://www.biblegateway.com/passage/?search={book}%201&version={bible_trans.upper()}".replace(' ', "%20")
            raise_exception(True, f"Request too large; Consider visiting {book_url}", user_number)
        # Chapter
        elif (fir_verse_beg is None):
            chapter = root.find(query_base)
            for verse in chapter.findall(".//VERS"):
                verse_number = verse.attrib.get("vnumber")
                payload += f"{verse_number} {verse.text}\n"
        # Verse (Range)
        elif (fir_verse_end is not None):
            if (int(fir_verse_beg) > int(fir_verse_end)):
                raise_exception(True, "Invalid range", user_number)
            elif ((int(fir_verse_end) - int(fir_verse_beg)) <= 12):
                payload = ""
                for verse_num in range(int(fir_verse_beg), int(fir_verse_end) + 1):
                    text_element = root.find(f"{query_base}/VERS[@vnumber='{verse_num}']")
                    payload += f"{verse_num} {text_element.text}\n"
            else:
                raise_exception(True, "Range request too large", user_number)
        # Verse (Individual)
        elif (fir_verse_beg is not None):
            path = f"{query_base}/VERS[@vnumber='{fir_verse_beg}']"
            text_element = root.find(path)
            payload += f"{fir_verse_beg} {text_element.text}\n"
        # Verse (Range [New])
        if (sec_verse_end is not None):
            if (int(sec_verse_beg) > int(sec_verse_end)):
                raise_exception(True, "Invalid range", user_number)
            elif ((int(sec_verse_end) - int(sec_verse_beg)) <= 12):
                payload += "...\n"
                for verse_num in range(int(sec_verse_beg), int(sec_verse_end) + 1):
                    text_element = root.find(f"{query_base}/VERS[@vnumber='{verse_num}']")
                    payload += f"{verse_num} {text_element.text}\n"
            else:
                raise_exception(True, "Range request too large", user_number)
        # Verse (Individual [New])
        elif (sec_verse_beg):
            path = f"{query_base}/VERS[@vnumber='{sec_verse_beg}']"
            text_element = root.find(path)
            payload += f"...\n{sec_verse_beg} {text_element.text}"
    except AttributeError:
        raise_exception(True, "Text doesn't exist", user_number)

    # Cleanup extranneous whitespace/Psalm titles
    payload = re.sub(r'[^\n\S]+', ' ', payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    # Append "opt-out" prompt for compliance
    payload += "\n\n⫺ Reply STOP to block, or HELP for assistance."

    # Determine message type based on payload size
    payload_size = len(payload)
    if (payload_size <= 0):
        raise_exception(True, "Text returned empty; Consider a different translation", user_number)
    elif (payload_size <= 160):
        protocol = "SMS"
    elif (payload_size <= 1600):
        protocol = "MMS"
    elif (payload_size > 1600):
        # To-do: Implement chunking function
        raise_exception(True, "Request too large; Consider a smaller request", user_number)
    print(f"Text:\n{payload}#")
    send_message(protocol, payload, user_number)

# Allow development run (uncomment):
# init_dev()
