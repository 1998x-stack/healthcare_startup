// 3.1 用户注册与登录（index.js）

const app = getApp();
Page({
  data: {
    userInfo: null,
  },
  onLoad: function () {
    wx.login({
      success: (res) => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        // ...
      },
    });
  },
  getUserProfile() {
    wx.getUserProfile({
      desc: "用于完善用户资料",
      success: (res) => {
        this.setData({
          userInfo: res.userInfo,
        });
        app.globalData.userInfo = res.userInfo;
      },
    });
  },
});
