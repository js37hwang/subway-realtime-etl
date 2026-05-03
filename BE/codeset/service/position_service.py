## 실시간 지하철 위치 정보 api 호출 로직
"""
[서울시 실시간 지하철 위치 정보 API 파라미터 명세]

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
import traceback

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
    
        response = requests.get(url, params=params)
        items = response.json()

        if items.get("errorMessage", {}).get("code") != "INFO-000":
            return {"trains": []}
        
        print("items : ", items)
        
        # 1. 노선도 정보 가져오기- subway_master
        stationResponse = await getStationLineInfo(subway_nm)
        
        # 딕셔너리- 내부의 리스트 추출
        stationOrderList = stationResponse.get("stationList", [])

        rawList = items.get("realtimePositionList", [])
        resList = []
        
        for item in rawList:
            currentStatnNm = item.get("statnNm")
            updnLine = item.get("updnLine") 
            trainSttus = item.get("trainSttus") 
            
            # 1. 현재 역의 정보 찾기
            currentStation = next((s for s in stationOrderList if s['statnNm'] == currentStatnNm), None)
            
            # currentStation이 없거나 'order' 키가 없는 경우 스킵
            if currentStation is None or currentStation.get('order') is None:
                continue
            
            currentOrder = currentStation['order']

            # 2. 다음 역(Next Station) 추정 로직
            # 상행(0)이면 감소, 하행(1)이면 증가
            try:
                nextOrder = currentOrder - 1 if int(updnLine) == 0 else currentOrder + 1
                nextStation = next((s for s in stationOrderList if s.get('order') == nextOrder), None)
                nextStatnNm = nextStation['statnNm'] if nextStation else "종점"
            except (TypeError, ValueError):
                nextStatnNm = "정보 없음"

            # 3. 상태 텍스트 가공
            status_list = ["진입", "도착", "출발", "전역출발"]

            curr_status = status_list[int(trainSttus)] if int(trainSttus) < len(status_list) else "운행중"

            # 4. 구간 정보 생성
            if curr_status in ["진입", "도착"]:
                sectionNm = f"{currentStatnNm} 대기 중"
            else:
                sectionNm = f"{currentStatnNm} ➔ {nextStatnNm} 이동 중"

            resList.append({
                "trainNo": item.get("trainNo"),
                "updnLine": "상행/상선/내선" if int(updnLine) == 0 else "하행/하선/외선",
                "currentStatnNm": currentStatnNm,
                "nextStatnNm": nextStatnNm,
                "sectionNm": sectionNm,
                "status": curr_status,
                "isExpress": int(item.get("directAt")) == 1
            })

        print("positions : ", resList)

        return {
            "subwayNm": subway_nm,
            "totalCount": len(resList),
            "trains": resList
        }

    except Exception as e:
        print("!!! positions Error 상세 보고 !!!")
        traceback.print_exc() 
        return {"errorMessage": "INTERNAL_SERVER_ERROR", "detail": str(e)}