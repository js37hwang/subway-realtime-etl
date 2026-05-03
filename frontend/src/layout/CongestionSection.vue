<template>
  <section class="congestion-section card">
    <div class="table-container">
      <table class="congestion-table">
        <thead>
          <tr>
            <th class="col-side" :style="{ backgroundColor: lineColor }">
              {{ directionNames.up }}
            </th>
            <th class="col-time" :style="{ backgroundColor: lineColor }">
              시간표
            </th>
            <th class="col-side" :style="{ backgroundColor: lineColor }">
              {{ directionNames.down }}
            </th>
          </tr>
        </thead>
        <tbody class="scrollable-body">
          <tr v-for="row in mergedTimeline" :key="row.time">
            <!-- 좌측: 상행/내선 혼잡도 -->
            <td class="col-side">
              <div
                v-if="row.up"
                class="status-cell"
                :style="{ color: row.up.color }"
              >
                {{ row.up.status }}
              </div>
            </td>

            <!-- 중앙: 시간 -->
            <td class="col-time time-text">{{ row.time }}</td>

            <!-- 우측: 하행/외선 혼잡도 -->
            <td class="col-side">
              <div
                v-if="row.down"
                class="status-cell"
                :style="{ color: row.down.color }"
              >
                {{ row.down.status }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script>
export default {
  props: ["timelineData", "lineColor"], // 부모(App.vue)로부터 congestions 배열 전체를 받음
  computed: {
    // 상행/하행 이름을 동적으로 결정
    directionNames() {
      const up = this.timelineData[0]?.direction || "상행";
      const down = this.timelineData[1]?.direction || "하행";
      return { up, down };
    },
    // 시간대별로 상/하행 데이터를 매칭하여 하나의 리스트로 변환
    mergedTimeline() {
      if (!this.timelineData || this.timelineData.length < 1) return [];

      const upData = this.timelineData[0]?.timeline || [];
      const downData = this.timelineData[1]?.timeline || [];

      // 시간(05:30 등)을 키로 사용하는 맵 생성
      const map = {};

      upData.forEach((item) => {
        if (!map[item.time]) map[item.time] = { time: item.time };
        map[item.time].up = item;
      });

      downData.forEach((item) => {
        if (!map[item.time]) map[item.time] = { time: item.time };
        map[item.time].down = item;
      });

      // 시간순 정렬하여 배열로 반환
      return Object.values(map).sort((a, b) => a.time.localeCompare(b.time));
    },
  },
};
</script>

<style scoped>
.congestion-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: white; /* 기본 배경 흰색 */
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.congestion-table {
  width: 100%;
  border-collapse: collapse; /* 경계선 일치를 위해 collapse 권장 */
}

/* 1. 헤더 섹션: 노선 색상으로 통일 */
.congestion-table thead th {
  color: white;
  padding: 15px 10px;
  position: sticky;
  top: 0;
  z-index: 10;
  font-size: 14px;
  border: none; /* 헤더 사이의 경계선 제거 */
}

/* 2. 컬럼별 너비 및 배경색 설정 */
.col-side {
  width: 40%;
  text-align: center;
  background-color: #ffffff; /* 상/하행 배경 흰색 */
}

.col-time {
  width: 20%;
  text-align: center;
  font-weight: bold;
  background-color: #f7f8f9; /* 시간표 배경만 아주 옅은 회색 */
}

.congestion-table td {
  padding: 12px 5px;
  border-bottom: 1px solid #f0f0f0; /* 행 간 구분선 */
  vertical-align: middle;
}

.time-text {
  color: #333;
  font-size: 13px;
}

.status-cell {
  font-weight: 800;
  font-size: 14px;
}

/* 스크롤바 디자인 (세련되게) */
.table-container::-webkit-scrollbar {
  width: 6px;
}
.table-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}
</style>
