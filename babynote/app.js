// app.js
const api = require('./utils/api')

App({
  async onLaunch() {
    console.log('BabyNote 启动')
    // 如果没有登录，静默尝试登录
    if (!api.getToken()) {
      try {
        await api.login()
        console.log('自动登录成功')
      } catch (err) {
        console.log('自动登录失败（请先在「我的」页面登录）')
      }
    }
  },
  globalData: {
    userInfo: null
  }
})
