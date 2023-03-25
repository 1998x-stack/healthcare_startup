const app = getApp();

Page({
  data: {
    inputValue: '',
    suggestedQuestions: [],
  },
  onInputChange: function (e) {
    this.setData({
      inputValue: e.detail.value,
    });
    this.getSuggestedQuestions();
  },
  onConfirm: function () {
    // 用户确认输入，将问题提交给后端处理
    const question = this.data.inputValue;
    // ...
  },
  getSuggestedQuestions: function () {
    // 调用云函数获取建议问题
    wx.cloud
      .callFunction({
        name: 'getSuggestedQuestions',
        data: {
          inputValue: this.data.inputValue,
        },
      })
      .then((res) => {
        if (res.result && res.result.code === 0) {
          // 获取建议问题成功
          this.setData({
            suggestedQuestions: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取建议问题失败',
            icon: 'none',
          });
        }
      })
      .catch((err) => {
        wx.showToast({
          title: '获取建议问题失败',
          icon: 'none',
        });
      });
  },
  onSuggestionTap: function (e) {
    const index = e.currentTarget.dataset.index;
    const question = this.data.suggestedQuestions[index];
    this.setData({
      inputValue: question,
    });
    this.onConfirm();
  },
});
