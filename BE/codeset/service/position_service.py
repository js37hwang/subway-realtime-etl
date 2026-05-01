## 실시간 지하철 위치 정보 api 호출 로직
"""
[서울시 실시간 지하철 위치 정보 API 컬럼 명세]

1. 기본 정보
- subwayId      : 지하철호선ID (1001:1호선, 1002:2호선, 1063:경의중앙 등)
- subwayNm      : 지하철호선명
- statnId       : 지하철역ID (현재 열차가 위치한 역 ID)
- statnNm       : 지하철역명 (현재 열차가 위치한 역 이름)

2. 열차 및 운행 정보
- trainNo       : 열차번호 (운행 중인 열차 고유 번호)
- updnLine      : 상하행선구분 (0:상행/내선, 1:하행/외선)
- statnTid      : 종착지하철역ID
- statnTnm      : 종착지하철역명 (열차의 목적지)
- trainSttus    : 열차상태구분 (0:진입, 1:도착, 2:출발, 3:전역출발)
- directAt      : 급행여부 (1:급행, 0:아님, 7:특급)
- lstcarAt      : 막차여부 (1:막차, 0:아님)

3. 수신 시간
- lastRecptnDt  : 최종수신날짜 (YYYYMMDD)
- recptnDt      : 최종수신시간 (YYYY-MM-DD HH:MM:SS)
- totalCount    : 전체 결과 수
"""

import requests
import os
import pandas as pd

from dotenv import load_dotenv
from .line_info_service import getStationLineInfo

load_dotenv(dotenv_path="../../dataset/config/.env")

async def getRealtimePosition(subway_nm):
    try:
        service_key = os.getenv("DATA_API_KEY")

        params ={
            "KEY" : service_key, # 인증키
            "TYPE" : "json", # 파일 타입
            "SERVICE":"realtimePosition", 
            "START_INDEX" : 0, # 시작행
            "END_INDEX" : 100, # 종료행
            "subwayNm" : subway_nm # 호선명- '역' 없이!
        }

        url = f"http://swopenAPI.seoul.go.kr/api/subway/{params['KEY']}/{params['TYPE']}/{params['SERVICE']}/{params['START_INDEX']}/{params['END_INDEX']}/{params['subwayNm']}"
    
        response = await requests.get(url, params=params)
        items = response.json()

        if items.get("errorMessage", {}).get("code") != "INFO-000":
            print(items["errorMessage"]["code"])
            return {}
        
        stationOrderList = await getStationLineInfo(subway_nm)
        rawList = items.get("realtimePositionList", [])

        resList = []
        
        for item in rawList:
            currentStatnId = item.get("statnId")
            updnLine = item.get("updnLine") # 0:상행, 1:하행
            trainSttus = item.get("trainSttus") # 0:진입, 1:도착, 2:출발
            
            # 2. 현재 역의 순서(Order) 찾기
            currentOrder = next((s['order'] for s in stationOrderList if s['statnId'] == currentStatnId), None)
            
            if currentOrder is None: continue

            # 3. 다음 역(Next Station) 추정 로직
            # 상행(0)이면 Order 감소, 하행(1)이면 Order 증가 (데이터 구조에 따라 다름)
            nextOrder = currentOrder - 1 if updnLine == "0" else currentOrder + 1
            nextStatn = next((s for s in stationOrderList if s['order'] == nextOrder), None)
            nextStatnNm = nextStatn['statnNm'] if nextStatn else "종점"

            # 4. 구간 텍스트 생성 (예: 서울역 -> 시청역 사이)
            sectionNm = ""
            if trainSttus in ["0", "1"]: # 진입 또는 도착
                sectionNm = f"{item.get('statnNm')} 대기 중"
            else: # 출발 또는 전역출발
                sectionNm = f"{item.get('statnNm')} ➔ {nextStatnNm} 이동 중"

            resList.append({
                "trainNo": item.get("trainNo"),
                "updnLine": "상행/내선" if updnLine == "0" else "하행/외선",
                "currentStatnNm": item.get("statnNm"), # 
                "nextStatnNm": nextStatnNm, # 이 둘 사이의 좌표를 계산해줌
                "sectionNm": sectionNm,
                "status": ["진입", "도착", "출발", "전역출발"][int(trainSttus)],
                "isExpress": item.get("directAt") != "0"
            })

        return {
            "subwayNm": subway_nm,
            "totalCount": len(resList), # 현재 운행 중인 열차 수
            "trains": resList
        }
    except Exception:
        print("Error!")



