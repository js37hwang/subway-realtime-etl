<template>
  <section class="track-map-container scrollable">
    <div class="map-wrapper">
      <!-- 1. 상행(내선) 라인: 정방향 (예: 서울역 -> 부산방향) -->
      <div class="rail-track">
        <div class="line-bar" :style="{ backgroundColor: lineColor }"></div>
        <div
          v-for="station in stations"
          :key="'up-' + station.statnId"
          class="station-node"
        >
          <div class="station-center">
            <div class="station-circle" :style="{ borderColor: lineColor }">
              <span class="arrow">↓</span>
            </div>
            <span class="station-name">{{ station.statnNm }}</span>
          </div>

          <transition-group name="train-move">
            <div
              v-for="train in filterTrains(station.statnNm, '상행')"
              :key="train.trainNo"
              class="train-rect up-train"
              :style="{ backgroundColor: lineColor }"
            >
              <span class="train-label">{{ train.trainNo }}</span>
            </div>
          </transition-group>
        </div>
      </div>

      <!-- 2. 하행(외선) 라인: 역방향 (예: 부산방향 -> 서울역) -->
      <div class="rail-track">
        <div class="line-bar" :style="{ backgroundColor: lineColor }"></div>
        <!-- computed에서 뒤집은 reversedStations 사용 -->
        <div
          v-for="station in reversedStations"
          :key="'down-' + station.statnId"
          class="station-node"
        >
          <div class="station-center">
            <div class="station-circle" :style="{ borderColor: lineColor }">
              <span class="arrow">↑</span>
            </div>
            <span class="station-name">{{ station.statnNm }}</span>
          </div>

          <transition-group name="train-move">
            <div
              v-for="train in filterTrains(station.statnNm, '하행')"
              :key="train.trainNo"
              class="train-rect down-train"
              :style="{ backgroundColor: lineColor }"
            >
              <span class="train-label">{{ train.trainNo }}</span>
            </div>
          </transition-group>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: ["stations", "trains", "lineColor"],
  computed: {
    // 하행 노선을 위해 역 리스트를 반대로 뒤집음
    reversedStations() {
      // 원본 데이터 훼손 방지를 위해 스프레드 연산자([...]) 사용 후 뒤집기
      return [...this.stations].reverse();
    },
  },
  methods: {
    filterTrains(statnNm, direction) {
      if (!this.trains) return [];
      return this.trains.filter(
        (t) => t.currentStatnNm === statnNm && t.updnLine.includes(direction)
      );
    },
  },
};
</script>

<style scoped>
.track-map-container {
  height: 100%;
  padding: 60px 0;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.map-wrapper {
  display: flex;
  justify-content: space-evenly;
  min-height: 1200px;
}

.rail-track {
  position: relative;
  width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.line-bar {
  position: absolute;
  width: 10px;
  height: 100%;
  top: 0;
  z-index: 1;
}

.station-node {
  height: 140px; /* 역 간 간격 최적화 */
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* 역 중앙 정렬 박스 */
.station-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.station-circle {
  width: 38px;
  height: 38px;
  background: white;
  border-width: 4px;
  border-style: solid;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.arrow {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 역 이름 스타일: 노선 바로 아래 배치 */
.station-name {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 800;
  color: #222;
  white-space: nowrap;
  text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff,
    1px 1px 0 #fff; /* 글자 가독성 보호 */
}

/* 열차 디자인 최적화 (밀착형) */
.train-rect {
  position: absolute;
  width: 32px;
  height: 55px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 5;
}

.train-label {
  color: white;
  font-size: 11px;
  font-weight: bold;
  writing-mode: vertical-lr;
}

/* 노선에 아주 가깝게 위치 조정 */
.up-train {
  left: 20px; /* 중앙 선에서 왼쪽으로 밀착 */
}

.down-train {
  right: 20px; /* 중앙 선에서 오른쪽으로 밀착 */
}

/* 실시간 이동 모션 */
.train-move-enter-active,
.train-move-leave-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.train-move-enter {
  opacity: 0;
  transform: translateY(40px);
}
.train-move-leave-to {
  opacity: 0;
  transform: translateY(-40px);
}

.scrollable {
  overflow-y: auto;
}
</style>
