const analyseBtn = document.getElementById('analyseBtn');
const tempInput = document.getElementById('tempInput');
const humInput = document.getElementById('humInput');
const statusText = document.getElementById('statusText');
const adviceText = document.getElementById('adviceText');
const historyList = document.getElementById('historyList');

let records = [];

analyseBtn.onclick = function(){
    let tempStr = tempInput.value.trim();
    let humStr = humInput.value.trim();

    // 第一层：判断是否为空（任意一个为空就触发）
    if(tempStr === "" || humStr === ""){
        alert("不能输入空值！温度和湿度都必须填写");
        return;
    }

    // 两个框都有内容，再转数字
    let temp = Number(tempStr);
    let hum = Number(humStr);

    // 第二层：内容存在，但不是数字（字母、汉字）
    if(isNaN(temp) || isNaN(hum)){
        alert("请输入有效的数字！");
        return;
    }

    // 第三层：数字但是超出范围
    if(temp < 0 || temp >60 || hum <0 || hum>100){
        alert("温湿度数值超出合理范围");
        return;
    }

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

    statusText.textContent = "当前状态：" + status;
    adviceText.textContent = advice;

    let nowTime = new Date().toLocaleString();
    let record = {
        time: nowTime,
        temp: temp,
        hum: hum,
        status: status
    }
    records.push(record);
    renderHistory();
}

function renderHistory(){
    historyList.innerHTML = "";
    for(let r of records){
        let div = document.createElement("div");
        div.className = "history-item";
        div.textContent = `${r.time} | ${r.temp}℃ | ${r.hum}% | ${r.status}`;
        historyList.appendChild(div);
    }
}
