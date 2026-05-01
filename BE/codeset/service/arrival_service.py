## 실시간 도착 정보 api 호출 로직
"""
[서울시 실시간 지하철 도착 정보 API 파라미터 명세]

1. 기본 정보
- subwayId     : 지하철호선ID (1001:1호선, 1002:2호선, 1063:경의중앙, 1065:공항철도 등)
- updnLine     : 상하행선구분 (상행/내선, 하행/외선)
- trainLineNm  : 도착지방면 (성수행 - 구로디지털단지방면)
- statnId      : 지하철역ID (현재 조회 중인 역 ID)
- statnNm      : 지하철역명 (현재 조회 중인 역 이름)

2. 열차 상태 및 위치
- btrainNo     : 열차번호 (현재 운행 중인 열차 고유 번호)
- btrainSttus  : 열차종류 (일반, 급행, ITX, 특급)
- arvlCd       : 도착코드 (0:진입, 1:도착, 2:출발, 3:전역출발, 4:전역진입, 5:전역도착, 99:운행중)
- arvlMsg2     : 첫번째도착메세지 (서울 도착, 전역 진입, 출발 등)
- arvlMsg3     : 두번째도착메세지 (현재 위치 역 이름 등)
- barvlDt      : 열차도착예정시간 (단위: 초 / 0은 도착 상태)
- recptnDt     : 정보 생성 시각 (데이터 업데이트 시간)

3. 경로 및 환승
- bstatnId     : 종착지하철역ID
- bstatnNm     : 종착지하철역명
- statnFid     : 이전지하철역ID
- statnTid     : 다음지하철역ID
- trnsitCo     : 환승노선수
- subwayList   : 연계호선ID (환승 가능한 노선 ID 리스트)
- statnList    : 연계지하철역ID (환승 가능한 역 ID 리스트)
- ordkey       : 도착예정열차순번 (정렬용 조합 키)
- lstcarAt     : 막차여부 (1:막차, 0:아님)
"""

import requests
import os
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../dataset/config/.env")

# 특정 역 실시간 도착정보 가져오기
async def getRealtimeArrival(statnNm) :
    try:
        service_key = os.getenv("DATA_API_KEY")

        params ={
            "KEY" : service_key, # 인증키
            "TYPE" : "json", # 파일 타입
            "SERVICE":"realtimeStationArrival", 
            "START_INDEX" : 0, # 시작행
            "END_INDEX" : 100, # 종료행
            "statnNm" : statnNm # 역명- '역' 없이!
        }

        response = await requests.get(f"http://swopenAPI.seoul.go.kr/api/subway/{params['KEY']}/{params['TYPE']}/{params['SERVICE']}/{params['START_INDEX']}/{params['END_INDEX']}/{params['statnNm']}", 
                                        params=params)
        items = response.json() 

        
        # if items["errorMessage"]["code"] != "INFO-000":
        if items.get("errorMessage", {}).get("code") != "INFO-000":
            print(items.get("errorMessage", {}).get("code"))
            return {"errorMessage" : items.get("errorMessage", {}).get("code")};

        # 역에서 출발 1분 미만- 화면에 그리기 위해
        serverTime = datetime.now()

        resList = []

        for d in items["realtimeArrivalList"]:
            # 1. 도착 예정 시간 정제 (초 -> 분/초 문자열)
            arrivalSec = int(d.get("barvlDt", 0))
            arrivalText = ""
            if arrivalSec > 0:
                minutes = arrivalSec // 60
                seconds = arrivalSec % 60
                arrivalText = f"{minutes}분 {seconds}초 후" if minutes > 0 else f"{seconds}초 후"
            else:
                arrivalText = d.get("arvlMsg2") # "진입", "도착" 등 메세지 그대로 사용

            # 2. 금방 떠난 열차 판단 로직 (1분 미만)
            # arvlCd 2: 출발, 3: 전역출발인 경우 체크
            isRecentlyLeft = False
            if d.get("arvlCd") in ["2", "3"]:
                # 데이터 생성 시각(recptnDt)과 현재 시간 비교
                try:
                    recptnTime = datetime.strptime(d.get("recptnDt"), '%Y-%m-%d %H:%M:%S')
                    diff = (serverTime - recptnTime).total_seconds()
                    if diff < 60:  # 60초 이내에 출발 정보가 생성된 경우
                        isRecentlyLeft = True
                except:
                    pass

            # 3. append res data
            data = {
                "subwayId": d.get("subwayId"),
                "updnLine": d.get("updnLine"),         # 상행/하행
                "trainLineNm": d.get("trainLineNm"),   # 방면
                "btrainNo": d.get("btrainNo"),         # 열차번호
                "arvlMsg2": d.get("arvlMsg2"),         # 전역 진입 등 메세지
                "arrivalText": arrivalText,               # 가공된 시간 메세지
                "arrivalTime": arrivalSec,                # 숫자 데이터 (정렬용)
                "isRecentlyLeft": isRecentlyLeft,         # 금방 떠난 열차 여부
                "isLastTrain": d.get("lstcarAt") == "1", # 막차 여부
                "ordkey": d.get("ordkey")              # 정렬 키
            }
            resList.append(data)

        print(key=lambda x: x['ordkey'])

        # 도착 순서대로 정렬
        return sorted(resList, key=lambda x: x['ordkey'])

    except Exception:
        print("Error!")
