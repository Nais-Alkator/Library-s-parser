import requests

def check_for_redirection(response):
    try:
        #response.raise_for_status()
        if response.status_code != 200: 
            raise requests.HTTPError
    except (requests.HTTPError, requests.ConnectionError) as error:
        print(f'{error}')

url = "http://tululu.orgffsd/abaadf/"
response = requests.get(url, verify=False)
print(response.content)


