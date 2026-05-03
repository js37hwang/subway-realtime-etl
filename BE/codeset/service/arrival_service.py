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
import traceback

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

        response = requests.get(f"http://swopenAPI.seoul.go.kr/api/subway/{params['KEY']}/{params['TYPE']}/{params['SERVICE']}/{params['START_INDEX']}/{params['END_INDEX']}/{params['statnNm']}", 
                                        params=params)
        response.raise_for_status()
        items = response.json() 

        
        if items.get("errorMessage", {}).get("code") != "INFO-000":
            return {"recentlyLeft": [], "upcoming": []}

        serverTime = datetime.now()
        recentlyLeft = []  # 떠난지 1분 미만 열차
        upcoming = []      # 도착 예정 열차

        for d in items["realtimeArrivalList"]:
            # 1. 공통 데이터 가공
            arrivalSec = int(d.get("barvlDt", 0))
            arvlCd = d.get("arvlCd")
            
            # 도착 메세지 가공
            if arrivalSec > 0:
                minutes = arrivalSec // 60
                seconds = arrivalSec % 60
                arrivalText = f"{minutes}분 {seconds}초 후" if minutes > 0 else f"{seconds}초 후"
            else:
                arrivalText = d.get("arvlMsg2")

            data = {
                "subwayId": d.get("subwayId"),
                "updnLine": d.get("updnLine"),
                "trainLineNm": d.get("trainLineNm"),
                "btrainNo": d.get("btrainNo"),
                "arvlMsg2": d.get("arvlMsg2"),
                "arrivalText": arrivalText,
                "arrivalTime": arrivalSec,
                "isLastTrain": d.get("lstcarAt") == "1",
                "ordkey": d.get("ordkey")
            }

            # 2. 떠난 열차 판단 (arvlCd 2: 출발)
            if arvlCd == "2":
                try:
                    recptnTime = datetime.strptime(d.get("recptnDt"), '%Y-%m-%d %H:%M:%S')
                    diff = (serverTime - recptnTime).total_seconds()
                    if diff < 60:  # 60초 이내 출발
                        data["leftSeconds"] = int(diff)
                        recentlyLeft.append(data)
                except:
                    pass
            
            # 3. 도착 예정 열차 판단 (출발 코드가 아닌 모든 열차)
            else:
                upcoming.append(data)

        # 4. 정렬 및 필터링
        # 예정 열차는 ordkey 순으로 정렬 후 상위 5개만 추출
        upcoming_sorted = sorted(upcoming, key=lambda x: x['ordkey'])[:5]
        
        # 떠난 열차는 방금 떠난 순서(diff가 작은 순)로 정렬
        recently_left_sorted = sorted(recentlyLeft, key=lambda x: x.get('leftSeconds', 999))

        return {
            "recentlyLeft": recently_left_sorted,
            "upcoming": upcoming_sorted
        }

    except Exception as e:
        print("!!! arrivals Error 상세 보고 !!!")
        # 1. 에러의 종류와 기본 메시지 출력
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
        # 2. 에러가 발생한 정확한 위치(파일, 라인 등) 출력
        print("\n--- Traceback ---")
        traceback.print_exc() 
        
        return {"errorMessage": "INTERNAL_SERVER_ERROR", "detail": str(e)}
