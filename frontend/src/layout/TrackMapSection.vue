<template>
  <section class="track-map-container scrollable">
    <div class="map-wrapper">
      <!-- [우측] 상행 -->
      <div ref="upTrack" class="rail-track">
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
        </div>

        <!-- 열차 -->
        <div
          v-for="(train, idx) in upTrains"
          :key="idx + train.trainNo + '-up'"
          class="train-rect up-train"
          :style="{
            backgroundColor: lineColor,
            top: getTrainTop(train, stations) + 'px',
          }"
        >
          <span class="train-label">{{ train.trainNo }}</span>
        </div>
      </div>

      <!-- [좌측] 하행 -->
      <div class="rail-track">
        <div class="line-bar" :style="{ backgroundColor: lineColor }"></div>
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
        </div>

        <!-- 열차 -->
        <div
          v-for="(train, idx) in downTrains"
          :key="train.trainNo + '-down' + idx"
          class="train-rect down-train"
          :style="{
            backgroundColor: lineColor,
            top: getTrainTop(train, reversedStations) + 'px',
          }"
        >
          <span class="train-label">{{ train.trainNo }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: ["stations", "trains", "lineColor"],
  computed: {
    reversedStations() {
      return [...this.stations].reverse();
    },
    upTrains() {
      if (!this.trains) return [];
      return this.trains.filter((t) => t.updnLine.includes("상행"));
    },
    downTrains() {
      if (!this.trains) return [];
      return this.trains.filter((t) => t.updnLine.includes("하행"));
    },
  },
  methods: {
    getTrainTop(train, stationList) {
      const STATION_HEIGHT = 140;
      const idx = stationList.findIndex(
        (s) => s.statnNm === train.currentStatnNm
      );
      if (idx === -1) return 0;

      let baseTop = idx * STATION_HEIGHT;
      let offset = 0;

      // 1. 상태별 기본 오프셋
      switch (train.status) {
        case "진입":
          offset = -30;
          break;
        case "도착":
          offset = 0;
          break;
        case "출발":
        case "전역출발":
          offset = 40;
          break;
      }

      // 2. 가상 이동 (Polling 대기 시간 동안의 흐름)
      const seconds = this.$parent.secondsSinceUpdate || 0;
      const driftAmount = seconds * 1; // 초당 1px 이동

      // 상행/하행 판별 후 방향 결정
      const isUpLine = train.updnLine.includes("상행");

      // 상행(↓): 좌표 증가 방향 (+)
      // 하행(↑): 좌표 감소 방향 (-) -> 그래야 위로 올라감
      const finalDrift = isUpLine ? driftAmount : -driftAmount;

      return baseTop + offset + finalDrift;
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

  /* 1.5초가 아니라 1초 정도로 설정하여 1초마다 업데이트되는 secondsSinceUpdate와 동기화 */
  transition: top 1s linear;
  will-change: top; /* 성능 최적화 */
}

.train-label {
  color: white;
  font-size: 11px;
  font-weight: bold;
  writing-mode: vertical-lr;
}

/* 노선에 아주 가깝게 위치 조정 */
.up-train {
  left: 0;
  border-bottom: 4px solid rgba(0, 0, 0, 0.2);
}

/* 하행 열차: 위쪽으로 살짝 그림자 */
.down-train {
  right: 0;
  border-top: 4px solid rgba(0, 0, 0, 0.2);
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
