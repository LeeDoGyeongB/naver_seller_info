import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import pytz

'''
트래킹이 필요한 데이터를 수집, 전처리, 저장하는 함수를 포함하고 있는 코드
'''

def eda_file(input_db):
    df = input_db
    # 데이터 타입 변경
    # 컬럼명 통일
    df.rename(columns={'사업자번호': 'company no'}, inplace=True)

    # 데이터가 존재할 경우, 데이터 타입 변경
    if df['company no'] is not None:
        df['company no'] = df['company no'].astype(str)
    else:
        pass

    # 공백 및 소수점 제거
    df['company no'] = df['company no'].str.strip()
    df['company no'] = df['company no'].str.replace('\.0', '')

    # info url 컬럼 추가
    df['info_url'] = df['Homepage URL'] + '/profile?cp=2'
    df = df[['Store name', 'Homepage URL', 'info_url', 'company no', '담당자이름', '연락처1', '연락처2', '이메일', '비고 ']]

    # ['Homepage URL'] 컬럼에서 'https://brand.' 로 시작하는 url을 'https://smartstore.' 로 시작하도록 수정
    df['Homepage URL'] = df['Homepage URL'].str.replace('https://brand.', 'https://smartstore.', regex=False)
    df['info_url'] = df['info_url'].str.replace('https://brand.', 'https://smartstore.', regex=False)

    return df


def crawler(df):
    test_df = df.copy()
    success_count = 0
    for idx, row in test_df.iterrows():
        url = row['Homepage URL']
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                success_count += 1
                print(idx, response)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 판매 중인 상품이 없는지 확인
                no_prod_tag = soup.find('div', {'class': '_2UoI-0yGAC'})

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
                        test_df.loc[idx, '비고 '] = all_elements[0].text
                    test_df.loc[idx, '담당자명'] = all_elements[1].text
                    time.sleep(0.5)
                    print(f'{idx}번째 데이터 수집 완료. 상호명 : {all_elements[0].text}')
            else:
                print(f"Request failed with status code {response.status_code}. Stopping the loop.")
                break
        except Exception as e:
            test_df.loc[idx, '이메일'] = '운영중지'
            time.sleep(0.5)

    print(f"Successfully processed {success_count} rows.")
    result = test_df.head(success_count)

    return result


def save_file(df):
    # 현재 시간을 가져옵니다.
    current_time = datetime.now()
    # UTC 시간대로 변경합니다.
    utc_time = current_time.replace(tzinfo=pytz.utc)
    # 한국 시간대로 변경합니다.
    korea_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    today_date = korea_time.strftime("%y%m%d %H:%m")

    # xlsx 파일로 바로 저장
    df.to_excel(f'{today_date}.xlsx', index=False)
    print('Successfully file saved.')

    return df


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = pd.read_csv('tracking_list.csv')
    target_df = eda_file(db)
    result_data = crawler(target_df)
    save_file(result_data)

