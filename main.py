import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


os.makedirs("books", exist_ok=True)

def download_books(folder="books"):
    for book in range(1, 11):
        url_for_download = "http://tululu.org/txt.php?id={}".format(book)
        response_for_download = requests.get(url_for_download, allow_redirects=False)
        response_for_download.raise_for_status() 
        url_for_title = "http://tululu.org/b{}".format(book)
        response_for_title = requests.get(url_for_title)
        response_for_title.raise_for_status()
        soup = BeautifulSoup(response_for_title.text, 'lxml')
        title = soup.find("h1")
        title = title.text.split("::")
        header = title[0].strip()
        header = "{}. ".format(book) + header
        header = sanitize_filename(header)
        filename = os.path.join(folder, header)

        if response_for_download.content:
            with open(filename, 'wb') as file:
                file.write(response_for_download.content)
download_books()