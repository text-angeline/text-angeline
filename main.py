import json
import requests

with open('config.json', 'r') as f:
    config = json.load(f)

api-key = config['key']

books = {"genesis", "exodus", "leviticus"}

url = f"https://api.scripture.api.bible/v1/bibles/{bibleId}/verses/{verseId}/"

### example request for Matthew 1:23 (MAT.1.23)
### https://api.scripture.api.bible/v1/bibles/9879dbb7cfe39e4d-04/verses/MAT.1.23?content-type=json&include-notes=false&include-titles=true&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false&use-org-id=false

query = input("Query: ")
formatted_query = query.lower()
if (formatted_query in books):
    print("Book found!")
else:
    print("Not found!")
