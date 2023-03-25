const app = getApp();

Page({
  data: {
    inputValue: '',
    messages: [],
  },
  onInputChange: function (e) {
    this.setData({
      inputValue: e.detail.value,
    });
  },
  onConfirm: function () {
    const message = this.data.inputValue;
    if (message.trim() === '') {
      return;
    }
    this.sendMessage(message);
    this.setData({
      inputValue: '',
    });
  },
  scrollToLower: function () {
    // 滚动到底部时触发的函数，可以在这里实现加载更多历史消息的功能
  },
  sendMessage: function (message) {
    this.addMessage('user', message);
    this.getChatGPTResponse(message);
  },
  addMessage: function (sender, content) {
    const messages = this.data.messages;
    messages.push({
      sender: sender,
      content: content,
    });
    this.setData({
      messages: messages,
    });
    this.scrollToBottom();
  },
  scrollToBottom: function () {
    wx.createSelectorQuery()
      .select('.chat-section')
      .scrollOffset((res) => {
        const scrollView = wx.createSelectorQuery().select('.chat-section');
        scrollView.scrollTop(res.scrollHeight, true);
      })
      .exec();
  },
  getChatGPTResponse: function (question) {
    wx.showLoading({
      title: '正在获取回答...',
    });
    wx.cloud
      .callFunction({
        name: 'getChatGPTResponse',
        data: {
          question: question,
        },
      })
      .then((res) => {
        wx.hideLoading();
        if (res.result && res.result.code === 0) {
          const answer = res.result.data;
          this.addMessage('chatgpt', answer);
        } else {
          wx.showToast({
            title: '获取回答失败',
            icon: 'none',
          });
        }
      })
      .catch((err) => {
        wx.hideLoading();
        wx.showToast({
          title: '获取回答失败',
          icon: 'none',
        });
      });
  },
});
