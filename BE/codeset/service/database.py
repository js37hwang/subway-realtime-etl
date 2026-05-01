import pymysql
import os
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv

# 스크린샷 2026-05-01 12:08:37.png 구조에 맞춘 env 경로 로드
load_dotenv(dotenv_path=".env")

def getDbConnection():
    """ MySQL 연결 설정 """
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        db=os.getenv("DB_NAME", "subway_db"), 
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def initCongestionTableFromCsv(csvPath):
    """
    CSV 파일명(예: subway_congestion_20260501.csv)에서 날짜를 추출하여
    DB에 해당 날짜 데이터가 없는 경우에만 적재합니다.
    """
    # 1. 파일명에서 날짜 추출 (파일명 형식: *_YYYYMMDD.csv 가정)
    fileName = os.path.basename(csvPath)
    try:
        fileDateStr = fileName.split('_')[-1].split('.')[0] # "20260501"
    except Exception:
        print("❌ 파일명 형식이 올바르지 않습니다. (예: data_20260501.csv)")
        return

    connection = getDbConnection()

    try:
        with connection.cursor() as cursor:
            # 2. 테이블 존재 여부 확인 및 생성
            createTableSql = """
            CREATE TABLE IF NOT EXISTS subway_congestion (
                row_id INT AUTO_INCREMENT PRIMARY KEY,
                day_type VARCHAR(10),
                line_nm VARCHAR(20),
                station_cd INT,
                station_nm VARCHAR(50),
                direction VARCHAR(10),
                t0530 FLOAT, t0600 FLOAT, t0630 FLOAT, t0700 FLOAT, t0730 FLOAT,
                t0800 FLOAT, t0830 FLOAT, t0900 FLOAT, t0930 FLOAT, t1000 FLOAT,
                t1030 FLOAT, t1100 FLOAT, t1130 FLOAT, t1200 FLOAT, t1230 FLOAT,
                t1300 FLOAT, t1330 FLOAT, t1400 FLOAT, t1430 FLOAT, t1500 FLOAT,
                t1530 FLOAT, t1600 FLOAT, t1630 FLOAT, t1700 FLOAT, t1730 FLOAT,
                t1800 FLOAT, t1830 FLOAT, t1900 FLOAT, t1930 FLOAT, t2000 FLOAT,
                t2030 FLOAT, t2100 FLOAT, t2130 FLOAT, t2200 FLOAT, t2230 FLOAT,
                t2300 FLOAT, t2330 FLOAT, t0000 FLOAT, t0030 FLOAT,
                data_date VARCHAR(8),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(createTableSql)

            # 3. 데이터 중복 확인 (해당 날짜 데이터가 이미 있는지)
            checkSql = "SELECT COUNT(*) as count FROM subway_congestion WHERE data_date = %s"
            cursor.execute(checkSql, (fileDateStr,))
            if cursor.fetchone()['count'] > 0:
                print(f"⚠️ {fileDateStr} 날짜 데이터가 이미 존재합니다. 스킵합니다.")
                return

            # 4. CSV 데이터 로드 및 전처리
            print(f"🚀 {fileName} 데이터를 DB에 적재하기 시작합니다...")
            df = pd.read_csv(csvPath, encoding='ms949')
            print('shape : ',df.shape)
            
            # CSV 컬럼명과 DB 컬럼명 매칭 (한글 -> 영문)
            # CSV 헤더가 '요일구분,호선...' 순서라고 가정
            df.columns = [
                'day_type', 'line_nm', 'station_cd', 'station_nm', 'direction',
                't0530', 't0600', 't0630', 't0700', 't0730', 't0800', 't0830', 't0900', 't0930',
                't1000', 't1030', 't1100', 't1130', 't1200', 't1230', 't1300', 't1330', 't1400',
                't1430', 't1500', 't1530', 't1600', 't1630', 't1700', 't1730', 't1800', 't1830',
                't1900', 't1930', 't2000', 't2030', 't2100', 't2130', 't2200', 't2230', 't2300',
                't2330', 't0000', 't0030'
            ]
            df['data_date'] = fileDateStr # 파일명에서 가져온 날짜 추가

            # 5. DB에 Bulk Insert
            insertSql = f"""
            INSERT INTO subway_congestion ({", ".join(df.columns)})
            VALUES ({", ".join(["%s"] * len(df.columns))})
            """
            cursor.executemany(insertSql, df.values.tolist())
            
        connection.commit()
        print(f"✅ {fileDateStr} 데이터 적재 완료 (총 {len(df)}행)")
    except Exception as e:
        print(f"❌ DB 적재 오류: {e}")
    finally:
        connection.close()

def initSubwayMaster():
    """ 지하철 노선 마스터 데이터 초기화 저장 """
    # 공식 노선도 색상 기준 데이터
    subwayData = [
        (1001, '1호선', '#0052A4'), (1002, '2호선', '#00A84D'),
        (1003, '3호선', '#EF7C1C'), (1004, '4호선', '#00A4E3'),
        (1005, '5호선', '#996CAC'), (1006, '6호선', '#CD7C2F'),
        (1007, '7호선', '#747F00'), (1008, '8호선', '#E6186C'),
        (1009, '9호선', '#BDB092'), (1063, '경의중앙선', '#77C4A3'),
        (1065, '공항철도', '#0090D2'), (1067, '경춘선', '#0C8E72'),
        (1075, '수인분당선', '#F5A200'), (1077, '신분당선', '#D4003B'),
        (1092, '우이신설선', '#B0AD00'), (1032, 'GTX-A', '#9A6292')
    ]

    connection = getDbConnection()

    try:
        with connection.cursor() as cursor:
            # 2. 테이블 존재 여부 확인 및 생성
            createTableSql = """
            CREATE TABLE IF NOT EXISTS subway_master (
                subway_id INT(10) PRIMARY KEY,
                subway_nm VARCHAR(20),
                line_color VARCHAR(10)
            )
            """
            cursor.execute(createTableSql)


            sql = """
            INSERT INTO subway_master (subway_id, subway_nm, line_color)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE subway_nm=VALUES(subway_nm), line_color=VALUES(line_color)
            """
            cursor.executemany(sql, subwayData)
        connection.commit()
        print("✅ 지하철 마스터 정보 업데이트 완료")
    except Exception as e:
        print(f"❌ DB 저장 오류: {e}")
    finally:
        connection.close()



def getLineColor(subwayId):
    """ 호선 ID로 색상 코드 가져오기 """
    connection = getDbConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT line_color FROM subway_master WHERE subway_id = %s"
            cursor.execute(sql, (subwayId,))
            result = cursor.fetchone()
            return result['line_color'] if result else "#808080"
    finally:
        connection.close()


async def getSubwayMasterList():
    """ 
    지하철 마스터 테이블의 모든 정보(ID, 이름, 색상)를 가져옴
    프론트엔드에서 노선별 테마 색상을 적용할 때 사용
    """
    initSubwayMaster()

    connection = getDbConnection()
    try:
        with connection.cursor() as cursor:
            # 모든 노선의 ID, 이름, 색상을 조회
            sql = "SELECT subway_id, subway_nm, line_color FROM subway_master"
            cursor.execute(sql)
            return cursor.fetchall() # 리스트 형태로 반환 (DictCursor 설정 덕분에 딕셔너리 리스트가 됨)
    except Exception as e:
        print(f"❌ 마스터 데이터 조회 오류: {e}")
        return []
    finally:
        connection.close()


def saveAnalysisResult(fileName, question, answer, usedModel):
    """ 분석 결과를 DB에 저장 (기존 로직 유지) """
    connection = getDbConnection()
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO analysis_logs (file_name, question, answer, used_model)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (fileName, question, answer, usedModel))
        connection.commit()
        print(f"✅ DB 저장 완료: {fileName}")
    except Exception as e:
        print(f"❌ DB 저장 오류: {e}")
    finally:
        connection.close()