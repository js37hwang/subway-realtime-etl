## 혼잡도 통계 api 호출 로직
"""
[서울시 지하철 혼잡도 통계 정보 API 컬럼 명세]

1. 기본 정보
- DOW_SE        : 요일 구분 (평일, 토요일, 일요일)
- LINE          : 호선 (예: 1호선)
- STTN_NO       : 역 번호 (고유 번호)
- DPTRE_STTN    : 출발역 이름 (기준 역)
- UP_DOWN_SE    : 상하구분 (상선, 하선)

2. 시간대별 혼잡도 (30분 단위)
- 혼잡도 수치 : 0 ~ 100 이상의 실수 (비율 %)
- TIME0530 ~ TIME0930 : 출근 시간대 혼잡도
- TIME1000 ~ TIME1630 : 낮 시간대 혼잡도
- TIME1700 ~ TIME1930 : 퇴근 시간대 혼잡도
- TIME2000 ~ TIME0030 : 야간 시간대 혼잡도

- 여유 (Low)    : 0% ~ 34%   (좌석 여유, 통로 비어있음)
- 보통 (Normal) : 35% ~ 79%  (좌석 만석, 입석 여유)
- 주의 (Caution): 80% ~ 124% (어깨 부딪힘 발생)
- 혼잡 (Heavy)  : 125% ~ 149% (열차 내 이동 어려움)
- 매우 혼잡      : 150% 이상   (열차 탑승 곤란)
"""

import requests
import os
import datetime
import pandas as pd

from dotenv import load_dotenv

load_dotenv(dotenv_path="../../dataset/config/.env")

def getCongestionStatus(value):
    """
    혼잡도 수치를 기준으로 등급, 텍스트, 색상을 반환
    """
    val = float(value)
    if val <= 34:
        return {"status": "여유", "level": "low", "color": "#2ECC71"}
    elif val <= 79:
        return {"status": "보통", "level": "normal", "color": "#3498DB"}
    elif val <= 124:
        return {"status": "주의", "level": "caution", "color": "#F1C40F"}
    elif val <= 149:
        return {"status": "혼잡", "level": "heavy", "color": "#E67E22"}
    else:
        return {"status": "매우 혼잡", "level": "very_heavy", "color": "#E74C3C"}
    
async def transformCongestionData(apiItem):
    """
    API의 시간대별 컬럼들을 리스트 형태의 응답 데이터로 변환
    """
    processedList = []
    
    # 시간대 컬럼 리스트 (05:30 ~ 00:30)
    # 실제 API 컬럼명 규칙에 맞게 리스트를 생성합니다.
    timeSlots = [
        "0530", "0600", "0630", "0700", "0730", "0800", "0830", "0900", "0930",
        "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400",
        "1430", "1500", "1530", "1600", "1630", "1700", "1730", "1800", "1830",
        "1900", "1930", "2000", "2030", "2100", "2130", "2200", "2230", "2300",
        "2330", "0000", "0030"
    ]

    for slot in timeSlots:
        columnName = f"TIME{slot}"
        rawValue = apiItem.get(columnName, 0)
        
        # 가공된 상태 정보 가져오기
        statusInfo = await getCongestionStatus(rawValue)
        
        processedList.append({
            "time": f"{slot[:2]}:{slot[2:]}", # "0830" -> "08:30"
            "rawVal": rawValue,
            **statusInfo # status, level, color 포함
        })

    return processedList


async def getStationCongestion(subway_nm, statn_nm):
    try:
        service_key = os.getenv("DATA_API_KEY")

        params ={
            "KEY" : service_key, # 인증키
            "TYPE" : "json", # 파일 타입
            "SERVICE":"subwConfusion", 
            "START_INDEX" : 0, # 시작행
            "END_INDEX" : 100, # 종료행
        }

        url = f"http://openapi.seoul.go.kr:8088/{params['KEY']}/{params['TYPE']}/{params['SERVICE']}/{params['START_INDEX']}/{params['END_INDEX']}"

        response = requests.get(url, params=params)
        items = response.json()


        if items.get("errorMessage", {}).get("code") != "INFO-000":
            print(items["errorMessage"]["code"])
            return {}
        
        

    except Exception:
        print("Error!");