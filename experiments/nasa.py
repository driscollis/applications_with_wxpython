# https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf

import urllib  # urllib.parse.urlencode(f)
import requests

base_url = 'https://images-api.nasa.gov/search'
search_term = 'apollo 11'
desc = 'moon landing'
media = 'image'
query = {'q': search_term, 'description': desc, 'media_type': media}
full_url = base_url + '?' + urllib.urlencode(query)

r = requests.get(full_url)
data = r.json()
data['collection']['items'][0]
asset_url = 'https://images-api.nasa.gov/asset/' + nasa_id