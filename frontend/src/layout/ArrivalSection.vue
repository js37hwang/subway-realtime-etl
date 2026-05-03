<template>
  <section class="arrival-section card">
    <div class="arrival-header">
      <h3 class="station-title">역 실시간 현황</h3>
    </div>

    <div class="timeline-container">
      <!-- [배경] 노선 라인  -->
      <div
        class="main-horizontal-line"
        :style="{ backgroundColor: lineColor }"
      ></div>

      <!-- [좌측] 접근중인 열차 -->
      <div class="timeline-wing upcoming">
        <div
          v-if="arrivals.upcoming && arrivals.upcoming.length > 0"
          class="train-badge next"
        >
          <span class="label">곧 도착</span>
          <strong class="time-countdown">{{
            arrivals.upcoming[0].arvlMsg2
          }}</strong>
          <span class="direction">{{ arrivals.upcoming[0].trainLineNm }}</span>
        </div>
        <div v-else class="no-data">운행 예정 열차 없음</div>
      </div>

      <!-- [중앙] 현재 역 -->
      <div class="timeline-center">
        <div class="center-node" :style="{ borderColor: lineColor }">
          <!-- 진행 방향 화살표 (오른쪽으로 흐르는 느낌) -->
          <span class="flow-arrow" :style="{ color: lineColor }">➔</span>
        </div>
        <span class="node-label">{{ selectedStation }}</span>
      </div>

      <!-- [우측] 떠나간 열차 -->
      <div class="timeline-wing left">
        <div
          v-if="arrivals.recentlyLeft && arrivals.recentlyLeft.length > 0"
          class="train-badge departed"
        >
          <span class="label">출발</span>
          <strong class="time-passed"
            >{{ arrivals.recentlyLeft[0].leftSeconds }}초 전</strong
          >
          <span class="direction">{{
            arrivals.recentlyLeft[0].trainLineNm
          }}</span>
        </div>
        <div v-else class="train-badge departed">최근 출발 정보 없음</div>
      </div>
    </div>

    <!-- 하단 미니 리스트 -->
    <div class="arrival-list-mini">
      <div
        v-for="(arr, index) in arrivals?.upcoming?.slice(1, 4)"
        :key="index"
        class="mini-item"
      >
        <div
          class="mini-dot"
          :class="getDotClass(arr.arrivalTime, arr?.arrivalText)"
        ></div>
        <span
          class="mini-time"
          :class="getArrivalStatus(arr.arrivalTime, arr?.arrivalText)"
        >
          {{ formatArrivalTime(arr.arrivalTime, arr?.arrivalText) }}
        </span>
        <span class="mini-dir">{{ formatDirection(arr.trainLineNm) }}</span>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: ["arrivals", "selectedStation", "lineColor"],
  methods: {
    getArrivalStatus(arrivalTime, arrivalText) {
      if (arrivalTime === 0 && arrivalText.includes("번째")) return "far";
      if (arrivalTime === 0) return "urgent";
      if (arrivalTime <= 180) return "soon";
      return "normal";
    },

    formatArrivalTime(arrivalTime, arrivalText) {
      if (arrivalTime === 0) return arrivalText;
      const min = Math.floor(arrivalTime / 60);
      const sec = arrivalTime % 60;
      return sec === 0 ? `${min}분 후` : `${min}분 ${sec}초`;
    },

    // 노선
    formatDirection(trainLineNm) {
      return trainLineNm ? trainLineNm.replace(/\[|\]/g, "") : "";
    },

    // css
    getDotClass(arrivalTime, arrivalText) {
      const status = this.getArrivalStatus(arrivalTime, arrivalText);
      // status가 'far'면 그대로 'far', 그 외엔 'dot-' 접두사 붙임
      return status === "far" ? "far" : `dot-${status}`;
    },
  },
};
</script>

<style scoped>
.arrival-section {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  min-height: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.station-title {
  font-size: 20px;
  font-weight: 900;
  color: #1a2a3a;
  margin-bottom: 40px;
}

.timeline-container {
  display: flex;
  align-items: center;
  position: relative;
  height: 120px;
}

/* 좌우를 잇는 메인 라인 */
.main-horizontal-line {
  position: absolute;
  left: 10%;
  right: 10%;
  height: 8px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  border-radius: 4px;
  opacity: 0.9;
}

.timeline-wing {
  flex: 1;
  display: flex;
  justify-content: center;
  z-index: 5;
}

.timeline-center {
  width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.center-node {
  width: 40px;
  height: 40px;
  background: white;
  border-width: 5px;
  border-style: solid;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 화살표 스타일 */
.flow-arrow {
  font-size: 20px;
  font-weight: bold;
}

.node-label {
  margin-top: 12px;
  font-weight: 800;
  font-size: 22px;
  color: #333;
}

/* 열차 뱃지 스타일 */
.train-badge {
  padding: 15px 20px;
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 140px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid #eee;
}

.train-badge.next {
  border-top: 5px solid #00a5de;
}
.train-badge.departed {
  border-top: 5px solid #ff9800;
}

.label {
  font-size: 11px;
  font-weight: bold;
  color: #888;
  margin-bottom: 6px;
}
.time-countdown {
  font-size: 18px;
  color: #00a5de;
}
.time-passed {
  font-size: 18px;
  color: #ff9800;
}
.direction {
  font-size: 13px;
  color: #444;
  margin-top: 4px;
  font-weight: 600;
}

.arrival-list-mini {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.mini-item {
  flex: 1;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  border: 0.5px solid #eee;
}
.mini-time {
  font-size: 20px;
  font-weight: 600;
}
.mini-dir {
  font-size: 11px;
  color: #999;
  text-align: center;
  line-height: 1.4;
}
.urgent {
  color: #e24b4a;
}
.soon {
  color: #ba7517;
}
.normal {
  color: #185fa5;
}
.mini-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-bottom: 2px;
}
.dot-urgent {
  background: #e24b4a;
}
.dot-soon {
  background: #ba7517;
}
.dot-normal {
  background: #185fa5;
}
</style>
