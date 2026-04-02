<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <h1>Fishpool 客户池管理系统</h1>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.app-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.app-main {
  padding: 0;
}
</style>
