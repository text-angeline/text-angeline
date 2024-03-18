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

SMS_MAX_CAP = 160
MMS_MAX_CAP = 1600

telnyx.api_key = config["TELNYX_KEY"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]
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
    "help": "HELP",
    "start": "START",
    "stop": "STOP",
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

### Raise exception
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
    dev_input = input("dev_input = ")
    dev_number = config['dev_number']
    init(dev_input, dev_number)

### Init (Production)
def init(user_input, user_number):
    pattern = (
        r"^("
            r"((?P<book_num>[1-9])(?: )?)?"
            r"(?P<book_title>[a-zA-Z]{2,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)"
            
            r"(?: (?P<Fch>\d{1,3})"
                r"(?:[\.:](?P<FchFvrBeg>\d{1,3}))?(?:-(?P<FchFvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<FchSvrBeg>\d{1,3}))?(?:-(?P<FchSvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<FchTvrBeg>\d{1,3}))?(?:-(?P<FchTvrEnd>\d{1,3}))?"
            r")?"

            r"((?:;)(?: )?(?P<Sch>\d{1,3})(?:[\.:])?"
                r"(?:[\.:](?P<SchFvrBeg>\d{1,3}))?(?:-(?P<SchFvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<SchSvrBeg>\d{1,3}))?(?:-(?P<SchSvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<SchTvrBeg>\d{1,3}))?(?:-(?P<SchTvrEnd>\d{1,3}))?"
            r")?"

            r"((?:;)(?: )?(?P<Tch>\d{1,3})(?:[\.:])?"
                r"(?:[\.:](?P<TchFvrBeg>\d{1,3}))?(?:-(?P<TchFvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<TchSvrBeg>\d{1,3}))?(?:-(?P<TchSvrEnd>\d{1,3}))?"
                r"(?:,(?: )?(?P<TchTvrBeg>\d{1,3}))?(?:-(?P<TchTvrEnd>\d{1,3}))?"
            r")?"

            r"(?: (?P<bible_trans>[0-9a-zA-Z]{,4}))?"
        r")$"
    )

    cleaned_user_input = re.sub(r"\s+", ' ', user_input.strip().lower())
    match = re.match(pattern, cleaned_user_input)
    if (match):
        try:
            book_num = match.group("book_num")
            book_title = match.group("book_title")

            Fch = match.group("Fch")
            FchFvrBeg = match.group("FchFvrBeg")
            FchFvrEnd = match.group("FchFvrEnd")
            FchSvrBeg = match.group("FchSvrBeg")
            FchSvrEnd = match.group("FchSvrEnd")
            FchTvrBeg = match.group("FchTvrBeg")
            FchTvrEnd = match.group("FchTvrEnd")

            Sch = match.group("Sch")
            SchFvrBeg = match.group("SchFvrBeg")
            SchFvrEnd = match.group("SchFvrEnd")
            SchSvrBeg = match.group("SchSvrBeg")
            SchSvrEnd = match.group("SchSvrEnd")
            SchTvrBeg = match.group("SchTvrBeg")
            SchTvrEnd = match.group("SchTvrEnd")

            Tch = match.group("Tch")
            TchFvrBeg = match.group("TchFvrBeg")
            TchFvrEnd = match.group("TchFvrEnd")
            TchSvrBeg = match.group("TchSvrBeg")
            TchSvrEnd = match.group("TchSvrEnd")
            TchTvrBeg = match.group("TchTvrBeg")
            TchTvrEnd = match.group("TchTvrEnd")

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
            if (book_dict[book_title] == "HELP"):
                raise_exception(False, "AngeLine\n\nThe text-messenger of God.\n\nOfficial website: Text-AngeLine.org\nContact support: support@text-angeline.org\nUsage guidelines: github.com/text-angeline\n\n⫺ Reply STOP to block.", user_number)
            elif (book_dict[book_title] == "START"):
                raise_exception(False, "", user_number)
            elif (book_dict[book_title] == "STOP"):
                raise_exception(False, "", user_number)
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
        f"""Book:\t\t{book}
Chapter:\t{Fch}
| Verse(s):\t{FchFvrBeg}-{FchFvrEnd}, {FchSvrBeg}-{FchSvrEnd}, {FchTvrBeg}-{FchTvrEnd}
Chapter:\t{Sch}
| Verse(s):\t{SchFvrBeg}-{SchFvrEnd}, {SchSvrBeg}-{SchSvrEnd}, {SchTvrBeg}-{SchTvrEnd}
Chapter:\t{Tch}
| Verse(s):\t{TchFvrBeg}-{TchFvrEnd}, {TchSvrBeg}-{TchSvrEnd}, {TchTvrBeg}-{TchTvrEnd}
Translation:\t{bible_trans.upper()}"""
    )

    fetch_dict = {
        "bible": bible,
        "bible_trans": bible_trans,
        "book": book,
        
        "Fch": Fch,
        "FchFvrBeg": FchFvrBeg,
        "FchFvrEnd": FchFvrEnd,
        "FchSvrBeg": FchSvrBeg,
        "FchSvrEnd": FchSvrEnd,
        "FchTvrBeg": FchTvrBeg,
        "FchTvrEnd": FchTvrEnd,
        
        "Sch": Sch,
        "SchFvrBeg": SchFvrBeg,
        "SchFvrEnd": SchFvrEnd,
        "SchSvrBeg": SchSvrBeg,
        "SchSvrEnd": SchSvrEnd,
        "SchTvrBeg": SchTvrBeg,
        "SchTvrEnd": SchTvrEnd,
        
        "Tch": Tch,
        "TchFvrBeg": TchFvrBeg,
        "TchFvrEnd": TchFvrEnd,
        "TchSvrBeg": TchSvrBeg,
        "TchSvrEnd": TchSvrEnd,
        "TchTvrBeg": TchTvrBeg,
        "TchTvrEnd": TchTvrEnd,
        
        "bible_trans": bible_trans
    }

    # Fetch text
    fetch_text(fetch_dict, user_number)

### Fetch text
def fetch_text(fetch_dict, user_number):
    try:
        ## Local XML:
        # tree = ET.parse(bible)
        # root = tree.getroot()
        ## Remote XML:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.raw"
        }
        response = requests.get(fetch_dict["bible"], headers=headers)
        root = ET.fromstring(response.content)
    except Exception:
        raise_exception(True, "Couldn't fetch text", user_number)

    try:
        # Book
        payload = ""
        request_order = ['F', 'S', 'T']
        if (fetch_dict["Fch"] is None):
            # Unsupported Bible Gateway translation(s)
            if (fetch_dict["bible_trans"] == "nasu"):
                bible_trans = "nasb"
            book_url = f"https://www.biblegateway.com/passage/?search={fetch_dict['book']}%201&version={fetch_dict['bible_trans'].upper()}".replace(' ', "%20")
            raise_exception(True, f"Request too large; Consider visiting {book_url}", user_number)

        # Chapter
        if (fetch_dict["Fch"] and fetch_dict["FchFvrBeg"] is None):
            base_query = f".//BIBLEBOOK[@bname='{fetch_dict['book']}']/CHAPTER[@cnumber='{fetch_dict['Fch']}']"
            chapter = root.find(base_query)
            for verse in chapter.findall(".//VERS"):
                vr_num = verse.attrib.get("vnumber")
                payload += f"{vr_num} {verse.text}\n"

        # Verse(s)
        for ch_order in request_order:
            base_query = f".//BIBLEBOOK[@bname='{fetch_dict['book']}']/CHAPTER[@cnumber='{fetch_dict[f'{ch_order}ch']}']"
            for vr_order in request_order:
                is_new = False
                if (vr_order != 'F'):
                    is_new = True
                if (fetch_dict[f"{ch_order}ch{vr_order}vrBeg"]):
                    # Individual
                    if (fetch_dict[f"{ch_order}ch{vr_order}vrEnd"] is None):
                        vr_num = fetch_dict[f"{ch_order}ch{vr_order}vrBeg"]
                        verse = root.find(f"{base_query}/VERS[@vnumber='{vr_num}']") 
                        if (is_new):
                            payload += "...\n"
                        payload += f"{vr_num} {verse.text}\n"
                    # Range
                    if (fetch_dict[f"{ch_order}ch{vr_order}vrEnd"] is not None):
                        vr_num_beg = int(fetch_dict[f"{ch_order}ch{vr_order}vrBeg"])
                        vr_num_end = int(fetch_dict[f"{ch_order}ch{vr_order}vrEnd"])
                        if (vr_num_beg > vr_num_end):
                            raise_exception(True, "Invalid range", user_number)
                        elif ((vr_num_end - vr_num_beg) <= 12):
                            if (is_new):
                                payload += "...\n"
                            for vr_num in range(vr_num_beg, (vr_num_end + 1)):
                                verse = root.find(f"{base_query}/VERS[@vnumber='{vr_num}']")
                                payload += f"{vr_num} {verse.text}\n"
                        else:
                            raise_exception(True, "Range request too large", user_number)
            # Print chapter separator
            ch_index = request_order.index(ch_order)
            if (ch_index < len(request_order) - 1):
                ch_next = request_order[ch_index + 1]
                if (fetch_dict[f"{ch_next}ch"]):
                    payload += "---\n"
    except AttributeError:
        raise_exception(True, "Text doesn't exist", user_number)

    # Cleanup extranneous whitespace/Psalm titles
    payload = re.sub(r'[^\n\S]+', ' ', payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    # Append "opt-out" prompt for compliance
    payload += "\n\n* Reply STOP to block, or HELP for assistance."

    # Determine message type based on payload size
    payload_size = len(payload)
    if (payload_size <= 0):
        raise_exception(True, "Text returned empty; Consider a different translation", user_number)
    elif (payload_size <= SMS_MAX_CAP):
        protocol = "SMS"
    elif (payload_size <= MMS_MAX_CAP):
        protocol = "MMS"
    elif (payload_size > MMS_MAX_CAP):
        # To-do: Implement chunking function
        raise_exception(True, "Request too large; Consider a smaller request", user_number)
    print(f"Protocol:\t{protocol} ({payload_size})\nText:\n{payload}")
    send_message(protocol, payload, user_number)

# Allow development run (uncomment):
# init_dev()