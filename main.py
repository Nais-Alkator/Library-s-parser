import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import argparse
import sys


def check_for_redirection(response):
    try:
        response.raise_for_status()
        if response.status_code != 200: 
            raise requests.HTTPError
    except (requests.HTTPError, requests.ConnectionError) as error:
        print(f'{error}')


def get_books_urls(start_page, end_page):
    books_urls = []
    for page in range(start_page, end_page):
        url = "http://tululu.org/l55/{}".format(page)
        response = requests.get(url, verify=False)
        check_for_redirection(response)
        books_info = BeautifulSoup(response.text, "lxml").select(".bookimage")
        for book in books_info:
            book_link = book.select_one("a")["href"]
            book_url = urljoin(url, book_link)
            books_urls.append(book_url)
    return books_urls


def parse_book_page(book_url):
    book_page = requests.get(book_url, verify=False)
    check_for_redirection(book_page)
    if book_page.content:
        soup = BeautifulSoup(book_page.text, 'lxml')
        title = soup.select_one("h1")
        title = title.text.split("::")
        header = title[0].strip()
        header = sanitize_filename(header)
        author = title[1].strip()
        book_id = book_url.split(".org/b")[1]
        image_url = soup.select_one(".bookimage a img")["src"]
        image_url = urljoin(book_url, image_url)
        book_path = os.path.join(books_folder, header)
        genres = soup.find("span", class_="d_book").text
        comments = soup.select("div .texts")
        comments_info = []
        for comment in comments:
            comment = comment.select_one("span")
            comments_info.append(comment.text)
        parsed_book_page = {"title": header, "author": author, "image_url": image_url, "book_path": book_path, 
        "comments": comments_info, "genres": genres, "book_id": book_id}
    return parsed_book_page


def fetch_parsed_books_pages(books_urls):
    parsed_books_pages = []
    for book_url in books_urls:
        parsed_book_page = parse_book_page(book_url)
        parsed_books_pages.append(parsed_book_page)
    return parsed_books_pages


def create_json_file(parsed_books_pages, json_path):
    with open(json_path, 'w', encoding="utf8") as file:
        json.dump(parsed_books_pages, file, ensure_ascii=False)


def download_book_file(book_id, book_path):
    url = "http://tululu.org"
    payload = {"txt.php": "", "id": book_id}
    book_file = requests.get(url, params=payload, verify=False)
    check_for_redirection(book_file)
    with open(book_path, 'wb') as file:
        file.write(book_file.content)


def download_image(image_url, images_folder, title):
    image_file = requests.get(image_url, allow_redirects=True, verify=False)
    image_file.raise_for_status()
    image_name = image_url.split("tululu.org/")
    images_tags = BeautifulSoup(image_file.text, 'lxml').select("div .bookimage")
    filename = os.path.join(images_folder, "{0}{1}".format(title, image_url[-4:]))
    with open(filename, 'wb') as file:
        file.write(image_file.content)


def get_parser():
    parser = argparse.ArgumentParser(description="Скрипт скачивает книги и обложки к ним с сайта tululu.org")
    parser.add_argument("--start_page", help="Начальная страница для скачивания", type=int, default=1)
    parser.add_argument("--end_page", help="Конечная страница для скачивания", type=int, default=5)
    parser.add_argument("--dest_folder", help="Путь к катологу с результатами парсинга", type=str, default="data")
    parser.add_argument("--skip_imgs", help="Не скачивать картинки", action="store_true")
    parser.add_argument("--skip_txt", help="Не скачивать книги", action="store_true")
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
    books_folder = os.path.join(dest_folder, "books")
    images_folder = os.path.join(dest_folder, "images")
    json_path = os.path.join(json_folder, "info.json")
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(json_folder, exist_ok=True)
    books_urls = get_books_urls(start_page, end_page)
    parsed_books_pages = fetch_parsed_books_pages(books_urls)
    if skip_txt and skip_imgs:
        create_json_file(parsed_books_pages, json_path)
        print("Ничего не скачивается. Создан json файл c информацией о книгах.")
    elif skip_imgs:
        for parsed_book_page in parsed_books_pages:
            title = parsed_book_page["title"]
            book_path = parsed_book_page["book_path"]
            download_book_file(title, book_path)
        create_json_file(parsed_books_pages, json_path)
        print("Скачивание книг завершено. Создан json файл с информацией о книгах.")
    elif skip_txt:
        for parsed_book_page in parsed_books_pages:
            image_url = parsed_book_page["image_url"]
            title = parsed_book_page["title"].split('/')[0]
            download_image(image_url, images_folder, title)
        create_json_file(parsed_books_pages, json_path)
        print("Скачивание обложек завершено. Создан json файл с информацией о книгах.")
    else:
        for parsed_book_page in parsed_books_pages:
            image_url = parsed_book_page["image_url"]
            title = parsed_book_page["title"].split('/')[0]
            book_path = parsed_book_page["book_path"]
            download_book_file(title, book_path)
            download_image(image_url, images_folder, title)
        create_json_file(parsed_books_pages, json_path)
        print("Скачивание книг и обложек завершено. Создан json файл с информацией о книгах.")