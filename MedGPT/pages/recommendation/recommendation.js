/*
需要在recommendation.js中完成以下功能：

从后端获取医院列表；
根据用户选择的医院筛选科室；
根据用户选择的科室筛选医生；
展示推荐的医生列表。
*/

data: {
    hospitalList: [], // 医院列表
    departmentList: [], // 科室列表
    doctorList: [], // 医生列表
    selectedHospital: null, // 用户选择的医院
    selectedDepartment: null, // 用户选择的科室
  }


//   我们需要实现从后端获取医院列表的功能。
//   在onLoad函数中，调用一个自定义函数fetchHospitalList：
// 我们通过调用云函数getHospitalList来获取医院列表。
// 成功获取医院列表后，我们将其存储到data中的hospitalList中。
// 如果获取失败，我们会显示一个提示消息。
  onLoad: function () {
    this.fetchHospitalList();
  },
  
  fetchHospitalList: function () {
    // 调用云函数获取医院列表
    wx.cloud.callFunction({
      name: 'getHospitalList',
      success: res => {
        if (res.result.code === 0) {
          this.setData({
            hospitalList: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取医院列表失败',
            icon: 'none',
          });
        }
      },
      fail: err => {
        console.error(err);
        wx.showToast({
          title: '获取医院列表失败',
          icon: 'none',
        });
      },
    });
  },


//   我们需要实现根据用户选择的医院筛选科室的功能。
//   在用户选择医院后，调用一个自定义函数fetchDepartmentList：
  
// 我们根据用户选择的医院ID调用云函数getDepartmentList来获取科室列表。
// 成功获取科室列表后，我们将其存储到data中的departmentList中。
// 如果获取失败，我们会显示一个提示消息。

  onHospitalSelected: function (event) {
    const selectedHospital = event.currentTarget.dataset.hospital;
    this.setData({
      selectedHospital,
    });
    this.fetchDepartmentList(selectedHospital.id);
  },
  
  fetchDepartmentList: function (hospitalId) {
    // 调用云函数获取科室列表
    wx.cloud.callFunction({
      name: 'getDepartmentList',
      data: {
        hospitalId,
      },
      success: res => {
        if (res.result.code === 0) {
          this.setData({
            departmentList: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取科室列表失败',
            icon: 'none',
          });
        }
      },
      fail: err => {
        console.error(err);
        wx.showToast({
          title: '获取科室列表失败',
          icon: 'none',
        });
      },
    });
  },
//   实现根据用户选择的科室筛选医生的功能。
//   在用户选择科室后，调用一个自定义函数`fetchDoctorList`
// 我们根据用户选择的科室ID调用云函数getDoctorList来获取医生列表。
// 成功获取医生列表后，我们将其存储到data中的doctorList中。
// 如果获取失败，我们会显示一个提示消息。


onDepartmentSelected: function (event) {
    const selectedDepartment = event.currentTarget.dataset.department;
    this.setData({
      selectedDepartment,
    });
    this.fetchDoctorList(selectedDepartment.id);
  },
  
  fetchDoctorList: function (departmentId) {
    // 调用云函数获取医生列表
    wx.cloud.callFunction({
      name: 'getDoctorList',
      data: {
        departmentId,
      },
      success: res => {
        if (res.result.code === 0) {
          this.setData({
            doctorList: res.result.data,
          });
        } else {
          wx.showToast({
            title: '获取医生列表失败',
            icon: 'none',
          });
        }
      },
      fail: err => {
        console.error(err);
        wx.showToast({
          title: '获取医生列表失败',
          icon: 'none',
        });
      },
    });
  },
//   最后，我们需要展示推荐的医生列表。在recommendation.wxml中，
//   我们可以通过wx:for循环来遍历doctorList，并显示每个医生的信息：
//   至此，我们已经实现了医院与医生推荐功能的主要部分。
// 在实际应用中，你还可以根据需要添加更多细节，比
// 如医生的头像、擅长领域、好评率等信息。
// 此外，你还可以考虑实现医生详情页面，
// 以便用户查看更多关于医生的信息并进行预约等操作。
  