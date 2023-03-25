
// 在上述代码中，我们首先调用了OpenAI的API，使用输入值作为提示，请求生成与之相关的建议问题。然后，我们对返回的建议问题进行处理，将其按行分割并过滤掉空行。最后，我们将处理好的建议问题返回给前端页面。

// 至此，我们已经完成了问题输入与选择模块的实现。用户可以在输入框中输入问题，系统会根据用户输入的问题实时生成建议问题。用户可以从建议问题中选择一个问题，也可以直接确认输入的问题。当用户确认问题后，我们将问题提交给后端处理，与ChatGPT进行交互，并返回答案给用户。

// 在整个实现过程中，我们详细地描述了各个功能模块的设计和实现，包括用户注册与登录、问题输入与选择等。希望这些细节能帮助你更好地理解和实现一个基于ChatGPT的微信小程序。


const axios = require("axios");
const OPENAI_API_KEY = "your_openai_api_key";

exports.main = async (event, context) => {
  const inputValue = event.inputValue;
  try {
    const res = await axios.post(
      "https://api.openai.com/v1/engines/davinci-codex/completions",
      {
        prompt: `给出关于"${inputValue}"的几个建议问题：`,
        max_tokens: 50,
        n: 1,
        stop: null,
        temperature: 0.5,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
      }
    );

    if (res.data && res.data.choices && res.data.choices.length > 0) {
      const suggestedQuestionsText = res.data.choices[0].text;
      const suggestedQuestions = suggestedQuestionsText
        .split("\n")
        .filter((item) => item.trim() !== "");
      return {
        code: 0,
        data: suggestedQuestions,
      };
    } else {
      return {
        code: -1,
        message: "获取建议问题失败",
      };
    }
  } catch (err) {
    console.error(err);
    return {
      code: -1,
      message: "获取建议问题失败",
    };
  }
};
