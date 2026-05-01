# 각 노선 별 존재하는 역 정보 api 호출

import requests
import os
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../dataset/config/.env")

async def getStationLineInfo(subway_nm):
    try:
        service_key = os.getenv("DATA_API_KEY")

        param ={
            "KEY" : service_key, # 인증키
            "TYPE" : "json", # 파일 타입
            "SERVICE":"SearchSTNBySubwayLineInfo", 
            "START_INDEX" : 0, # 시작행
            "END_INDEX" : 1000, # 종료행
            "STATION_NM" : '', 
            "LINE_NUM" : subway_nm # 노선도명
        }

        response = await requests.get(f"http://openapi.seoul.go.kr:8088/{param['KEY']}/{param['TYPE']}/{param['SERVICE']}/{param['START_INDEX']}/{param['END_INDEX']}///{param['LINE_NUM']}", 
                                        params=param)
        items = response.json()

        return items
    except Exception:
        print("Error!")

