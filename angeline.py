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

### Global variables

## Constants
SMS_MAX_CAP = 160
MMS_MAX_CAP = 1600

## Configuration
telnyx.api_key = config["TELNYX_KEY"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]
DEFAULT_TRANS = config["DEFAULT_TRANS"]
TELNYX_NUMBER = config["TELNYX_NUMBER"]

### Dictionaries

## Character
char_dict = {
    # Spanish (ES)
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'ñ': 'n', 'Ñ': 'N', '¡': ''
}

## Translation
trans_dict_url = f"https://raw.githubusercontent.com/text-angeline/text-angeline/main/trans/"
trans_dict = {
    # Dutch (NL)
    "dsv": f"{trans_dict_url}nl/dsv.xml",
    # English (EN)
    "esv": f"{trans_dict_url}en/esv.xml",
    "kj21": f"{trans_dict_url}en/kj21.xml",
    "nasb": f"{trans_dict_url}en/nasb-strong.xml",
    "nasu": f"{trans_dict_url}en/nasu.xml",
    "niv": f"{trans_dict_url}en/niv.xml",
    "nkjv": f"{trans_dict_url}en/nkjv.xml",
    "nlt": f"{trans_dict_url}en/nlt.xml",
    "nrsv": f"{trans_dict_url}en/nrsv.xml",
    "rsv": f"{trans_dict_url}en/rsv.xml",
    "web": f"{trans_dict_url}en/web.xml",
    # Spanish (ES)
    "oso": f"{trans_dict_url}es/oso.xml"
}

## Book
book_dict_tup = {
    # Controls
    ("help",): "HELP",
    ("start",): "START",
    ("stop",): "STOP",
    # Books
    ("gn", "gen", "gene", "gens", "genes", "genesis"): "Genesis",
    ("ex", "exo", "exod", "exodu", "exods", "exodus"): "Exodus",
    ("lv", "lev", "levi", "levit", "leviticus"): "Leviticus",
    ("nu", "num", "numb", "nums", "numbr", "numbs", "numbers"): "Numbers",
    ("dt", "deu", "deut", "deute", "deutr", "deuteronomy"): "Deuteronomy",
    ("js", "jos", "josh", "joshu", "joshua"): "Joshua",
    ("jd", "jdg", "judg", "judge", "judges"): "Judges",
    ("rt", "rut", "ruth"): "Ruth",
    ("1 sa", "1 sam", "1 samu", "1 same", "1 samue", "1 samuel"): "1 Samuel",
    ("2 sa", "2 sam", "1 samu", "1 same", "2 samue", "2 samuel"): "2 Samuel",
    ("1 ki", "1 kin", "1 king", "1 kings"): "1 Kings",
    ("2 ki", "2 kin", "2 king", "2 kings"): "2 Kings",
    ("1 ch", "1 chr", "1 chro", "1 chrn", "1 chron", "1 chronicles"): "1 Chronicles",
    ("2 ch", "2 chr", "2 chro", "1 chrn", "2 chron", "2 chronicles"): "2 Chronicles",
    ("er", "ezr", "ezra"): "Ezra",
    ("nh", "neh", "nehe", "nehem", "nehemiah"): "Nehemiah",
    ("et", "est", "esth", "esthr", "esther"): "Esther",
    ("jb", "job"): "Job",
    ("ps", "psa", "psal", "psalm", "psalms"): "Psalm",
    ("pr", "pro", "prov", "prove", "provs", "provb", "proverbs"): "Proverbs",
    ("ec", "ecc", "eccs", "eccle", "eccls", "ecclesiastes"): "Ecclesiastes",
    ("sn", "son", "song", "solom", "song of songs", "song of solomon"): "Song of Solomon",
    ("is", "isa", "isai", "isaia", "isaiah"): "Isaiah",
    ("jr", "jer", "jere", "jerem", "jeremiah"): "Jeremiah",
    ("lm", "lam", "lame", "lamen", "lamnt", "lamns", "lamentations"): "Lamentations",
    ("ez", "eze", "ezek", "ezeki", "ezekl", "ezekiel"): "Ezekiel",
    ("dn", "dan", "dani", "danie", "daniel"): "Daniel",
    ("hs", "hos", "hose", "hosea"): "Hosea",
    ("jl", "joe", "joel"): "Joel",
    ("am", "amo", "amos"): "Amos",
    ("ob", "oba", "obad", "obadi", "obadh", "obadiah"): "Obadiah",
    ("jo", "jon", "jona", "jonah"): "Jonah",
    ("mi", "mic", "mica", "micah"): "Micah",
    ("na", "nah", "nahu", "nahum"): "Nahum",
    ("hb", "hab", "haba", "habak", "habakkuk"): "Habakkuk",
    ("zp", "zep", "zepe", "zepha", "zephn", "zephaniah"): "Zephaniah",
    ("hg", "hag", "hagg", "hagga", "haggai"): "Haggai",
    ("zc", "zec", "zech", "zecha", "zechr", "zechariah"): "Zechariah",
    ("ml", "mal", "mala", "malac", "malch", "malci", "malachi"): "Malachi",
    ("mt", "mat", "matt", "matth", "matte", "mattw", "matthew"): "Matthew",
    ("mr", "mar", "mark"): "Mark",
    ("lk", "luk", "luke"): "Luke",
    ("jn", "jhn", "john"): "John",
    ("ac", "act", "acts"): "Acts",
    ("rm", "rom", "roms", "roman", "romns", "romans"): "Romans",
    ("1 co", "1 cor", "1 cori", "1 corin", "1 crths", "1 corinthians"): "1 Corinthians",
    ("2 co", "2 cor", "2 cori", "1 corin", "1 crths", "2 corinthians"): "2 Corinthians",
    ("gl", "gal", "gala", "galat", "galas", "galatians"): "Galatians",
    ("ep", "eph", "ephe", "ephes", "ephns", "ephesians"): "Ephesians",
    ("ph", "phi", "phil", "phili", "philp", "phpns", "philippians"): "Philippians",
    ("cl", "col", "colo", "colos", "clsns", "colossians"): "Colossians",
    ("1 th", "1 ths", "1 thes", "1 thess", "1 thesl", "1 thessalonians"): "1 Thessalonians",
    ("2 th", "2 ths", "2 thes", "2 thess", "2 thesl", "2 thessalonians"): "2 Thessalonians",
    ("1 ti", "1 tim", "1 timo", "1 timot", "1 tmthy", "1 timothy"): "1 Timothy",
    ("2 ti", "2 tim", "2 timo", "2 timot", "2 tmthy", "2 timothy"): "2 Timothy",
    ("ti", "tit", "titu", "titus"): "Titus",
    ("pm", "phm", "phmn", "phile", "phlmn", "philemon"): "Philemon",
    ("he", "heb", "hebr", "hebre", "hbrws", "hebrews"): "Hebrews",
    ("jm", "jam", "jame", "james"): "James",
    ("1 pe", "1 pet", "1 pete", "1 peter"): "1 Peter",
    ("2 pe", "2 pet", "2 pete", "2 peter"): "2 Peter",
    ("1 jn", "1 jhn", "1 john"): "1 John",
    ("2 jn", "2 jhn", "2 john"): "2 John",
    ("3 jn", "3 jhn", "3 john"): "3 John",
    ("jd", "jud", "jude"): "Jude",
    ("rv", "rev", "reve", "revel", "revln", "rvlns", "revelation", "revelations",) : "Revelation"
}
book_dict = { key: value for keys, value in book_dict_tup.items() for key in keys }

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
    payload += "\n\n* Reply STOP to block, or HELP for assistance."
    # System log
    print(payload)
    if (text_content):
        send_message("SMS", payload, user_number)
    raise Exception("Aborting")

### Initial
def init(user_input, user_number):
    pattern = (
        r"^("
            r"((?P<book_num>[1-9])(?: )?)?"
            r"(?P<book_title>[a-zA-Z]{2,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)"

            r"(?:(?: )?(?P<Fch>\d{1,3})"
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

            r"(?:(?: )?(?P<bible_trans>[0-9a-zA-Z]{3,4}))?"
        r")$"
    )

    cleaned_user_input = re.sub(r"\s+", ' ', user_input.strip().lower())
    match = re.match(pattern, cleaned_user_input)
    if (match):
        try:
            book_num = match.group("book_num")
            book_title = match.group("book_title")
            fetch_dict = {
                "Fch": match.group("Fch"),
                "FchFvrBeg": match.group("FchFvrBeg"),
                "FchFvrEnd": match.group("FchFvrEnd"),
                "FchSvrBeg": match.group("FchSvrBeg"),
                "FchSvrEnd": match.group("FchSvrEnd"),
                "FchTvrBeg": match.group("FchTvrBeg"),
                "FchTvrEnd": match.group("FchTvrEnd"),

                "Sch": match.group("Sch"),
                "SchFvrBeg": match.group("SchFvrBeg"),
                "SchFvrEnd": match.group("SchFvrEnd"),
                "SchSvrBeg": match.group("SchSvrBeg"),
                "SchSvrEnd": match.group("SchSvrEnd"),
                "SchTvrBeg": match.group("SchTvrBeg"),
                "SchTvrEnd": match.group("SchTvrEnd"),

                "Tch": match.group("Tch"),
                "TchFvrBeg": match.group("TchFvrBeg"),
                "TchFvrEnd": match.group("TchFvrEnd"),
                "TchSvrBeg": match.group("TchSvrBeg"),
                "TchSvrEnd": match.group("TchSvrEnd"),
                "TchTvrBeg": match.group("TchTvrBeg"),
                "TchTvrEnd": match.group("TchTvrEnd"),

                "bible_trans": match.group("bible_trans"),
            }
        except AttributeError:
            raise_exception(True, "Couldn't parse request", user_number)
    else:
        raise_exception(True, "Invalid format", user_number)

    ## Translation
    if fetch_dict["bible_trans"] is None:
        bible_trans = DEFAULT_TRANS
        fetch_dict["bible_xml"] = trans_dict[DEFAULT_TRANS]
    elif fetch_dict["bible_trans"] in trans_dict:
        fetch_dict["bible_xml"] = trans_dict[fetch_dict["bible_trans"]]
    else:
        raise_exception(True, "Unsupported translation", user_number)

    ## Controls/Book
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
                fetch_dict["book"] = book_dict[book_title]
        else:
            # Ex: "1 John"
            fetch_dict["book"] = book_dict[f"{book_num} {book_title}"]
    except KeyError:
        raise_exception(True, "Couldn't locate book", user_number)

    # Build message payload
    build_payload(fetch_dict, user_number)

### Fetch text
def fetch_text(fetch_dict, user_number):
    try:
        ## Local:
        # tree = ET.parse(bible)
        # root = tree.getroot()

        ## Remote:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.raw"
        }
        response = requests.get(fetch_dict["bible_xml"], headers=headers)
        root = ET.fromstring(response.content)
        return root
    except Exception:
        raise_exception(True, "Couldn't fetch text", user_number)

### Determine message protocol
def determine_protocol(payload, user_number):
    payload_size = len(payload)
    if (payload_size <= 0):
        raise_exception(True, "Text returned empty; Consider a different translation", user_number)
    elif (payload_size <= SMS_MAX_CAP):
        protocol = "SMS"
    elif (payload_size > SMS_MAX_CAP and payload_size <= MMS_MAX_CAP):
        protocol = "MMS"
    elif (payload_size > MMS_MAX_CAP):
        # To-do: Implement chunking function
        raise_exception(True, "Request too large; Consider a smaller request", user_number)
    return protocol

### Build text payload
def build_payload(fetch_dict, user_number):
    root = fetch_text(fetch_dict, user_number)
    try:
        payload = ""
        request_order = ['F', 'S', 'T']

        ## Book
        if (fetch_dict["Fch"] is None):
            # Unsupported Bible Gateway translation(s)
            if (fetch_dict["bible_trans"] == "nasu"):
                bible_trans = "nasb"
            book_url = f"https://www.biblegateway.com/passage/?search={fetch_dict['book']}%201&version={fetch_dict['bible_trans'].upper()}".replace(' ', "%20")
            raise_exception(True, f"Request too large; Consider visittrans_dict_urling {book_url}", user_number)

        ## Chapter
        if (fetch_dict["Fch"] and fetch_dict["FchFvrBeg"] is None):
            base_query = f".//BIBLEBOOK[@bname='{fetch_dict['book']}']/CHAPTER[@cnumber='{fetch_dict['Fch']}']"
            chapter = root.find(base_query)
            for verse in chapter.findall(".//VERS"):
                vr_num = verse.attrib.get("vnumber")
                payload += f"{vr_num} {verse.text}\n"

        ## Verse(s)
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

                    ## Range
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

            ## Separate chapters
            ch_index = request_order.index(ch_order)
            if (ch_index < len(request_order) - 1):
                ch_next = request_order[ch_index + 1]
                if (fetch_dict[f"{ch_next}ch"]):
                    payload += "~\n"
    except AttributeError:
        raise_exception(True, "Text doesn't exist", user_number)

    # Cleanup extranneous whitespace/Psalm titles
    payload = re.sub(r'[^\n\S]+', ' ', payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    # Replace special characters with Latin-based equivalents
    for char, replacement in char_dict.items():
        payload = payload.replace(char, replacement)
    # Append "opt-out" prompt for compliance
    payload += "\n\n* Reply STOP to block, or HELP for assistance."
    # Determine message protocol based on payload size
    protocol = determine_protocol(payload, user_number)
    # System log
    print(payload)
    try:
        send_message(protocol, payload, user_number)
    except telnyx.error.InvalidRequestError:
        raise_exception(True, "Request too large for this translation", user_number)

# Allow development run (uncomment):
# init(input("dev_input = "), config["dev_number"])
