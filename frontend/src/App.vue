<template>
  <div id="app" class="app-layout">
    <HeaderSection
      :selectedLine="selectedLine"
      :selectedStation="selectedStation"
      :lineList="lineList"
      lineColor="#2c3e50"
      :secondsSinceUpdate="secondsSinceUpdate"
      @update:line="selectedLine = $event"
      @update:station="selectedStation = $event"
      @search="initIntervals(true)"
    />

    <main class="main-container">
      <TrackMapSection
        :stations="lineStations"
        :trains="trainPositions"
        :lineColor="selectedColor"
      />

      <div class="info-side">
        <ArrivalSection :arrivals="arrivalStatus" />
        <CongestionSection
          :timelineData="congestionTimeline"
          :lineColor="selectedColor"
        />
      </div>
    </main>
  </div>
</template>

<script>
import "./assets/reset.css";
import HeaderSection from "./layout/HeaderSction.vue";
import TrackMapSection from "./layout/TrackMapSection.vue";
import ArrivalSection from "./layout/ArrivalSection.vue";
import CongestionSection from "./layout/CongestionSection.vue";
import axios from "axios";

export default {
  components: {
    HeaderSection,
    TrackMapSection,
    CongestionSection,
    ArrivalSection,
  },
  data() {
    return {
      selectedLine: "4호선",
      selectedStation: "서울역",
      selectedColor: "#2c3e50",
      lineList: [],
      lineStations: [],
      trainPositions: [],
      arrivalStatus: [],
      congestionTimeline: [],
      secondsSinceUpdate: 0, // 마지막 호출 후 경과 시간
      fetchInterval: null, // 15초 기준 polling
      timerInterval: null, // 데이터 불러온 뒤 지난 시간 체크
    };
  },
  async created() {
    try {
      this.lineList = await this.getLineInfo();
      await this.updateMainThemeColor();
    } catch (error) {
      console.error(error);
    }
  },
  async mounted() {
    try {
      await this.initIntervals(false);
    } catch (error) {
      console.error(error);
    }
  },
  beforeUnmount() {
    this.clearAllIntervals();
  },
  methods: {
    async initIntervals(isUserSearch) {
      // 실행 중인 인터벌 제거
      await this.clearAllIntervals();

      // 데이터 초기 호출
      await this.fetchData(isUserSearch);

      // 15초 데이터 폴링 시작
      this.fetchInterval = setInterval(() => {
        this.fetchData(isUserSearch);
      }, 15000);

      // 1초 타이머 시작
      this.timerInterval = setInterval(() => {
        this.secondsSinceUpdate++;
      }, 1000);
    },

    // 인터벌 제거
    clearAllIntervals() {
      if (this.fetchInterval) {
        clearInterval(this.fetchInterval);
        this.fetchInterval = null;
      }
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },

    /*
     * 서울시 지하철 노선 종류 및 색상 헥사코드 호출
     * */
    async getLineInfo() {
      try {
        const res = await axios.get("http://localhost:3000/subway/lines");

        return res.data;
      } catch (error) {
        console.error(error);
      }
    },

    /*
     * 메인 색상 변경하기
     * */
    updateMainThemeColor() {
      if (!this.lineList || this.lineList.length === 0) return;

      const targetLine = this.lineList.find(
        (line) => line.subway_nm === this.selectedLine
      );

      if (targetLine) {
        this.selectedColor = targetLine.line_color;
      }
    },

    /*
     * 검색일 기준으로 평일/토요일/일요일 여부 확인
     * */
    getDayType() {
      try {
        const now = new Date();
        const day = now.getDay(); // 1-5 평일 6 토요일 0 일요일

        switch (day) {
          case 0:
            return "일요일";
          case 6:
            return "토요일";
          default:
            return "평일";
        }
      } catch (error) {
        console.error(error);
      }
    },

    /*
     * 노선 실시간 열차 상황/ 역 실시간 도착 정보 호출
     * */
    async getRealtimeData(lineName, stationName) {
      try {
        console.log(lineName, stationName);
        const realtimeRes = await axios.get(
          `http://localhost:3000/subway/realtime`,
          {
            params: {
              subway_nm: lineName,
              statn_nm: stationName,
            },
          }
        );
        return realtimeRes.data;
      } catch (error) {
        console.error(error);
      }
    },

    /*
     * 검색 역 혼잡도 정보 호출
     * */
    async getCongestionData(stationName, dayType) {
      try {
        let res = await axios.get(`http://localhost:3000/subway/congestion`, {
          params: {
            subway_nm: this.selectedLine,
            statn_nm: stationName,
            day_type: dayType,
          },
        });

        return res.data;
      } catch (error) {
        console.error(error);
      }
    },

    /*
     * 검색
     */
    async fetchData(isUserSearch = false) {
      try {
        // 검색이 맞을 시 메인 색상 변경
        if (isUserSearch) {
          this.updateMainThemeColor();
        }

        this.secondsSinceUpdate = 0;
        const dayType = this.getDayType();
        const stName = this.selectedStation.replace("역", "");

        // === 운행중인 지하철 데이터 가져오기
        let rtData = await this.getRealtimeData(this.selectedLine, stName);

        this.lineStations =
          rtData.lineStations?.stationList || rtData.lineStations || [];
        this.trainPositions = rtData.realtimeTrainPosition?.trains || [];
        this.arrivalStatus = rtData.realtimeArrivalStatus || [];

        // === 선택 역 혼잡도 가져오기
        let congRes = await this.getCongestionData(stName, dayType);

        this.congestionTimeline = congRes?.congestions || [];
      } catch (err) {
        console.error("❌ 메인 데이터 로드 실패:", err);
      }
    },
    getTrainsAtStation(name) {
      return this.trainPositions.filter((t) => t.currentStatnNm === name);
    },
  },
};
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.main-container {
  display: grid;
  grid-template-columns: 500px 1fr;
  flex: 1;
  overflow: hidden;
  background: #f5f6f7;
  padding: 15px;
  gap: 15px;
}
.info-side {
  display: grid;
  grid-template-rows: 1fr 1.5fr;
  gap: 15px;
  overflow: hidden;
}
</style>
