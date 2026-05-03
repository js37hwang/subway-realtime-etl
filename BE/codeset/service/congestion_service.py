## 혼잡도 통계 api 호출 로직
"""
[서울시 지하철 혼잡도 통계 정보 API 파라미터 명세]

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

from dotenv import load_dotenv
from .database import getCongestionData

load_dotenv(dotenv_path="../../dataset/config/.env")


def getCongestionStatus(value):
    """
    혼잡도 수치를 기준으로 등급, 텍스트, 색상을 반환
    """
    val = float(value)
    if val <= 34:
        return {"status": "여유", "level": "low", "color": "#3498DB"}
    elif val <= 79:
        return {"status": "보통", "level": "normal", "color": "#2ECC71"}
    elif val <= 124:
        return {"status": "주의", "level": "caution", "color": "#F1C40F"}
    elif val <= 149:
        return {"status": "혼잡", "level": "heavy", "color": "#E67E22"}
    else:
        return {"status": "매우 혼잡", "level": "very_heavy", "color": "#E74C3C"}
    



def getStationCongestion(subway_nm, statn_nm, day_type):
    """
    DB -> 프론트용으로 가공
    """
    dbCongData = getCongestionData(subway_nm, statn_nm, day_type)
    
    if not dbCongData:
        return {"subwayNm": subway_nm, "stationNm": statn_nm, "congestions": []}

    final_res = []

    for row in dbCongData:
        # 1. 컬럼명 매핑: DB- direction=
        direction = row.get("direction") 
        timeline = []

        # 2. t0530부터 t0030까지 30분 단위 컬럼 순회
        for hour in range(0, 25): # 00시부터 24시까지
            for minute in ["00", "30"]:
                # DB 컬럼 규칙: 't' + 'HHMM' (예: t0530, t1800)
                time_key = f"t{str(hour).zfill(2)}{minute}"
                
                # 해당 시간 데이터가 row에 존재하는지 
                congestion_val = row.get(time_key)

                if congestion_val is not None:
                    # 혼잡도 등급 및 색상 정보 가져오기
                    status_info = getCongestionStatus(congestion_val)
                    
                    timeline.append({
                        # "t0830" -> "08:30"
                        "time": f"{time_key[1:3]}:{time_key[3:]}", 
                        "value": float(congestion_val),
                        "status": status_info["status"],
                        "level": status_info["level"],
                        "color": status_info["color"]
                    })

        final_res.append({
            "direction": direction,
            "timeline": timeline
        })

    return {
        "subwayNm": subway_nm,
        "stationNm": statn_nm,
        "dayType": day_type,
        "congestions": final_res
    }