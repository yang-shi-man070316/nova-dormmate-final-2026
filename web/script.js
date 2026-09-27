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

    // 改成不带逗号的时间格式，不会拆分表格，WPS不容易出现#
    let nowTime = new Date().toISOString();
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

// 导出CSV
function exportCSV() {
    let csvContent = "time,temperature,humidity,status\n";
    records.forEach(item => {
        let line = `${item.time},${item.temp},${item.hum},${item.status}\n`
        csvContent += line;
    });
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "dormmate.csv";
    a.click();
    URL.revokeObjectURL(url);
}
document.getElementById("exportCsvBtn").addEventListener("click", exportCSV);

// ========== M3 Camera 摄像头拍照 ==========
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const openCameraBtn = document.getElementById('openCameraBtn');
const takePhotoBtn = document.getElementById('takePhotoBtn');

let mediaStream = null;

openCameraBtn.onclick = async function() {
    alert("✅ 按钮点击生效，开始尝试调用摄像头");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("❌ 浏览器不支持摄像头API！请用Chrome/Edge，localhost访问");
        return;
    }
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = mediaStream;
        alert("✅ 摄像头已开启");
    } catch(err) {
        alert("❌ 打开摄像头失败：" + err.name);
    }
}

takePhotoBtn.onclick = function() {
    alert("拍照按钮被点击");
    if(!mediaStream){
        alert("请先打开摄像头");
        return;
    }
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const link = document.createElement('a');
    link.download = `snapshot_${new Date().getTime()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
}

// ========== M3 TTS朗读 ==========
const ttsReadBtn = document.getElementById('ttsReadBtn');
ttsReadBtn.onclick = function() {
    let statusText = document.getElementById('statusText').innerText;
    const utter = new SpeechSynthesisUtterance("当前环境状态：" + statusText);
    utter.lang = 'zh-CN';
    speechSynthesis.speak(utter);
}

// ========== M3 ASR语音识别 ==========
const startAsrBtn = document.getElementById('startAsrBtn');
const asrResultText = document.getElementById('asrResultText');

startAsrBtn.onclick = function() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("❌ 浏览器不支持语音识别，请使用Edge浏览器");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "zh-CN";
    recognition.start();
    asrResultText.innerText = "正在聆听...";
    recognition.onresult = function(e) {
        const text = e.results[0][0].transcript;
        asrResultText.innerText = text;
    }
    recognition.onerror = function(e) {
        asrResultText.innerText = "识别失败";
    }
}

