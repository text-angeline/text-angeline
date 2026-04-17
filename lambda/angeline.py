### "What hath God wrought"

import os
import re
import boto3
import telnyx
import xml.etree.ElementTree as ET
from datetime import datetime

### Configuration settings
telnyx.api_key = os.environ.get("TELNYX_KEY", "")
TELNYX_NUMBER = os.environ.get("TELNYX_NUMBER", "")
DEFAULT_TRANS = os.environ.get("DEFAULT_TRANS", "niv")
S3_BUCKET = os.environ.get("TRANS_BUCKET", "")
S3_PREFIX = os.environ.get("TRANS_PREFIX", "trans/")

s3 = boto3.client("s3") if S3_BUCKET else None

### Global variables

## Constants
SMS_MAX_CAP = 160
MMS_MAX_CAP = 1600
CACHE_DIR = "/tmp/trans"
GSM_CHAR_SET = frozenset(
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "\n\r !\"#$%&'()*+,-./:;<=>?@[\\]^_{}|~"
)

## In-memory cache (persists across warm Lambda invocations)
_xml_cache = {}

### Dictionaries

## Translation
trans_dict = {
    # Basque (baq)
    "bhnt": "baq/bhnt.xml",
    # Coptic (cop)
    "cnt": "cop/cnt.xml",
    # Danish (dan)
    "d31": "dan/d31.xml",
    # Dutch (dut)
    "dsv": "dut/dsv.xml",
    # English (eng)
    "abc": "eng/abc.xml",
    "acv": "eng/acv.xml",
    "akjv": "eng/akjv-strong.xml",
    "amp": "eng/amp.xml",
    "bb": "eng/bb.xml",
    "bbe": "eng/bbe.xml",
    "cev": "eng/cev.xml",
    "cjb": "eng/cjb.xml",
    "cvb": "eng/cvb.xml",
    "dby": "eng/dby.xml",
    "drb": "eng/drb.xml",
    "ejb": "eng/ejb.xml",
    "erv": "eng/erv.xml",
    "esv": "eng/esv.xml",
    "gb": "eng/gb.xml",
    "gnb": "eng/gnb.xml",
    "gw": "eng/gw.xml",
    "hcsb": "eng/hcsb.xml",
    "kj21": "eng/kj21.xml",
    "litv": "eng/litv.xml",
    "lxxe": "eng/lxxe.xml",
    "mkjv": "eng/mkjv.xml",
    "msg": "eng/msg.xml",
    "nasb": "eng/nasb-strong.xml",
    "nasu": "eng/nasu.xml",
    "ncv": "eng/ncv.xml",
    "net": "eng/net.xml",
    "nirv": "eng/nirv.xml",
    "niv": "eng/niv-1984.xml",
    "nivuk": "eng/nivuk.xml",
    "njb": "eng/njb.xml",
    "nkjv": "eng/nkjv.xml",
    "nlt": "eng/nlt.xml",
    "nlv": "eng/nlv.xml",
    "nrsv": "eng/nrsv.xml",
    "rnkjv": "eng/rnkjv.xml",
    "rsv": "eng/rsv.xml",
    "rwb": "eng/rwb.xml",
    "tmb": "eng/tmb.xml",
    "tniv": "eng/tniv.xml",
    "trc": "eng/trc.xml",
    "vw": "eng/vw.xml",
    "web": "eng/web.xml",
    "ylt": "eng/ylt.xml",
    # French (fre)
    "dbyf": "fre/dby.xml",
    "dmb": "fre/dmb.xml",
    "lsg": "fre/lsg.xml",
    "ostr": "fre/ostr.xml",
    # German (ger)
    "elb": "ger/elb-strong.xml",
    "ebl1": "ger/elb1.xml",
    "lb": "ger/lb.xml",
    "lutd": "ger/lutd.xml",
    "s00": "ger/s00.xml",
    # Italian (ita)
    "lnd": "ita/lnd.xml",
    "nr2006": "ita/nr2006.xml",
    "riv": "ita/riv.xml",
    # Latin (lat)
    "nvul": "lat/nvul.xml",
    "v": "lat/v.xml",
    # Romanian (rum)
    "gps": "rum/gps.xml",
    # Spanish (spa)
    "oso": "spa/oso.xml",
    "rv09": "spa/rv09.xml",
    # Swedish (swe)
    "s17": "swe/s17.xml"
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
    ("lv", "lev", "levi", "levt", "levit", "leviticus"): "Leviticus",
    ("nu", "num", "numb", "nums", "numbr", "numbs", "numbers"): "Numbers",
    ("dt", "deu", "deut", "deute", "deutr", "deuteronomy"): "Deuteronomy",
    ("js", "jos", "josh", "joshu", "joshua"): "Joshua",
    ("jd", "jdg", "judg", "judge", "judges"): "Judges",
    ("rt", "rut", "ruth"): "Ruth",
    ("1 sa", "1 sam", "1 samu", "1 same", "1 samue", "1 samuel"): "1 Samuel",
    ("2 sa", "2 sam", "2 samu", "2 same", "2 samue", "2 samuel"): "2 Samuel",
    ("1 ki", "1 kin", "1 king", "1 kings"): "1 Kings",
    ("2 ki", "2 kin", "2 king", "2 kings"): "2 Kings",
    ("1 ch", "1 chr", "1 chro", "1 chrn", "1 chron", "1 chronicles"): "1 Chronicles",
    ("2 ch", "2 chr", "2 chro", "2 chrn", "2 chron", "2 chronicles"): "2 Chronicles",
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
    ("2 co", "2 cor", "2 cori", "2 corin", "2 crths", "2 corinthians"): "2 Corinthians",
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
    ("rv", "rev", "reve", "revel", "revln", "rvlns", "revelation", "revelations",): "Revelation"
}
book_dict = {key: value for keys, value in book_dict_tup.items() for key in keys}

### Parsing

## Chapter reference pattern (applied per chunk after splitting on ";")
_ch_pattern = re.compile(
    r"^(?P<ch>\d+)"
    r"(?:[\.:](?P<verses>.+))?"
    r"$"
)

## Verse range pattern (applied per chunk after splitting on ",")
_vr_pattern = re.compile(r"^(?P<beg>\d+)(?:-(?P<end>\d+))?$")

## Full input pattern (book + optional chapter/verses + optional translation)
_input_pattern = re.compile(
    r"^(?:(?P<book_num>[1-3]) ?)?"
    r"(?P<book_title>[a-zA-Z]{2,13}(?:(?: [a-zA-Z]{,2}) [a-zA-Z]{,7})?)"
    r"(?: ?(?P<reference>.+?) ?(?P<bible_trans>[a-zA-Z]{1,6}))?$"
    r"|"
    r"^(?:(?P<book_num2>[1-3]) ?)?"
    r"(?P<book_title2>[a-zA-Z]{2,13}(?:(?: [a-zA-Z]{,2}) [a-zA-Z]{,7})?)"
    r"(?: ?(?P<reference2>.+?))?$"
)

def parse_input(user_input):
    """Parse user input into a structured request or command."""
    cleaned = re.sub(r"\s+", " ", user_input.strip().lower())

    ## Resolve book
    # Try to extract book title (with optional number prefix)
    book_match = re.match(
        r"^(?:(?P<book_num>[1-3]) ?)?"
        r"(?P<book_title>[a-zA-Z]{2,13}(?:(?: [a-zA-Z]{,2}) [a-zA-Z]{,7})?)"
        r"(?P<rest>.*)$",
        cleaned
    )
    if not book_match:
        raise AngelineError("Invalid format")

    book_num = book_match.group("book_num")
    book_title = book_match.group("book_title")
    rest = book_match.group("rest").strip()

    # Look up book
    book_key = f"{book_num} {book_title}" if book_num else book_title
    if book_key not in book_dict:
        raise AngelineError("Couldn't locate book")

    book = book_dict[book_key]

    ## Commands (not errors -normal control flow)
    if book == "HELP":
        return {
            "type": "command",
            "message": "        AngeLine\nThe text-messenger of God.\n\nOfficial website: Text-AngeLine.org\nContact support: support@text-angeline.org\nUsage guidelines: github.com/text-angeline\n\nCopyright (c) {datetime.now().year} Dane Hobrecht. All Rights Reserved."
        }
    if book in ("START", "STOP"):
        return {"type": "command", "message": ""}

    ## Parse reference and translation from the rest
    # Try to detect translation suffix (last word if it's a known translation code)
    bible_trans = DEFAULT_TRANS
    reference_str = rest

    if reference_str:
        parts = reference_str.rsplit(" ", 1)
        if len(parts) == 2 and parts[1] in trans_dict:
            reference_str = parts[0]
            bible_trans = parts[1]
        elif len(parts) == 1 and parts[0] in trans_dict and not parts[0][0].isdigit():
            # Bare translation code, no chapter reference
            bible_trans = parts[0]
            reference_str = ""

    if bible_trans not in trans_dict:
        raise AngelineError("Unsupported translation")

    ## Parse chapter references (split on ";")
    chapters = []
    if reference_str:
        for ch_chunk in reference_str.split(";"):
            ch_chunk = ch_chunk.strip()
            if not ch_chunk:
                continue

            ch_match = _ch_pattern.match(ch_chunk)
            if not ch_match:
                raise AngelineError("Invalid format")

            ch_num = ch_match.group("ch")
            verses_str = ch_match.group("verses")

            # Parse verse ranges (split on ",")
            verses = []
            if verses_str:
                for vr_chunk in verses_str.split(","):
                    vr_chunk = vr_chunk.strip()
                    vr_match = _vr_pattern.match(vr_chunk)
                    if not vr_match:
                        raise AngelineError("Invalid format")
                    beg = vr_match.group("beg")
                    end = vr_match.group("end")
                    if end and int(beg) > int(end):
                        raise AngelineError("Invalid range")
                    if end and (int(end) - int(beg)) > 12:
                        raise AngelineError("Range request too large")
                    verses.append({"beg": beg, "end": end})

            chapters.append({"ch": ch_num, "verses": verses})
    else:
        # Book only, no chapter -too large
        book_url = f"https://www.biblegateway.com/passage/?search={book}%201".replace(" ", "%20")
        raise AngelineError(f"Request too large; Consider visiting {book_url}")

    return {
        "type": "lookup",
        "book": book,
        "trans_key": trans_dict[bible_trans],
        "chapters": chapters
    }

### Fetch text
def fetch_text(trans_key):
    """Fetch translation XML with in-memory caching. Tries local, then S3."""
    # In-memory cache (survives across warm Lambda invocations)
    if trans_key in _xml_cache:
        return _xml_cache[trans_key]

    try:
        ## Local (development):
        local_path = os.path.join(os.path.dirname(__file__), "..", "trans", trans_key)
        if os.path.exists(local_path):
            root = ET.parse(local_path).getroot()
            _xml_cache[trans_key] = root
            return root

        ## S3 (production):
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_path = os.path.join(CACHE_DIR, trans_key.replace("/", "_"))

        # Disk cache (survives across warm invocations too)
        if not os.path.exists(cache_path):
            if not s3:
                raise AngelineError("Couldn't fetch text")
            s3.download_file(S3_BUCKET, f"{S3_PREFIX}{trans_key}", cache_path)

        root = ET.parse(cache_path).getroot()
        _xml_cache[trans_key] = root
        return root
    except AngelineError:
        raise
    except Exception:
        raise AngelineError("Couldn't fetch text")

### Build text payload
def build_payload(root, request):
    """Build the text payload from a structured request. Returns a string."""
    book = request["book"]
    lines = []

    for ch_idx, chapter in enumerate(request["chapters"]):
        base_query = f".//BIBLEBOOK[@bname='{book}']/CHAPTER[@cnumber='{chapter['ch']}']"

        if not chapter["verses"]:
            ## Full chapter
            ch_element = root.find(base_query)
            if ch_element is None:
                raise AngelineError("Text doesn't exist")
            for verse in ch_element.findall(".//VERS"):
                vr_num = verse.attrib.get("vnumber")
                lines.append(f"{vr_num} {verse.text}")
        else:
            ## Verse(s)
            for vr_idx, vr in enumerate(chapter["verses"]):
                if vr_idx > 0:
                    lines.append("...")

                if vr["end"] is None:
                    # Individual
                    verse = root.find(f"{base_query}/VERS[@vnumber='{vr['beg']}']")
                    if verse is None or verse.text is None:
                        raise AngelineError("Text doesn't exist")
                    lines.append(f"{vr['beg']} {verse.text}")
                else:
                    ## Range
                    for vr_num in range(int(vr["beg"]), int(vr["end"]) + 1):
                        verse = root.find(f"{base_query}/VERS[@vnumber='{vr_num}']")
                        if verse is None or verse.text is None:
                            raise AngelineError("Text doesn't exist")
                        lines.append(f"{vr_num} {verse.text}")

        ## Separate chapters
        if ch_idx < len(request["chapters"]) - 1:
            lines.append("---")

    payload = "\n".join(lines)
    # Cleanup extranneous whitespace/Psalm titles
    payload = re.sub(r'[^\n\S]+', ' ', payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    return payload

### Determine message protocol
def determine_protocol(payload):
    """Determine message protocol based on payload size."""
    payload_size = len(payload)
    for char in payload:
        if char not in GSM_CHAR_SET:
            payload_size += 3
    print("Approximate payload size:", payload_size)
    if payload_size <= 0:
        raise AngelineError("Text returned empty; Consider a different translation")
    elif payload_size <= SMS_MAX_CAP:
        return "SMS"
    elif payload_size <= MMS_MAX_CAP:
        return "MMS"
    else:
        # To-do: Implement chunking function
        raise AngelineError("Request too large; Consider a smaller request")

### Send text message
def send_message(protocol, payload, user_number):
    # Append "opt-out" prompt for compliance
    payload += "\n\n* Reply STOP to block, or HELP for assistance"
    # System log
    print(payload)
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=payload,
        type_=protocol
    )

### Raise exception
class AngelineError(Exception):
    def __init__(self, message="", is_error=True):
        self.message = message
        self.is_error = is_error
        super().__init__(message)

# Allow development run (uncomment):
request = parse_input(input("dev_input = "))
if request["type"] == "lookup":
    root = fetch_text(request["trans_key"])
    payload = build_payload(root, request)
    print(payload)
