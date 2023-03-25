const cloud = require('wx-server-sdk');
cloud.init();
const db = cloud.database();

exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext();
  const openId = wxContext.OPENID;
  const userInfo = event.userInfo;

  // 查询用户是否已存在
  const userRes = await db.collection('users').where({ _openid: openId }).get();
  if (userRes.data && userRes.data.length > 0) {
    // 用户已存在，更新用户信息
    const user = userRes.data[0];
    await db.collection('users').doc(user._id).update({
      data: {
        userInfo,
        updateTime: db.serverDate(),
      },
    });
    return {
      code: 0,
      data: user,
    };
  } else {
    // 用户不存在，进行注册
    const newUser = {
        _openid: openId,
  userInfo: userInfo,
  createTime: db.serverDate(),
  updateTime: db.serverDate(),
};

try {
  // 将新用户信息插入到数据库中
  const res = await db.collection('users').add({
    data: newUser,
  });

  // 注册成功，将新用户信息返回
  newUser._id = res._id;
  return {
    code: 0,
    data: newUser,
  };
} catch (err) {
  console.error(err);
  return {
    code: -1,
    message: '注册失败',
  };
}

