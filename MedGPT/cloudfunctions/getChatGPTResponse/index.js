// 1）从请求参数中提取问题；
// 2）调用OpenAI API发送问题并接收回答；
// 3）将回答返回给前端。

const cloud = require('wx-server-sdk');
const axios = require('axios');

cloud.init();

const OPENAI_API_KEY = 'your_openai_api_key';
const OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci-codex/completions';

axios.defaults.headers.common['Authorization'] = `Bearer ${OPENAI_API_KEY}`;

exports.main = async (event, context) => {
  const question = event.question;

  try {
    const response = await axios.post(OPENAI_API_URL, {
      prompt: `问题：${question}\n回答：`,
      max_tokens: 100,
      n: 1,
      stop: null,
      temperature: 0.8,
      top_p: 1,
    });

    if (response.data.choices.length > 0) {
      const answer = response.data.choices[0].text.trim();
      return {
        code: 0,
        data: answer,
      };
    } else {
      return {
        code: -1,
        message: '获取回答失败',
      };
    }
  } catch (err) {
    console.error(err);
    return {
      code: -1,
      message: '获取回答失败',
    };
  }
};

/* Explain
在上述代码中，我们首先从请求参数中提取问题，并通过axios.post()方法
调用OpenAI API。API请求中的prompt字段包含问题，
并以“回答：”作为回答的开始。我们设置max_tokens为100，
以限制回答的长度。temperature和top_p参数用于控制生成回答的随机性。

收到OpenAI API的响应后，我们检查是否存在至少一个回答选项。
如果存在，则提取第一个选项的文本内容作为回答，并将其返回给前端。
如果不存在，则返回获取回答失败的错误信息。
*/