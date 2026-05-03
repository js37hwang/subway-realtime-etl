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
            <!-- [좌측] 상행/내선 혼잡도 -->
            <td class="col-side">
              <div
                v-if="row.up"
                class="status-cell"
                :style="{ color: row.up.color }"
              >
                {{ row.up.status }}
              </div>
            </td>

            <!-- [중앙] 시간 -->
            <td class="col-time time-text">{{ row.time }}</td>

            <!-- [우측] 하행/외선 혼잡도 -->
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
  props: ["timelineData", "lineColor"],
  computed: {
    directionNames() {
      const up = this.timelineData[0]?.direction || "상행";
      const down = this.timelineData[1]?.direction || "하행";
      return { up, down };
    },
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
  background-color: white;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.congestion-table {
  width: 100%;
  border-collapse: collapse;
}

/* 헤더 섹션 */
.congestion-table thead th {
  color: white;
  padding: 15px 10px;
  position: sticky;
  top: 0;
  z-index: 10;
  font-size: 14px;
  border: none;
}

.col-side {
  width: 40%;
  text-align: center;
  background-color: #ffffff;
}

.col-time {
  width: 20%;
  text-align: center;
  font-weight: bold;
  background-color: #f7f8f9;
}

.congestion-table td {
  padding: 12px 5px;
  border-bottom: 1px solid #f0f0f0;
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

.table-container::-webkit-scrollbar {
  width: 6px;
}
.table-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}
</style>
