import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.request import urlopen

# 1. 데이터 불러오기

# csv 파일 불러오기
df = pd.read_excel('/content/drive/MyDrive/info_tracking/children/Children_tracking_list.xlsx')

# 2. 데이터 전처리하기
## 01. 데이터 타입 변경
# ['company no']컬럼의 데이터를 문자열로 변환
# 데이터 type 확인하기
df.rename(columns = {'사업자번호':'company no'}, inplace=True)

# 'company no' 컬럼에 null 값이 포함되는지 살펴보기
df['company no'].isnull().sum()

# 'company no' 컬럼에는 null 값이 존재하기 때문에 int타입으로 변경 시 오류 발생
if df['company no'] is not None :
  df['company no'] = df['company no'].astype(str)
else :
  pass

# 'company no'의 공백 제거
df['company no'] = df['company no'].str.strip()

# 'company no'의 소수점 제거
df['company no'] = df['company no'].str.replace('\.0', '')

# 이외의 모든 float 타입을 str로 변경하기
# df[['담당자이름', '연락처1', '연락처2', '이메일', '비고 ']] = df[['담당자이름', '연락처1', '연락처2', '이메일', '비고 ']].astype(str)


## 02. URL 변경
# ['Homepage URL'] 컬럼에서 'https://brand.' 로 시작하는 url을 'https://smartstore.' 로 시작하도록 수정

# url 수정
df['Homepage URL'] = df['Homepage URL'].str.replace('https://brand.', 'https://smartstore.', regex=False)
df['info_url'] = df['info_url'].str.replace('https://brand.', 'https://smartstore.', regex=False)


## 03. 판매자정보 url 컬럼 만들기
df['url_info'] = df['Homepage URL'] + '/profile?cp=2'
df = df[['company name', 'Store name', 'Homepage URL', 'url_info', 'company no', '담당자명', '연락처1', '연락처2', '이메일', '비고']]

# 3. 필요 데이터 수집하기
# response 값 확인
test_url = 'https://smartstore.naver.com/opuwomall/profile?cp=2'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
response = requests.get(test_url, headers=headers)
print(response)

## 01. 필요한 부분 잘라서 데이터 수집하기
test_df = df.copy()

# 접속 가능한 row까지 데이터 수집하기
success_count = 0

for idx, row in test_df.iterrows():
    url = row['url_info']
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            success_count += 1
            print(idx, response)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 판매중인 상품이 없는지 확인
            no_prod_tag = soup.find('div', {'class':'_2UoI-0yGAC'})

            if no_prod_tag and '판매중인 상품이 없습니다.' in no_prod_tag.text:
                test_df.loc[idx, '이메일'] = '운영중지'

            else:
                # 필요한 데이터 수집 부분
                contents_zone = soup.find('div', {'class': '_3i59rveNvJ'})

                # 'dd' 태그를 가진 모든 요소 찾기
                all_elements = contents_zone.find_all('span', {'class': '_1hBeKq0WZK'})

                # DataFrame을 생성하고 각 컬럼에 값 할당
                test_df.loc[idx, 'company_name_updated'] = all_elements[0].text

                # 기존에 찾은 상호명과 다를 경우 표시 남기기
                if test_df.loc[idx, 'company name'] == test_df.loc[idx, 'company_name_updated']:
                    pass
                else:
                    test_df.loc[idx, '비고'] = all_elements[0].text

                    test_df.loc[idx, '담당자명'] = all_elements[1].text
                    time.sleep(0.5)
        else:
            print(f"Request failed with status code {response.status_code}. Stopping the loop.")
            break

    except Exception as e:
        test_df.loc[idx, '이메일'] = '운영중지'
        time.sleep(0.5)

print(f"Successfully processed {success_count} rows.")
result = test_df.head(success_count)

# 5. xlsx 파일로 저장하기

# csv 파일로 저장
# 일간트렌드 데이터마다 파일명 다르게 저장
from datetime import datetime
import pytz

# 현재 시간을 가져옵니다.
current_time = datetime.now()

# UTC 시간대로 변경합니다.
utc_time = current_time.replace(tzinfo=pytz.utc)

# 한국 시간대로 변경합니다.
korea_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))

today_date = korea_time.strftime('%y%m%d %H:%M')

# xlsx 파일로 바로 저장
result.to_excel(f'/content/drive/My Drive/info_tracking/children/scrapping_name/{today_date}.xlsx', index=False)