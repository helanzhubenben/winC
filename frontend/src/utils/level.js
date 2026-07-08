/**
 * 计算客户等级
 * 客户等级由后端按所有客户三维总分排名后统一计算。
 * 前端只能预判三维有 0 分时为 X，否则保存后自动排名。
 */
export function calculateLevel(scoreX, scoreY, scoreZ) {
  const x = Number(scoreX) || 0
  const y = Number(scoreY) || 0
  const z = Number(scoreZ) || 0

  if ([x, y, z].some((score) => score === 0)) {
    return 'X'
  }

  return '保存后自动排名'
}

/**
 * 获取等级对应的颜色
 */
export function getLevelColor(level) {
  const colors = {
    A: '#F56C6C',  // 红色
    B: '#409EFF',  // 蓝色
    C: '#67C23A',  // 绿色
    D: '#909399',  // 灰色
    X: '#E6A23C'   // 橙色
  }
  return colors[level] || colors.D
}
