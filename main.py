import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin


books_folder = os.makedirs("books", exist_ok=True)
images_folder = os.makedirs("images", exist_ok=True)


def download_books(folder="books"):
    for book in range(1, 11):
        url_for_download = "http://tululu.org/txt.php?id={}".format(book)
        response_for_download = requests.get(url_for_download, allow_redirects=False)
        response_for_download.raise_for_status() 
        url_for_title = "http://tululu.org/b{}".format(book)
        response_for_title = requests.get(url_for_title)
        response_for_title.raise_for_status()
        if response_for_download.content:
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            title = soup.find("h1")
            title = title.text.split("::")
            header = title[0].strip()
            header = "{}. ".format(book) + header
            header = sanitize_filename(header)
            image = soup.find("div", class_="bookimage").find("a").find("img")["src"]
            image = urljoin(url_for_title, image)
            filename = os.path.join(folder, header)

        if response_for_download.content:
            with open(filename, 'wb') as file:
                file.write(response_for_download.content)


def download_image(images_folder="images"):
    for book in range(1, 6):
        url_for_download = "http://tululu.org/txt.php?id={}".format(book)
        response_for_download = requests.get(url_for_download, allow_redirects=False)
        response_for_download.raise_for_status() 
        url_for_title = "http://tululu.org/b{}".format(book)
        response_for_title = requests.get(url_for_title)
        response_for_title.raise_for_status()
        if response_for_title and response_for_download.content:
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            image = soup.find("div", class_="bookimage").find("a").find("img")["src"]
            image = urljoin(url_for_title, image)
            response_image = requests.get(image)
            filename = os.path.join(images_folder, "{0}{1}".format(book, image[-4:]))
            with open(filename, 'wb') as file:
                file.write(response_image.content)

if __name__ == "__main__":             
    download_image()

