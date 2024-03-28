# 네이버 스마트 스토어 seller 정보 크롤링
> 아웃바운드 셀러 영입을 위해 네이버 스마트 스토어를 운영 중인 셀러의 정보(스토어명, 사업자 번호, 연락처 등)를 수집하기 위한 크롤링 코드를 개발한 프로젝트입니다.


## Getting Started
해당 프로젝트를 clone해서 사용할 수 있습니다
````
git clone naver_seller_info
````
가상환경은 따로 사용하지 않았지만, 가상환경에서 실행하면 더 빠른 결과를 낼 수 있을 것으로 기대됨.
  
## Structure
```
naver_seller_info/
│
├── src/                            # 소스 코드를 포함하는 디렉터리
│   └── main.py                     # 메인 스크립트 파일
│
├── tests/                          # 테스트 코드를 포함하는 디렉터리
│   └── scrapping_seller_info.py
│
├── .gitignore                      # Git에서 추적하지 않을 파일 목록
└── README.md                       # 프로젝트에 대한 개요와 설치, 사용 방법 등을 설명하는 파일

```

## Author
이도경 - dokat@kakao.com
