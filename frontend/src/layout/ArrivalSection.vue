<template>
  <section class="arrival-section card">
    <div class="arrival-header">
      <h3 class="station-title">역 실시간 현황</h3>
    </div>

    <div class="timeline-container">
      <!-- 1. 좌우를 잇는 노선도색 굵은 선 -->
      <div
        class="main-horizontal-line"
        :style="{ backgroundColor: lineColor }"
      ></div>

      <!-- 2. 다가오는 열차 (왼쪽) -->
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

      <!-- 3. 중앙 역 지점 (화살표 포함) -->
      <div class="timeline-center">
        <div class="center-node" :style="{ borderColor: lineColor }">
          <!-- 진행 방향 화살표 (오른쪽으로 흐르는 느낌) -->
          <span class="flow-arrow" :style="{ color: lineColor }">➔</span>
        </div>
        <span class="node-label">{{ selectedStation }}</span>
      </div>

      <!-- 4. 방금 떠난 열차 (오른쪽) -->
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
        <div v-else class="no-data-text">최근 출발 정보 없음</div>
      </div>
    </div>

    <!-- 하단 미니 리스트 -->
    <div class="arrival-list-mini">
      <div
        v-for="(arr, index) in arrivals?.upcoming?.slice(1, 4)"
        :key="index"
        class="mini-item"
      >
        <span class="mini-dir">{{ arr.trainLineNm }}</span>
        <span class="mini-time">{{ arr.arrivalText }}</span>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: ["arrivals", "selectedStation", "lineColor"],
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
  min-height: 300px;
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
  height: 8px; /* 굵직한 노선 느낌 */
  top: 50%;
  transform: translateY(-50%);
  z-index: 1; /* 뱃지보다 뒤에 위치 */
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
  font-size: 16px;
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
}

.mini-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.mini-dir {
  font-size: 12px;
  color: #999;
}
.mini-time {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}
</style>
