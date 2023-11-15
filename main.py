import random
from datetime import datetime
import streamlit as st
import pandas as pd
import requests

# CSV에 있는 x,y 좌표 값을 불러옴
# 데이터에서 NaN은 fillna('')을 통해 공백으로 치환
geo_coordinate = pd.read_csv("geo_coordi.csv", encoding='CP949').fillna('')  

category_mapping = {
    "T1H" : "기온(℃)",
    "RN1" : "1시간 강수량(범주(1 mm))",
    "SKY" : "하늘상태(코드값)",
    "UUU" : "동서람성분(m/s)",
    "VVV" : "남북바람성분(m/s)",
    "REH" : "습도(%)",
    "PTY" : "강수형태(코드값)",
    "LGT" : "낙뢰(코드값)",
    "VEC" : "풍향(deg)",
    "WSD" : "풍속(m/s)"
}

# API 요청 URL
url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'

# API 요청 변수 설정
service_key = 'UYknNB/v9UKs5VdAS6Ts/Xh0XTlPySYCPE/C4GmcK0Sd7X+AXSyIgFP7eAl84PEiECf73MOiEbvAFiiYXe5lRA=='
page_no = '1'
num_of_rows = '10'
data_type = 'JSON'
base_date = '20231115'
base_time = '0600'
nx = '60'
ny = '126'


# st.subheader("우리 지역의 날씨는?")

# API 요청 함수
def make_api_request(x,y):
    time_column = []
    temperture = []

    for i in range(24):
        if i<10:
            i="0"+str(i)
        params = {
        'serviceKey': service_key,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        'dataType': data_type,
        'base_date' : base_date,
        'base_time' : str(i)+"00",
        'nx': x,
        'ny': y
        }
        try:
            # API 요청 보내기
            response = requests.get(url, params=params)
            # XML 데이터 파싱
            data = response.json()

            # 데이터가 존재하지 않으면(code:03) 패스
            if data['response']['header']['resultCode'] == "03":
                break
            # 기온 정보(T1H)만 수집
            for j in data['response']['body']['items']['item']:
                if j['category'] == "T1H":
                    print(j['baseTime'][0:2]," : ",j['obsrValue'])
                    time_column.append(int(j['baseTime'][0:2]))
                    temperture.append(float(j['obsrValue']))
        except Exception as e:
            print("API 요청 중 오류발생:", e)
    # 데이터를 반환
    return {
        '온도' : temperture,
        '시간' : time_column
        }


# API 요청 버튼 추가

# 1단계 선택
step1 = st.selectbox('시', options=geo_coordinate['시'].unique())

# 2단계 선택
filtered_data_step2 = geo_coordinate[geo_coordinate['시'] == step1]
step2 = st.selectbox('군/구', options=filtered_data_step2['군/구'].unique())

# 3단계 선택
filtered_data_step3 = filtered_data_step2[filtered_data_step2['군/구'] == step2]
step3 = st.selectbox('동/리', options=filtered_data_step3['동/리'].unique())

# 사용자 선택에 따른 데이터 필터링
selected_data = filtered_data_step3[filtered_data_step3['동/리'] == step3]

st.write(selected_data)

# 선택된 데이터 표시
st.write('선택된 지역:', step1, step2, step3)
if st.button('조회'):
    with st.spinner('기상청 API 조회 중...'):
        data = pd.DataFrame(make_api_request(selected_data['X'],selected_data['Y']))
        st.write("오늘의 온도 추이")       
        st.line_chart(
            data,
            x='시간',
            y='온도',
            height=250,
            color=["#FF0000"]
            )
        

# add_selectbox = st.sidebar.selectbox(
#     'How would you like to be contacted?',
#     ('Email', 'Home phone', 'Mobile phone')
# )
