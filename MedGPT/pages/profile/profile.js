data: {
    userInfo: {},
    medicalRecords: [],
  },

//   接下来，我们需要在页面加载时获取用户信息和档案列表。
//   可以在onLoad生命周期函数中实现：
  onLoad: function () {
    this.fetchUserInfo();
    this.fetchMedicalRecords();
  },

//   我们分别调用了getUserInfo和getMedicalRecords云函数来获取用户信息和档案列表。
//   成功获取后，我们将它们分别存储到data中的userInfo和medicalRecords中。
//   如果获取失败，我们会显示一个提示消息。


  fetchUserInfo: function () {
    // 获取用户信息的逻辑
    wx.cloud.callFunction({
      name: 'getUserInfo',
      success: res => {
        if (res.result.code === 0) {
          this.setData({
            userInfo: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取用户信息失败',
            icon: 'none',
          });
        }
      },
      fail: err => {
        console.error(err);
        wx.showToast({
          title: '获取用户信息失败',
          icon: 'none',
        });
      },
    });
  },
  
  fetchMedicalRecords: function () {
    // 获取档案列表的逻辑
    wx.cloud.callFunction({
      name: 'getMedicalRecords',
      success: res => {
        if (res.result.code === 0) {
          this.setData({
            medicalRecords: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取档案列表失败',
            icon: 'none',
          });
        }
      },
      fail: err => {
        console.error(err);
        wx.showToast({
          title: '获取档案列表失败',
          icon: 'none',
        });
      },
    });
  },
    
//   在profile.wxml中，我们需要展示用户信息和档案列表。可以通过wx:for循环来遍历medicalRecords，并显示每个档案的信息：