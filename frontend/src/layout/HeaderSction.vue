<template>
  <header
    class="header-section"
    :style="{ borderBottom: `4px solid ${lineColor}` }"
  >
    <div class="search-container">
      <select
        :value="selectedLine"
        class="line-select"
        @change="$emit('update:line', $event.target.value)"
      >
        <option
          v-for="line in lineList"
          :key="line.subway_id"
          :value="line.subway_nm"
        >
          {{ line.subway_nm }}
        </option>
      </select>
      <input
        class="station-input"
        type="text"
        placeholder="역 이름 입력"
        :value="stationName"
        @input="stationName = $event.target.value"
        @keyup.enter="handleSearch"
      />
      <button
        class="search-btn"
        :style="{ backgroundColor: lineColor }"
        @click="handleSearch"
      >
        검색
      </button>
    </div>

    <div class="refresh-timer">
      <span class="timer-text">
        <strong>{{ secondsSinceUpdate }}초 전</strong>
        새로고침됨
      </span>
      <div class="refresh-dot" :style="{ backgroundColor: lineColor }"></div>
    </div>
  </header>
</template>

<script>
export default {
  props: [
    "selectedLine",
    "selectedStation",
    "lineList",
    "lineColor",
    "secondsSinceUpdate",
  ],
  data() {
    return {
      stationName: "",
    };
  },
  watch: {
    selectedStation(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.stationName = newVal;
      }
    },
  },
  mounted() {
    this.stationName = this.selectedStation;
  },
  methods: {
    handleSearch() {
      if (!this.stationName.trim()) {
        alert("역 이름을 입력해주세요.");
        return;
      }
      this.$emit("search", this.stationName.trim());
    },
  },
};
</script>

<style scoped>
.header-section {
  justify-content: space-between;
  height: 70px;
  width: 100%;
  background: #fff;
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.search-container {
  width: 100%;
  display: grid;
  gap: 10px;
  align-items: center;
  grid-template-columns: 220px 1fr 100px;
}
.line-select,
.station-input {
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 14px;
}
.search-btn {
  padding: 10px 25px;
  color: #fff;
  border-radius: 4px;
  font-weight: bold;
}
.refresh-timer {
  width: 150px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #666;
  justify-content: flex-end;
}

.timer-text strong {
  color: #333;
}

/* 깜빡이는 포인트 효과 */
.refresh-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: blink 2s infinite;
}

@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 1;
  }
}
</style>
