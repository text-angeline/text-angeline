### "What hath God wrought"

import os
import re
import json
import boto3
import telnyx
import xml.etree.ElementTree as ET

### Configuration
telnyx.api_key = os.environ["TELNYX_KEY"]
TELNYX_NUMBER = os.environ["TELNYX_NUMBER"]
DEFAULT_TRANS = os.environ.get("DEFAULT_TRANS", "niv")

S3_BUCKET = os.environ.get("TRANS_BUCKET", "")
S3_PREFIX = os.environ.get("TRANS_PREFIX", "trans/")

s3 = boto3.client("s3") if S3_BUCKET else None

### Constants
SMS_MAX_CAP = 160
MMS_MAX_CAP = 1600
CACHE_DIR = "/tmp/trans"
GSM_CHAR_SET = frozenset(
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "\n\r !\"#$%&'()*+,-./:;<=>?@[\\]^_{}|~"
)

### Translation dictionary
# Maps short codes to S3 keys (language/file.xml)
TRANSLATIONS = {
    # Basque
    "bhnt": "baq/bhnt.xml",
    # Coptic
    "cnt": "cop/cnt.xml",
    # Danish
    "d31": "dan/d31.xml",
    # Dutch
    "dsv": "dut/dsv.xml",
    # English
    "abc": "eng/abc.xml", "acv": "eng/acv.xml", "akjv": "eng/akjv-strong.xml",
    "amp": "eng/amp.xml", "bb": "eng/bb.xml", "bbe": "eng/bbe.xml",
    "cev": "eng/cev.xml", "cjb": "eng/cjb.xml", "cvb": "eng/cvb.xml",
    "dby": "eng/dby.xml", "drb": "eng/drb.xml", "ejb": "eng/ejb.xml",
    "erv": "eng/erv.xml", "esv": "eng/esv.xml", "gb": "eng/gb.xml",
    "gnb": "eng/gnb.xml", "gw": "eng/gw.xml", "hcsb": "eng/hcsb.xml",
    "kj21": "eng/kj21.xml", "litv": "eng/litv.xml", "lxxe": "eng/lxxe.xml",
    "mkjv": "eng/mkjv.xml", "msg": "eng/msg.xml", "nasb": "eng/nasb-strong.xml",
    "nasu": "eng/nasu.xml", "ncv": "eng/ncv.xml", "net": "eng/net.xml",
    "nirv": "eng/nirv.xml", "niv": "eng/niv-1984.xml", "nivuk": "eng/nivuk.xml",
    "njb": "eng/njb.xml", "nkjv": "eng/nkjv.xml", "nlt": "eng/nlt.xml",
    "nlv": "eng/nlv.xml", "nrsv": "eng/nrsv.xml", "rnkjv": "eng/rnkjv.xml",
    "rsv": "eng/rsv.xml", "rwb": "eng/rwb.xml", "tmb": "eng/tmb.xml",
    "tniv": "eng/tniv.xml", "trc": "eng/trc.xml", "vw": "eng/vw.xml",
    "web": "eng/web.xml", "ylt": "eng/ylt.xml",
    # French
    "dbyf": "fre/dby.xml", "dmb": "fre/dmb.xml",
    "lsg": "fre/lsg.xml", "ostr": "fre/ostr.xml",
    # German
    "elb": "ger/elb-strong.xml", "ebl1": "ger/elb1.xml",
    "lb": "ger/lb.xml", "lutd": "ger/lutd.xml", "s00": "ger/s00.xml",
    # Italian
    "lnd": "ita/lnd.xml", "nr2006": "ita/nr2006.xml", "riv": "ita/riv.xml",
    # Latin
    "nvul": "lat/nvul.xml", "v": "lat/v.xml",
    # Romanian
    "gps": "rum/gps.xml",
    # Spanish
    "oso": "spa/oso.xml", "rv09": "spa/rv09.xml",
    # Swedish
    "s17": "swe/s17.xml",
}

### Book lookup
BOOK_ALIASES = {
    ("help",): "HELP",
    ("start",): "START",
    ("stop",): "STOP",
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
    ("jude",): "Jude",
    ("rv", "rev", "reve", "revel", "revln", "rvlns", "revelation", "revelations"): "Revelation",
}
BOOKS = {alias: name for aliases, name in BOOK_ALIASES.items() for alias in aliases}

### Input pattern
INPUT_PATTERN = re.compile(
    r"^"
    r"((?P<book_num>[1-3])(?: )?)?"
    r"(?P<book_title>[a-zA-Z]{2,13}((?: )([a-zA-Z]{,2})(?: )[a-zA-Z]{,7})?)"
    r"(?:(?: )?(?P<Fch>\d+)"
        r"(?:[\.:](?P<FchFvrBeg>\d+))?(?:-(?P<FchFvrEnd>\d+))?"
        r"(?:,(?: )?(?P<FchSvrBeg>\d+))?(?:-(?P<FchSvrEnd>\d+))?"
        r"(?:,(?: )?(?P<FchTvrBeg>\d+))?(?:-(?P<FchTvrEnd>\d+))?"
    r")?"
    r"((?:;)(?: )?(?P<Sch>\d+)"
        r"(?:[\.:](?P<SchFvrBeg>\d+))?(?:-(?P<SchFvrEnd>\d+))?"
        r"(?:,(?: )?(?P<SchSvrBeg>\d+))?(?:-(?P<SchSvrEnd>\d+))?"
        r"(?:,(?: )?(?P<SchTvrBeg>\d+))?(?:-(?P<SchTvrEnd>\d+))?"
    r")?"
    r"((?:;)(?: )?(?P<Tch>\d+)"
        r"(?:[\.:](?P<TchFvrBeg>\d+))?(?:-(?P<TchFvrEnd>\d+))?"
        r"(?:,(?: )?(?P<TchSvrBeg>\d+))?(?:-(?P<TchSvrEnd>\d+))?"
        r"(?:,(?: )?(?P<TchTvrBeg>\d+))?(?:-(?P<TchTvrEnd>\d+))?"
    r")?"
    r"(?:(?: )?(?P<bible_trans>[0-9a-zA-Z]{1,6}))?"
    r"$"
)

GROUPS = [
    "Fch", "FchFvrBeg", "FchFvrEnd", "FchSvrBeg", "FchSvrEnd", "FchTvrBeg", "FchTvrEnd",
    "Sch", "SchFvrBeg", "SchFvrEnd", "SchSvrBeg", "SchSvrEnd", "SchTvrBeg", "SchTvrEnd",
    "Tch", "TchFvrBeg", "TchFvrEnd", "TchSvrBeg", "TchSvrEnd", "TchTvrBeg", "TchTvrEnd",
    "bible_trans",
]


class AngelineError(Exception):
    """Raised to abort processing and optionally send a message to the user."""
    def __init__(self, message="", is_error=True):
        self.message = message
        self.is_error = is_error
        super().__init__(message)


def send_message(protocol, payload, user_number):
    payload += "\n\n* Reply STOP to block, or HELP for assistance"
    print(f"[send] {protocol} to {user_number}: {len(payload)} chars")
    telnyx.Message.create(
        from_=TELNYX_NUMBER,
        to=user_number,
        text=payload,
        type_=protocol,
    )


def fetch_xml(trans_key):
    """Fetch translation XML from S3 with /tmp caching."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, trans_key.replace("/", "_"))

    # Warm Lambda cache hit
    if os.path.exists(cache_path):
        return ET.parse(cache_path).getroot()

    if not s3 or not S3_BUCKET:
        raise AngelineError("Translation storage not configured")

    s3_key = f"{S3_PREFIX}{trans_key}"
    s3.download_file(S3_BUCKET, s3_key, cache_path)
    return ET.parse(cache_path).getroot()


def determine_protocol(payload):
    extra = sum(3 for c in payload if c not in GSM_CHAR_SET)
    size = len(payload) + extra
    print(f"[size] {size} chars (payload={len(payload)}, non-gsm extra={extra})")

    if size <= 0:
        raise AngelineError("Text returned empty; Consider a different translation")
    if size <= SMS_MAX_CAP:
        return "SMS"
    if size <= MMS_MAX_CAP:
        return "MMS"
    raise AngelineError("Request too large; Consider a smaller request")


def build_payload(fetch_dict):
    root = fetch_xml(fetch_dict["trans_key"])
    payload = ""
    order = ["F", "S", "T"]

    # Book only (no chapter) — too large
    if fetch_dict["Fch"] is None:
        book_url = f"https://www.biblegateway.com/passage/?search={fetch_dict['book']}%201".replace(" ", "%20")
        raise AngelineError(f"Request too large; Consider visiting {book_url}")

    # Full chapter
    if fetch_dict["Fch"] and fetch_dict["FchFvrBeg"] is None:
        query = f".//BIBLEBOOK[@bname='{fetch_dict['book']}']/CHAPTER[@cnumber='{fetch_dict['Fch']}']"
        chapter = root.find(query)
        if chapter is None:
            raise AngelineError("Text doesn't exist")
        for verse in chapter.findall(".//VERS"):
            payload += f"{verse.attrib.get('vnumber')} {verse.text}\n"

    # Verse ranges
    for ch_order in order:
        base = f".//BIBLEBOOK[@bname='{fetch_dict['book']}']/CHAPTER[@cnumber='{fetch_dict[f'{ch_order}ch']}']"
        for i, vr_order in enumerate(order):
            beg_key = f"{ch_order}ch{vr_order}vrBeg"
            end_key = f"{ch_order}ch{vr_order}vrEnd"
            if not fetch_dict.get(beg_key):
                continue

            if i > 0:
                payload += "...\n"

            if fetch_dict[end_key] is None:
                # Single verse
                vn = fetch_dict[beg_key]
                verse = root.find(f"{base}/VERS[@vnumber='{vn}']")
                if verse is None or verse.text is None:
                    raise AngelineError("Text doesn't exist")
                payload += f"{vn} {verse.text}\n"
            else:
                # Range
                vn_beg = int(fetch_dict[beg_key])
                vn_end = int(fetch_dict[end_key])
                if vn_beg > vn_end:
                    raise AngelineError("Invalid range")
                if (vn_end - vn_beg) > 12:
                    raise AngelineError("Range request too large")
                for vn in range(vn_beg, vn_end + 1):
                    verse = root.find(f"{base}/VERS[@vnumber='{vn}']")
                    if verse is None or verse.text is None:
                        raise AngelineError("Text doesn't exist")
                    payload += f"{vn} {verse.text}\n"

        # Chapter separator
        idx = order.index(ch_order)
        if idx < len(order) - 1:
            next_ch = order[idx + 1]
            if fetch_dict.get(f"{next_ch}ch"):
                payload += "---\n"

    # Clean whitespace and Psalm titles
    payload = re.sub(r"[^\n\S]+", " ", payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    return payload


def process(user_input, user_number):
    cleaned = re.sub(r"\s+", " ", user_input.strip().lower())
    match = INPUT_PATTERN.match(cleaned)
    if not match:
        raise AngelineError("Invalid format")

    # Extract groups
    fetch_dict = {g: match.group(g) for g in GROUPS}
    book_num = match.group("book_num")
    book_title = match.group("book_title")

    # Resolve translation
    trans_code = fetch_dict["bible_trans"] or DEFAULT_TRANS
    if trans_code not in TRANSLATIONS:
        raise AngelineError("Unsupported translation")
    fetch_dict["trans_key"] = TRANSLATIONS[trans_code]

    # Resolve book
    book_key = f"{book_num} {book_title}" if book_num else book_title
    if book_key not in BOOKS:
        raise AngelineError("Couldn't locate book")

    book = BOOKS[book_key]

    # Handle control commands
    if book == "HELP":
        raise AngelineError(
            "        AngeLine\nThe text-messenger of God.\n\n"
            "Official website: Text-AngeLine.org\n"
            "Contact support: support@text-angeline.org\n"
            "Usage guidelines: github.com/text-angeline\n\n"
            "Copyright (c) 2024 Dane Hobrecht. All Rights Reserved.",
            is_error=False,
        )
    if book in ("START", "STOP"):
        raise AngelineError("", is_error=False)

    fetch_dict["book"] = book
    payload = build_payload(fetch_dict)
    protocol = determine_protocol(payload)
    try:
        send_message(protocol, payload, user_number)
    except telnyx.error.InvalidRequestError:
        raise AngelineError("Request too large for this translation")
