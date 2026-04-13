<template>
  <div class="app-shell">
    <el-container class="layout">
      <el-header class="app-header">
        <div class="header-content">
          <h1>Fishpool 客户池管理系统</h1>
          <p>客户信息、评分和联系人统一管理</p>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          background-color="transparent"
          text-color="#fff"
          active-text-color="#ffd04b"
          class="header-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/customers">客户管理</el-menu-item>
          <el-menu-item index="/weekly-reports">周报管理</el-menu-item>
        </el-menu>
      </el-header>
      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const activeMenu = ref('/customers')

watch(
  () => route.path,
  (newPath) => {
    if (newPath.startsWith('/weekly-reports')) {
      activeMenu.value = '/weekly-reports'
    } else if (newPath.startsWith('/customers')) {
      activeMenu.value = '/customers'
    }
  },
  { immediate: true }
)

const handleMenuSelect = (index) => {
  router.push(index)
}
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
  justify-content: space-between;
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

.header-menu {
  border: none;
}

.header-menu :deep(.el-menu-item) {
  border-bottom: 2px solid transparent;
}

.header-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.header-menu :deep(.el-menu-item.is-active) {
  border-bottom-color: #ffd04b;
}

.app-main {
  padding: 24px;
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 18px 16px;
  }

  .header-content h1 {
    font-size: 22px;
  }

  .header-menu {
    width: 100%;
    margin-top: 12px;
  }

  .app-main {
    padding: 16px;
  }
}
</style>
