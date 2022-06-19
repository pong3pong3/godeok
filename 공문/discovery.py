"""
평택시 지적공부 고시공고 가운데 키워드 검색으로 확인이 안 된 고시공고를 추출 (예: 궁리2지구)
"""
import requests
from bs4 import BeautifulSoup
import time
candidates = {}
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
for i in range(69160,73217):
    url = 'https://www.pyeongtaek.go.kr/pyeongtaek/saeol/gosiView.do?notAncmtMgtNo='\
          +str(i)+'&mId=0401020000'
    try:
        response = requests.get(url, headers=header)
    except:
        print('도망중')
        time.sleep(3)
        response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content,'lxml')
    if i%1000==0:
        print(i)
    title = soup.find('div',attrs={'class':'bod_view'}).find('h4').text
    if '지적공부' in title:
        candidates[i] = title
    
