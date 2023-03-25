// 3.3 聊天界面（chat.js）

const app = getApp();
Page({
  data: {
    chatHistory: [],
    question: "",
    answer: "",
  },
  onLoad: function (options) {
    this.setData({
      question: options.question,
    });
    this.getAnswer(options.question);
  },
  getAnswer: function (question) {
    // 调用后端接口，传递问题，获取ChatGPT的回答
    // ...
  },
  onAnswerReceived: function (answer) {
    // 更新聊天历史
    const chatHistory = this.data.chatHistory;
    chatHistory.push({
      role: "user",
      content: this.data.question,
    });
    chatHistory.push({
      role: "chatgpt",
      content: answer,
    });
    this.setData({
      chatHistory,
      question: "",
      answer: "",
    });
  },
});
