import os
import requests

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

def fetch_trans():
    for current_trans, url in trans_dict.items():
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs("trans/en", exist_ok=True)
            with open(f"trans/en/{current_trans}.xml", "wb") as f:
                f.write(response.content)
                print(f"Data for {current_trans} has been fetched and written to trans/en/{current_trans}.xml")
        else:
            print(f"Failed to fetch data for {current_trans} from the URL.")
