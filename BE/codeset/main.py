# main.py
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 서비스 레이어 임포트
from service.line_info_service import getStationLineInfo
from service.arrival_service import getRealtimeArrival
from service.position_service import getRealtimePosition
from service.congestion_service import getStationCongestion
from service.database import initCongestionTableFromCsv, getSubwayMasterList

# 환경 변수 로드
load_dotenv(dotenv_path="../dataset/config/.env")

# 서버 시작 시 실행- vue created 같은 부분
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 ETL 서버 시작 및 초기 데이터 적재 중...")
    csv_file_path = "../dataset/서울교통공사_지하철혼잡도정보_20251130.csv"
    
    if os.path.exists(csv_file_path):
        # CSV 데이터 DB 적재
        initCongestionTableFromCsv(csv_file_path)
        print("✅ 지하철 혼잡도 CSV 데이터 적재 완료")
    else:
        print("⚠️ 주의: 적재할 CSV 파일이 지정된 경로에 없습니다.")

    yield


app = FastAPI(lifespan=lifespan, title="Subway ETL Backend Server")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", 
        "http://localhost:5500",
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/subway/realtime")
async def getSubwayInfo(subway_nm: str, statn_nm: str):
    """
    특정 호선의 실시간 위치와 도착 정보를 결합하여 반환
    """
    try:
        stations = await getStationLineInfo(subway_nm)
        positions = await getRealtimePosition(subway_nm)
        arrivals = await getRealtimeArrival(statn_nm)
        
        return {
            "subwayName": subway_nm,
            "stationName": statn_nm,
            "realtimeTrainPosition": positions, # 선택 역 운행 열차 정보
            "realtimeArrivalStatus": arrivals, # 선택 역에 도착할 열차 데이터
            "lineStations": stations, # 선택 노선에 존재하는 열차들 데이터
        }
    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subway/congestion")
async def getCongestion(subway_nm, statn_nm, day_type):
    """
    노선/역명/요일별 혼잡도 통계 반환
    day_type: 평일/ 토요일/ 일요일
    """
    res =  getStationCongestion(subway_nm, statn_nm, day_type)

    return res

@app.get("/subway/lines")
async def getLineColor():
    """
    서울 지하철 노선 리스트+ 노선별 색상 헥사코드
    """

    res = await getSubwayMasterList();
    
    return res

# 메인 실행부
if __name__ == "__main__":
    port = int(os.getenv("MAIN_PORT", 3000))
    print(f"📡 API 서버를 http://localhost:{port}에서 시작합니다.")
    # reload=True: 코드 수정 시 서버 자동 재시작
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)