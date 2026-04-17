### "What hath God wrought"

import os
import re
import boto3
import telnyx
import xml.etree.ElementTree as ET

### Configuration settings
telnyx.api_key = os.environ["TELNYX_KEY"]
TELNYX_NUMBER = os.environ["TELNYX_NUMBER"]
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
    ("rv", "rev", "reve", "revel", "revln", "rvlns", "revelation", "revelations",) : "Revelation"
}
book_dict = { key: value for keys, value in book_dict_tup.items() for key in keys }

### Pre-compiled input pattern
pattern = re.compile(
    r"^("
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
    r")$"
)

### Raise exception
class AngelineError(Exception):
    def __init__(self, message="", is_error=True):
        self.message = message
        self.is_error = is_error
        super().__init__(message)

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

### Fetch text
def fetch_text(trans_key, user_number):
    # In-memory cache (survives across warm Lambda invocations)
    if trans_key in _xml_cache:
        return _xml_cache[trans_key]

    try:
        ## S3:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_path = os.path.join(CACHE_DIR, trans_key.replace("/", "_"))

        # Disk cache (survives across warm invocations too)
        if not os.path.exists(cache_path):
            if not s3 or not S3_BUCKET:
                raise AngelineError("Translation storage not configured")
            s3.download_file(S3_BUCKET, f"{S3_PREFIX}{trans_key}", cache_path)

        root = ET.parse(cache_path).getroot()
        _xml_cache[trans_key] = root
        return root
    except AngelineError:
        raise
    except Exception:
        raise AngelineError("Couldn't fetch text")

### Determine message protocol
def determine_protocol(payload, user_number):
    payload_size = len(payload)
    for char in payload:
        if (char not in GSM_CHAR_SET):
            payload_size += 3
    print("Approximate payload size:", payload_size)
    if (payload_size <= 0):
        raise AngelineError("Text returned empty; Consider a different translation")
    elif (payload_size <= SMS_MAX_CAP):
        protocol = "SMS"
    elif (payload_size > SMS_MAX_CAP and payload_size <= MMS_MAX_CAP):
        protocol = "MMS"
    elif (payload_size > MMS_MAX_CAP):
        # To-do: Implement chunking function
        raise AngelineError("Request too large; Consider a smaller request")
    return protocol

### Build text payload
def build_payload(fetch_dict, user_number):
    root = fetch_text(fetch_dict["trans_key"], user_number)
    try:
        payload = ""
        request_order = ['F', 'S', 'T']

        ## Book
        if (fetch_dict["Fch"] is None):
            book_url = f"https://www.biblegateway.com/passage/?search={fetch_dict['book']}%201".replace(' ', "%20")
            raise AngelineError(f"Request too large; Consider visiting {book_url}")

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
                            raise AngelineError("Invalid range")
                        elif ((vr_num_end - vr_num_beg) <= 12):
                            if (is_new):
                                payload += "...\n"
                            for vr_num in range(vr_num_beg, (vr_num_end + 1)):
                                verse = root.find(f"{base_query}/VERS[@vnumber='{vr_num}']")
                                payload += f"{vr_num} {verse.text}\n"
                        else:
                            raise AngelineError("Range request too large")

            ## Separate chapters
            ch_index = request_order.index(ch_order)
            if (ch_index < (len(request_order) - 1)):
                ch_next = request_order[ch_index + 1]
                if (fetch_dict[f"{ch_next}ch"]):
                    payload += "---\n"
    except AttributeError:
        raise AngelineError("Text doesn't exist")

    # Cleanup extranneous whitespace/Psalm titles
    payload = re.sub(r'[^\n\S]+', ' ', payload.rsplit("Psalm", 2)[0].replace("`", "'").strip())
    # Determine message protocol based on payload size
    protocol = determine_protocol(payload, user_number)
    try:
        send_message(protocol, payload, user_number)
    except telnyx.error.InvalidRequestError:
        raise AngelineError("Request too large for this translation")

### Initial
def init(user_input, user_number):
    cleaned_user_input = re.sub(r"\s+", ' ', user_input.strip().lower())
    match = pattern.match(cleaned_user_input)
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
            raise AngelineError("Couldn't parse request")
    else:
        raise AngelineError("Invalid format")

    ## Translation
    if fetch_dict["bible_trans"] is None:
        fetch_dict["trans_key"] = trans_dict[DEFAULT_TRANS]
    elif fetch_dict["bible_trans"] in trans_dict:
        fetch_dict["trans_key"] = trans_dict[fetch_dict["bible_trans"]]
    else:
        raise AngelineError("Unsupported translation")

    ## Controls/Book
    try:
        if (book_num is None):
            if (book_dict[book_title] == "HELP"):
                raise AngelineError("        AngeLine\nThe text-messenger of God.\n\nOfficial website: Text-AngeLine.org\nContact support: support@text-angeline.org\nUsage guidelines: github.com/text-angeline\n\nCopyright (c) 2024 Dane Hobrecht. All Rights Reserved.", is_error=False)
            elif (book_dict[book_title] == "START"):
                raise AngelineError("", is_error=False)
            elif (book_dict[book_title] == "STOP"):
                raise AngelineError("", is_error=False)
            else:
                # Ex: "John"
                fetch_dict["book"] = book_dict[book_title]
        else:
            # Ex: "1 John"
            fetch_dict["book"] = book_dict[f"{book_num} {book_title}"]
    except KeyError:
        raise AngelineError("Couldn't locate book")

    # Build message payload
    build_payload(fetch_dict, user_number)

# Allow development run (uncomment):
# init(input("dev_input = "), "+19493573901")
