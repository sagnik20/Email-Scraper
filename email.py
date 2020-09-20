import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
from google.colab import files

url_file_name = input("Enter the file name with websites url: ") 

url_file_name_extension = url_file_name[-3:] 
header = 0 if url_file_name_extension == 'csv' else None
original_url = pd.read_csv(url_file_name, header=header, names=['url'])['url'].tolist()

unscraped = deque(original_url)  
scraped = set()  
emails = set()  

while len(unscraped):
    url = unscraped.popleft()  
    scraped.add(url)
    parts = urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    if '/' in parts.path:
      path = url[:url.rfind('/')+1]
    else:
      path = url
    print("Crawling URL %s" % url)
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        continue
    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
    emails.update(new_emails) 
    soup = BeautifulSoup(response.text, 'lxml')
    for anchor in soup.find_all("a"):
      if "href" in anchor.attrs:
        link = anchor.attrs["href"]
      else:
        link = ''
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            link = path + link
        if not link.endswith(".gz"):
          if not link in unscraped and not link in scraped:
              unscraped.append(link)

df = pd.DataFrame(emails, columns=["Email"])
df.to_csv('email.csv', index=False)

files.download("email.csv")
