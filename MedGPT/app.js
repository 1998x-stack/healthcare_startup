App({
    onLaunch: function () {
      wx.cloud.init({
        env: 'your-cloud-environment-id',
        traceUser: true,
      });
    },
  });
  