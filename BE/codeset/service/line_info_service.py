# 선택 노선 존재하는 역 정보 api 호출
"""
[지하철 역 정보 API 파라미터 명세]

- STATION_CD      : 전철역코드
- STATION_NM      : 전철역명
- STATION_NM_ENG  : 전철역명(영문)
- LINE_NUM        : 호선
- FR_CODE         : 외부코드
- STATION_NM_CHN  : 전철역명(중문)
- STATION_NM_JPN  : 전철역명(일문)
"""

import requests
import os
import traceback

from dotenv import load_dotenv

load_dotenv(dotenv_path="../../dataset/config/.env")


def sortStationList(stationList):
    if not stationList:
        return []
    
    sortedList = sorted(stationList, key=lambda x: x.get("FR_CODE", ""))

    # 3. 정렬된 순서대로 order 부여(1부터 시작) 
    for idx, station in enumerate(sortedList):
        station['order'] = idx + 1

    return sortedList


async def getStationLineInfo(subway_nm):
    """
        원하는 노선 내 존재하는 모든 역을 순서대로 출력
    """
    try:
        service_key = os.getenv("DATA_API_KEY")

        param ={
            "KEY" : service_key, # 인증키
            "TYPE" : "json", # 파일 타입
            "SERVICE":"SearchSTNBySubwayLineInfo", 
            "START_INDEX" : 0, # 시작행
            "END_INDEX" : 500, # 종료행
            "STATION_NM" : '', 
            "LINE_NUM" : subway_nm # 노선도명
        }

        response = requests.get(f"http://openapi.seoul.go.kr:8088/{param['KEY']}/{param['TYPE']}/{param['SERVICE']}/{param['START_INDEX']}/{param['END_INDEX']}///{param['LINE_NUM']}", 
                                        params=param)
        items = response.json()

        if items.get("SearchSTNBySubwayLineInfo", {}).get("RESULT").get("CODE") != "INFO-000":
            return {}
        
        rawList = items.get("SearchSTNBySubwayLineInfo", {}).get("row")

        stationList = []

        for item in rawList:
            stationList.append({
                "statnId" : item.get("STATION_CD"),
                "statnNm" : item.get("STATION_NM") ,
                "FR_CODE" : item.get("FR_CODE") ,
            })

        resList = sortStationList(stationList)
            
        return {
                "totalCnt" : items.get("SearchSTNBySubwayLineInfo", {}).get("list_total_count"),
                "stationList": resList
            }

    except Exception as e:
        print("!!! lineStations Error 상세 보고 !!!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
        print("\n--- Traceback ---")
        traceback.print_exc() 
        
        return {"errorMessage": "INTERNAL_SERVER_ERROR", "detail": str(e)}

