import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime

def login_and_get_reading_data(userId: str, password: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }
    login_url = "https://syosetu.org/"    
    session = requests.Session()
    login_data = {
        "id": userId,
        "pass": password,
        "autologin": "1",
        "submit": "ログイン",
        "mode": "login_entry_end",
        "redirect_mode": ""
    }
    response = session.post(login_url,headers=headers, data=login_data)
    sleep(3)
    if response.status_code != 200:
        raise Exception("Login failed")

    reading_data = []
    for year in range(2024, datetime.datetime.now().year+1):
        for month in range(2, datetime.datetime.now().month+1):
            history_url = f"https://syosetu.org/?mode=view_reading_history&type=&date={year}-{month}"
            response = session.get(history_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find('table', class_="table1")
            info = table.find_all("td")
            book_count = info[0].get_text().replace("\n","").replace(" ","").replace("\t","").replace(",","").replace("-","0")
            chapter_count = info[1].get_text().replace("\n","").replace(" ","").replace("\t","").replace(",","").replace("-","0")
            word_count = info[2].get_text().replace("\n","").replace(" ","").replace("\t","").replace(",","").replace("-","0")
            daily_table = soup.find_all('table', class_='table1')[3].find_all('tr')[1:-1]
            daily_data = dict()
            for i in daily_table:
                daily_data[int(i.find_all('td')[0].text[-2:])] = [
                    {'daily_book_count': int(i.find_all('td')[1].text.replace("-","0").replace(",",""))},
                    {'daily_chapter_count': int(i.find_all('td')[2].text.replace("-","0").replace(",",""))},
                    {'daily_word_coount': int(i.find_all('td')[3].text.replace("-","0").replace(",",""))}
                ]
            reading_data.append({
                "year": year,
                "month": month,
                "book_count": f'{int(book_count):,}',
                "chapter_count": f'{int(chapter_count):,}',
                "word_count": f'{int(word_count):,}',
                "daily_data": daily_data
            })
            sleep(3)
    return reading_data