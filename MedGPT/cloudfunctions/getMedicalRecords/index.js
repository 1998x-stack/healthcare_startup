const cloud = require('wx-server-sdk');

cloud.init();

const db = cloud.database();

exports.main = async (event, context) => {
  try {
    const { OPENID } = cloud.getWXContext();
    const medicalRecords = await db.collection('medical_records').where({ _openid: OPENID }).get();
    return {
      code: 0,
      data: medicalRecords.data,
    };
  } catch (err) {
    console.error(err);
    return {
      code: -1,
      message: '获取档案列表失败',
    };
  }
};
