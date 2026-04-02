<template>
  <div class="app-shell">
    <el-container class="layout">
      <el-header class="app-header">
        <div class="header-content">
          <h1>Fishpool 客户池管理系统</h1>
          <p>客户信息、评分和联系人统一管理</p>
        </div>
      </el-header>
      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.layout {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  min-height: 88px;
  height: auto;
  padding: 20px 24px;
  background:
    linear-gradient(135deg, rgba(24, 144, 255, 0.92), rgba(16, 82, 171, 0.96)),
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 30%);
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.16);
}

.header-content h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.header-content p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
}

.app-main {
  padding: 24px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 18px 16px;
  }

  .header-content h1 {
    font-size: 22px;
  }

  .app-main {
    padding: 16px;
  }
}
</style>
