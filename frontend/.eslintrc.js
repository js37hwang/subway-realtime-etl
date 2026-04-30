module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    "plugin:vue/recommended",
    "eslint:recommended",
    "plugin:prettier/recommended",
    "prettier" // Prettier와 충돌 방지
  ],
  parserOptions: {
    parser: "@babel/eslint-parser",
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
    "vue/multi-word-component-names": "off" // 마감 기한 내 빠른 개발을 위해 컴포넌트명 규칙 완화
  },
};
