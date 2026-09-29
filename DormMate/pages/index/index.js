// index.js
Page({
  data: {
    // 输入框
    temperature: "",
    humidity: "",
    // 当前选中宿舍
    currentDorm: "dorm-a",
    // 三个宿舍独立存储数据
    dormData: {
      "dorm-a": {
        temperature: 22,
        humidity: 50,
        status: "环境舒适",
        time: "2026-09-29 12:00",
        historyTemp: [20,23,22,24,21],
        historyHum: [48,52,50,53,49]
      },
      "dorm-b": {
        temperature: 28,
        humidity: 70,
        status: "偏热",
        time: "2026-09-29 12:10",
        historyTemp: [26,29,28,27,30],
        historyHum: [68,72,70,71,69]
      },
      "dorm-c": {
        temperature: 18,
        humidity: 35,
        status: "偏冷偏干",
        time: "2026-09-29 12:20",
        historyTemp: [17,19,18,16,20],
        historyHum: [33,36,35,34,37]
      }
    },
    status: "",
    time: "",
    advice: "",
    historyTemp: [],
    historyHum: []
  },

  onLoad() {
    // 页面加载，初始化加载当前宿舍数据
    this.loadDormData(this.data.currentDorm);
  },

  // 切换宿舍按钮
  switchDorm(e) {
    const dormKey = e.currentTarget.dataset.dorm;
    this.setData({
      currentDorm: dormKey
    })
    this.loadDormData(dormKey);
  },

  // 加载指定宿舍的数据到页面【增加防崩溃判断】
  loadDormData(dormKey) {
    // 新增：如果找不到这个宿舍，直接退出，不继续执行
    if (!this.data.dormData[dormKey]) {
      console.error("找不到宿舍：", dormKey);
      return;
    }
    const dorm = this.data.dormData[dormKey];
    this.setData({
      temperature: dorm.temperature,
      humidity: dorm.humidity,
      status: dorm.status,
      time: dorm.time,
      advice: dorm.advice || "",
      historyTemp: dorm.historyTemp,
      historyHum: dorm.historyHum
    }, ()=>{
      this.drawChart();
    })
  },

  // 分析环境并保存【已修复trim报错】
  analyseEnv() {
    let tempStr = String(this.data.temperature).trim();
    let humStr = String(this.data.humidity).trim();

    if (tempStr === "" || humStr === "") {
      wx.showToast({
        title: "不能输入空值！温度和湿度都必须填写",
        icon: "none"
      })
      return;
    }
    let temp = Number(tempStr);
    let hum = Number(humStr);
    if(isNaN(temp) || isNaN(hum)){
      wx.showToast({title:"请输入数字",icon:"none"})
      return;
    }

    let status = "";
    let advice = "";
    if (temp >= 20 && temp <= 26 && hum >=40 && hum <=65) {
      status = "环境舒适";
      advice = "温湿度合适，保持通风";
    } else if(temp >26){
      status = "偏热";
      advice = "建议适当降温";
    }else if(temp <20){
      status = "温度偏低";
      advice = "建议适当保暖";
    }
    if(hum>65){
      status = "偏潮湿";
      advice = "注意除湿";
    }else if(hum<40){
      status = "偏干燥";
      advice = "建议增加空气湿度";
    }

    const now = new Date();
    const time = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`

    const currentDormKey = this.data.currentDorm;
    const dormData = this.data.dormData;

    // 更新宿舍最新状态
    dormData[currentDormKey].temperature = temp;
    dormData[currentDormKey].humidity = hum;
    dormData[currentDormKey].status = status;
    dormData[currentDormKey].time = time;
    dormData[currentDormKey].advice = advice;

    // 追加历史数据，最多保留5个点
    dormData[currentDormKey].historyTemp.push(temp);
    dormData[currentDormKey].historyHum.push(hum);
    if(dormData[currentDormKey].historyTemp.length>5){
      dormData[currentDormKey].historyTemp.shift();
      dormData[currentDormKey].historyHum.shift();
    }

    this.setData({
      dormData: dormData,
      temperature: temp,
      humidity: hum,
      status: status,
      time: time,
      advice: advice,
      historyTemp: dormData[currentDormKey].historyTemp,
      historyHum: dormData[currentDormKey].historyHum
    }, ()=>{
      this.drawChart();
    })

    wx.showToast({title:"分析完成",icon:"success"})
  },

  // 绘制折线图
  drawChart() {
    const ctx = wx.createCanvasContext('chartCanvas');
    ctx.clearRect(0,0,320,200);

    const tempArr = this.data.historyTemp;
    const humArr = this.data.historyHum;
    if(tempArr.length ===0) return;

    // 温度蓝色线
    ctx.setStrokeStyle('#1677ff');
    ctx.setLineWidth(2);
    ctx.beginPath();
    let stepX = 300/(tempArr.length-1);
    for(let i=0;i<tempArr.length;i++){
      let x = 20 + i*stepX;
      let y = 180 - (tempArr[i]-10)*5;
      if(i===0){
        ctx.moveTo(x,y);
      }else{
        ctx.lineTo(x,y);
      }
    }
    ctx.stroke();

    // 湿度绿色线
    ctx.setStrokeStyle('#00b42a');
    ctx.beginPath();
    for(let i=0;i<humArr.length;i++){
      let x = 20 + i*stepX;
      let y = 180 - (humArr[i]-20)*2.5;
      if(i===0){
        ctx.moveTo(x,y);
      }else{
        ctx.lineTo(x,y);
      }
    }
    ctx.stroke();
    ctx.draw();
  },

  // 输入框绑定事件
  onTempInput(e){
    this.setData({temperature:e.detail.value})
  },
  onHumInput(e){
    this.setData({humidity:e.detail.value})
  }
})