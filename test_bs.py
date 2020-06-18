for page in range(1, 5):
    url_for_title = "http://tululu.org/l55/{}".format(page)
    response_for_title = requests.get(url_for_title)
    response_for_title.raise_for_status()
    if response_for_title:
        soup = BeautifulSoup(response_for_title.text, 'lxml')
        images = soup.find_all("div", class_="bookimage")
        for image in images:
            image_url = image.find("a").find("img")["src"]
            image_url = urljoin(url_for_title, image_url)
            print(image_url)