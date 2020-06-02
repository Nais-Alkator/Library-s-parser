import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


url = "http://tululu.org/l55"
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
first_book = soup.find("div", class_="bookimage").find("a")["href"]
first_book = urljoin(url, first_book)
print(first_book)
