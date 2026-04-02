/**
 * 计算客户等级
 * Level A: X>=70 AND Y>=70 AND Z>=70
 * Level B: 至少两项>=70
 * Level C: X>=70
 * Level D: 其他
 */
export function calculateLevel(scoreX, scoreY, scoreZ) {
  const x = Number(scoreX) || 0
  const y = Number(scoreY) || 0
  const z = Number(scoreZ) || 0

  // Level A: 三项都>=70
  if (x >= 70 && y >= 70 && z >= 70) {
    return 'A'
  }

  // Level B: 至少两项>=70
  const highScoreCount = [x >= 70, y >= 70, z >= 70].filter(Boolean).length
  if (highScoreCount >= 2) {
    return 'B'
  }

  // Level C: X>=70
  if (x >= 70) {
    return 'C'
  }

  // Level D: 其他
  return 'D'
}

/**
 * 获取等级对应的颜色
 */
export function getLevelColor(level) {
  const colors = {
    A: '#F56C6C',  // 红色
    B: '#409EFF',  // 蓝色
    C: '#67C23A',  // 绿色
    D: '#909399'   // 灰色
  }
  return colors[level] || colors.D
}
