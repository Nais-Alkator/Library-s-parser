import requests
from bs4 import BeautifulSoup


url = "http://tululu.org/b1/"
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
title = soup.find("h1")
title = title.text.split("::")
header = title[0].strip()
author = title[1].strip()
print("Заголовок:", header)
print("Автор:", author)
