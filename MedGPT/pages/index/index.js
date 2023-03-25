const app = getApp();

Page({
  data: {
    userInfo: null,
  },
  onLoad: function () {
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
      });
    } else {
      // 监听 app.js 中的 onLaunch 和 onShow 事件，判断用户是否已登录
      app.userInfoReadyCallback = (userInfo) => {
        this.setData({
          userInfo,
        });
      };
    }
  },
  onGetUserProfile: function (e) {
    if (!this.data.userInfo && e.detail.userInfo) {
      // 获取用户微信信息成功
      this.setData({
        userInfo: e.detail.userInfo,
      });
      app.globalData.userInfo = e.detail.userInfo;
      this.registerOrLogin();
    }
  },
  registerOrLogin: function () {
    // 调用云函数进行用户注册和登录
    wx.cloud
      .callFunction({
        name: 'registerOrLogin',
        data: {
          userInfo: this.data.userInfo,
        },
      })
      .then((res) => {
        if (res.result && res.result.code === 0) {
          // 注册或登录成功，将用户信息存储到全局变量中
          app.globalData.userInfo = res.result.data;
          this.setData({
            userInfo: res.result.data,
          });
        } else {
          wx.showToast({
            title: '注册或登录失败',
            icon: 'none',
          });
        }
      })
      .catch((err) => {
        wx.showToast({
          title: '注册或登录失败',
          icon: 'none',
        });
      });
  },
});
