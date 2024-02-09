import json
import requests

with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['key']

book_dict = {"genesis": "GEN", "exodus": "EXO", "leviticus": "LEV"}

### example request for Matthew 1:23 (MAT.1.23)
### https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/verses/MAT.1.23?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false&use-org-id=false

query = input ("Query (<book_abrv>.<chapter_num>.<verse_num>): ")

url = f"https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/verses/{query}?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false&use-org-id=false"

headers = {'api-key': api_key}
response = requests.request("GET", url, headers=headers)
### print(response.text)
data = response.json()

verse_content = data['data']['content']
verse_text = ''
for item in verse_content:
    if 'items' in item:
        for sub_item in item['items']:
            if 'text' in sub_item:
                verse_text += sub_item['text']
print(verse_text)

# query = input("Query: ")
# formatted_query = query.lower()
# if (formatted_query in books):
#     print("Book found!")
# else:
#     print("Not found!")
