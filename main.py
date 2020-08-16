import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import argparse
import sys


def check_link(url):
    try:
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        if response.status_code == 301:
            print("ОШИБКА. Редирект")
            sys.exit()
    except requests.exceptions.HTTPError as error:
        print("ОШИБКА HTTP ERROR: ", error)
        sys.exit()
    except requests.exceptions.ConnectionError as error:
        print("ОШИБКА СОЕДИНЕНИЯ: ", error)
        sys.exit()
    return response


def get_links_for_books(start_page, end_page): 
    links_for_books = [] 
    for page in range(start_page, end_page):
        url = "http://tululuf.org/l55/{}".format(page)
        response = check_link(url)
        soup = BeautifulSoup(response.text, "lxml")
        all_books = soup.select(".bookimage")
        for book in all_books:
            book = book.select_one("a")["href"]
            book = urljoin(url, book)
            links_for_books.append(book)
    return links_for_books


def download_books(links_for_books, json_path, books_folder="books"):
    json_data = []
    for link in links_for_books:
        response = check_link(link)
        if response.content:
            soup = BeautifulSoup(response.text, 'lxml')
            title = soup.select_one("h1")
            title = title.text.split("::")
            header = title[0].strip()
            header = sanitize_filename(header)
            author = title[1].strip()
            id_book = link.split(".org/b")
            id_book = id_book[1]
            image = soup.select_one(".bookimage a img")["src"]
            image = urljoin(link, image)
            filename = os.path.join(books_folder, header)

            #Добавляем жанр книги
            genres = soup.find("span", class_="d_book")
            genres = genres.text

            #Добавляем комментарии
            comments = soup.select("div .texts")
            comments_info = []
            for comment in comments:
                comment = comment.select_one("span")
                comments_info.append(comment.text)

            payload = {"txt.php": "", "id": id_book}
            link_for_download_book = "http://tululu.org"
            response_for_download = requests.get(link_for_download_book, params=payload, allow_redirects=False)
            
            #Скачивание книг
            with open(filename, 'wb') as file:
                file.write(response_for_download.content)


def get_json(links_for_books, json_path, books_folder="books"):
    json_data = []
    for link in links_for_books:
        response = check_link(link)
        if response.content:
            soup = BeautifulSoup(response.text, 'lxml')
            title = soup.select_one("h1")
            title = title.text.split("::")
            header = title[0].strip()
            header = sanitize_filename(header)
            author = title[1].strip()
            id_book = link.split(".org/b")
            id_book = id_book[1]
            image = soup.select_one(".bookimage a img")["src"]
            image = urljoin(link, image)
            filename = os.path.join(books_folder, header)

            #Добавляем жанр книги
            genres = soup.find("span", class_="d_book")
            genres = genres.text

            #Добавляем комментарии
            comments = soup.select("div .texts")
            comments_info = []
            for comment in comments:
                comment = comment.select_one("span")
                comments_info.append(comment.text)


            info = {"title": header, "author": author, "img_src": image, "book_path": filename, 
            "comments": comments_info, "genres": genres}
            json_data.append(info)

        with open(json_path, 'w', encoding="utf8") as file:
            json.dump(json_data, file, ensure_ascii=False)


def download_images(links_for_books, images_folder="images"):
    number = 1
    for link in links_for_books:
        response_for_title = check_link(link)
        if response_for_title:
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            images = soup.select("div .bookimage")
            for image in images:
                image_url = image.select_one("a img")["src"]
                image_url = urljoin(link, image_url)
                image_name = image_url.split("tululu.org/")
                response_image = check_link(image_url)
                filename = os.path.join(images_folder, "{0}{1}".format(number, image_url[-4:]))
                number += 1
                with open(filename, 'wb') as file:
                    file.write(response_image.content)


def get_parser():
    parser = argparse.ArgumentParser(description="Скрипт скачивает книги и обложки к ним с сайта tululu.org")
    parser.add_argument("--start_page", help="Начальная страница для скачивания", type=int, default=1)
    parser.add_argument("--end_page", help="Конечная страница для скачивания", type=int, default=5)
    parser.add_argument("--dest_folder", help="Путь к катологу с результатами парсинга", type=str, default="data")
    parser.add_argument("--skip_imgs", help="Не скачивать картинки", action="store_true")
    parser.add_argument("--skip_txt", help="Не скачивать книги", action ="store_true")
    parser.add_argument("--json_path", help="Путь к файлу json", type=str, default="json")
    return parser


if __name__ == "__main__":   
    args = get_parser().parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_folder = args.json_path
    books = os.path.join(dest_folder, "books")
    images = os.path.join(dest_folder, "images")
    json_path = os.path.join(json_folder, "info.json")
    os.makedirs(books, exist_ok=True)
    os.makedirs(images, exist_ok=True)
    os.makedirs(json_folder, exist_ok=True)
    links_for_books = get_links_for_books(start_page, end_page) 
    if skip_txt and skip_imgs:
        get_json(links_for_books, json_path, books_folder=books)
        print("Ничего не скачивается. Создан json файл.")
    elif skip_imgs:         
        download_books(links_for_books, json_path, books_folder=books)
        get_json(links_for_books, json_path, books_folder=books)
        print("Скачивание книг завершено. Создан json файл.")
    elif skip_txt:
        download_images(links_for_books, images_folder=images)
        get_json(links_for_books, json_path, books_folder=books)
        print("Скачивание обложек завершено. Создан json файл.")
    else:
        download_books(links_for_books, json_path, books_folder=books)
        download_images(links_for_books, images_folder=images)
        get_json(links_for_books, json_path, books_folder=books)
        print("Скачивание книг и обложек завершено. Создан json файл.")