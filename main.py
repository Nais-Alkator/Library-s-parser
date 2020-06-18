import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


books_folder = os.makedirs("books", exist_ok=True)
images_folder = os.makedirs("images", exist_ok=True)


def get_links_for_books(): 
    links_for_books = [] 
    for page in range(1, 2):
        url = "http://tululu.org/l55/{}".format(page)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        all_books = soup.select(".bookimage")
        for book in all_books:
            book = book.select_one("a")["href"]
            book = urljoin(url, book)
            links_for_books.append(book)
    return links_for_books


def download_books(links_for_books, folder="books"):
    json_data = []
    for link in links_for_books:
        response = requests.get(link, allow_redirects=False)
        response.raise_for_status() 
        if response.content:
            soup = BeautifulSoup(response.text, 'lxml')
            title = soup.select_one("h1")
            title = title.text.split("::")
            header = title[0].strip()
            header = "{}. ".format(header)
            header = sanitize_filename(header)
            author = title[1].strip()
            id_book = link.split(".org/b")
            id_book = id_book[1]
            image = soup.select_one(".bookimage a img")["src"]
            image = urljoin(link, image)
            filename = os.path.join(folder, header)

            #Добавляем жанр книги
            print(header)
            genres = soup.select_one("span .d_book")
            genres = genres.text
            print(genres)

            #Добавляем комментарии
            comments = soup.select("div .texts")
            comments_info = []
            for comment in comments:
                comment = comment.select_one("span")
                comments_info.append(comment.text)


            link_for_download_book = "http://tululu.org/txt.php?id={}".format(id_book)
            response_for_download = requests.get(link_for_download_book)
            
            #Скачивание книг
            with open(filename, 'wb') as file:
                file.write(response_for_download.content)

            info = {"title": header, "author": author, "img_src": image, "book_path": filename, 
            "comments": comments_info, "genres": genres}
            json_data.append(info)

        with open('info.json', 'w', encoding="utf8") as file:
            json.dump(json_data, file, ensure_ascii=False)
            

def download_image(links_for_books, images_folder="images"):
    number = 1
    for link in links_for_books:
        response_for_title = requests.get(link)
        response_for_title.raise_for_status()
        if response_for_title:
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            images = soup.select("div .bookimage")
            for image in images:
                image_url = image.select_one("a img")["src"]
                image_url = urljoin(link, image_url)
                image_name = image_url.split("tululu.org/")
                response_image = requests.get(image_url)
                filename = os.path.join(images_folder, "{0}{1}".format(number, image_url[-4:]))
                number += 1
                with open(filename, 'wb') as file:
                    file.write(response_image.content)

if __name__ == "__main__":   
    links_for_books = get_links_for_books()          
    #download_books(links_for_books)
    download_image(links_for_books)