// 3.2 问题输入与选择（question.js）


Page({
  data: {
    question: "",
    questionList: [
      "如何预防感冒？",
      "高血压患者需要注意哪些饮食禁忌？",
      // ...
    ],
  },
  inputQuestion: function (e) {
    this.setData({
      question: e.detail.value,
    });
  },
  chooseQuestion: function (e) {
    const question = e.currentTarget.dataset.question;
    this.setData({
      question,
    });
  },
  onSubmit: function () {
    // 跳转到聊天界面，并传递问题
    wx.navigateTo({
      url: `/pages/chat/chat?question=${this.data.question}`,
    });
  },
});
