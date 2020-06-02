import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

for page in range(1, 11):
	print("Страница №{}. Ссылки:".format(page))
	url = "http://tululu.org/l55/{}".format(page)
	response = requests.get(url)
	response.raise_for_status()
	soup = BeautifulSoup(response.text, "lxml")
	all_books = soup.find_all("div", class_="bookimage")

	for book in all_books:
		book = book.find("a")["href"]
		book = urljoin(url, book)
		print(book)

