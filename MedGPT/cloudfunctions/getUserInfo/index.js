const cloud = require('wx-server-sdk');

cloud.init();

const db = cloud.database();

exports.main = async (event, context) => {
  try {
    const { OPENID } = cloud.getWXContext();
    const userInfo = await db.collection('users').where({ _openid: OPENID }).get();
    if (userInfo.data.length > 0) {
      return {
        code: 0,
        data: userInfo.data[0],
      };
    } else {
      return {
        code: -1,
        message: '用户未找到',
      };
    }
  } catch (err) {
    console.error(err);
    return {
      code: -1,
      message: '获取用户信息失败',
    };
  }
};
