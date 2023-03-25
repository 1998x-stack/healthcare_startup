// 3.5 用户信息与档案管理（profile.js）

const app = getApp();
Page({
  data: {
    userInfo: null,
    medicalRecords: [],
  },
  onLoad: function () {
    this.setData({
      userInfo: app.globalData.userInfo,
    });
    this.getMedicalRecords();
  },
  getMedicalRecords: function() {
    // 调用后端接口，获取用户的医疗档案列表
    // ...
    },
    onMedicalRecordSelected: function (e) {
    const recordId = e.currentTarget.dataset.id;
    this.viewMedicalRecord(recordId);
    },
    viewMedicalRecord: function (recordId) {
    // 跳转到医疗档案详情页面
    wx.navigateTo({
    url: /pages/medical-record/medical-record?id=${recordId},
    });
    },
    onAddMedicalRecord: function () {
    // 跳转到新增医疗档案页面
    wx.navigateTo({
    url: '/pages/add-medical-record/add-medical-record',
    });
    },
    });
