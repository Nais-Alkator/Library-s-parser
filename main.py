import requests
import os

directory = "books"
os.makedirs(directory, exist_ok=True)

for book in range(1, 11):
    url = "http://tululu.org/txt.php?id={}".format(book)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status() 
    filename = "{0}/{1}.txt".format(directory, book)
    if response.content:
        with open(filename, 'wb') as file:
            file.write(response.content)