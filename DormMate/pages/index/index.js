Page({
  data: {
    temperature: "",
    humidity: "",
    status: "当前状态",
    advice: ""
  },

  // 读取温度输入
  onTempInput(e) {
    this.setData({
      temperature: e.detail.value
    })
  },
  // 读取湿度输入
  onHumInput(e) {
    this.setData({
      humidity: e.detail.value
    })
  },

  // 点击分析按钮
  analyseEnv() {
    let tempStr = this.data.temperature.trim();
    let humStr = this.data.humidity.trim();

    // 校验：空值
    if (tempStr === "" || humStr === "") {
      wx.showToast({
        title: "不能输入空值！温度和湿度都必须填写",
        icon: "none"
      })
      return;
    }

    let temp = Number(tempStr);
    let hum = Number(humStr);
    // 校验：不是数字
    if (isNaN(temp) || isNaN(hum)) {
      wx.showToast({
        title: "请输入有效的数字",
        icon: "none"
      })
      return;
    }

    // =====业务判断规则【和M1网页完全一致！】=====
    let statusText = "";
    let adviceText = "";
    if(temp >= 28){
      statusText = "偏热";
      adviceText = "温度偏高，建议通风降温";
    }else if(temp <=18){
      statusText = "偏冷";
      adviceText = "温度偏低，注意保暖";
    }else{
      statusText = "正常";
      adviceText = "宿舍温湿度环境舒适";
    }

    this.setData({
      status: statusText,
      advice: adviceText
    })
  }
})

