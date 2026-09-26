// 获取页面元素
const tempInput = document.getElementById('tempInput');
const humInput = document.getElementById('humInput');
const analyseBtn = document.getElementById('analyseBtn');
const statusText = document.getElementById('statusText');
const adviceText = document.getElementById('adviceText');
const historyList = document.getElementById('historyList');

// 历史记录数组
let historyArr = [];

// 点击分析环境按钮
analyseBtn.onclick = function(){
    //1.拿到输入框原始字符串，去除首尾空格
    let tempStr = tempInput.value.trim();
    let humStr = humInput.value.trim();

    //【第一步：判断是否为空】
    if(tempStr === '' || humStr === ''){
        alert("请输入温度和湿度！");
        return;
    }

    //【第二步：转数字】
    let temp = Number(tempStr);
    let hum = Number(humStr);

    //【第三步：判断是不是有效数字】
    if(isNaN(temp) || isNaN(hum)){
        alert("输入不是有效数字！");
        return;
    }

    //【第四步：判断数值范围】
    if(temp < 0 || temp > 60 || hum <0 || hum >100){
        alert("温湿度数值超出合理范围");
        return;
    }

    //4. 判断温湿度状态
    let status, advice;
    if(temp >= 30){
        status = "偏热";
        advice = "注意通风降温";
    }else if(temp >=22 && temp <30){
        status = "正常";
        advice = "环境舒适";
    }else{
        status = "偏冷";
        advice = "注意保暖";
    }

    //5.页面展示状态和建议
    statusText.textContent = status;
    adviceText.textContent = advice;

    //6.获取当前日期时间
    let nowTime = new Date().toLocaleString();

    //7.新增一条记录放进数组
    let record = {
        time: nowTime,
        temp: temp,
        hum: hum,
        status: status
    };
    historyArr.push(record);

    //8.渲染全部历史记录
    let html = '';
    for(let i = 0; i < historyArr.length; i++){
        let r = historyArr[i];
        html += `<div class="history-item">${r.time} | ${r.temp}℃ | ${r.hum}% | ${r.status}</div>`
    }
    historyList.innerHTML = html;
}
