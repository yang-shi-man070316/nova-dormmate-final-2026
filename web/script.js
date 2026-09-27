const analyseBtn = document.getElementById('analyseBtn');
const tempInput = document.getElementById('tempInput');
const humInput = document.getElementById('humInput');
const statusText = document.getElementById('statusText');
const adviceText = document.getElementById('adviceText');
const historyList = document.getElementById('historyList');
// 新增按钮变量
const startAsrBtn = document.getElementById('startAsrBtn');
const asrResultText = document.getElementById('asrResultText');
const takePhotoBtn = document.getElementById('takePhotoBtn');
const closePhotoBtn = document.getElementById('closePhotoBtn');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
let mediaStream = null;
let records = [];

// 分析环境按钮
analyseBtn.onclick = function(){
    let tempStr = tempInput.value.trim();
    let humStr = humInput.value.trim();

    if(tempStr === "" || humStr === ""){
        alert("不能输入空值！温度和湿度都必须填写");
        return;
    }

    let temp = Number(tempStr);
    let hum = Number(humStr);
    if(isNaN(temp) || isNaN(hum)){
        alert("温度和湿度必须输入数字！");
        return;
    }

    let status = "";
    let advice = "";
    if(temp >=25){
        status = "偏热";
        advice = "建议通风降温";
    }else if(temp <=18){
        status = "偏冷";
        advice = "注意保暖";
    }else{
        status = "正常";
        advice = "环境舒适";
    }
    statusText.innerText = "当前状态：" + status;
    adviceText.innerText = "建议:"+advice;

    // 新增记录
    let now = new Date();
    let record = {
        time: now.toLocaleString(),
        temperature: temp,
        humidity: hum,
        status: status
    };
    records.push(record);
    renderHistory();
}

// 渲染历史记录
function renderHistory(){
    historyList.innerHTML = "";
    records.forEach((item,idx)=>{
        let div = document.createElement("div");
        div.className="history-item";
        div.innerText = `${item.time} 温度:${item.temperature}℃ 湿度:${item.humidity}% 状态:${item.status}`;
        historyList.appendChild(div);
    })
}

// CSV导出
function exportCSV(){
    let header = "time,temperature,humidity,status\n";
    let csvStr = header;
    records.forEach(item=>{
        // 把内容里的逗号做处理，避免表格错乱
        let t = `"${item.time}"`;
        csvStr += `${t},${item.temperature},${item.humidity},"${item.status}"\n`;
    })
    let blob = new Blob([csvStr],{type:"text/csv;charset=utf-8"});
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = "dormmate.csv";
    a.click();
    URL.revokeObjectURL(url);
}

// 摄像头打开
const openCamBtn = document.getElementById('openCamBtn');
openCamBtn.onclick = async function(){
    try{
        mediaStream = await navigator.mediaDevices.getUserMedia({video:true});
        video.srcObject = mediaStream;
        await video.play();
        alert("✅摄像头已开启");
    }catch(err){
        alert("❌打开摄像头失败："+err.message);
    }
}

// 拍照
takePhotoBtn.onclick = function(){
    if(!mediaStream){
        alert("请先打开摄像头！");
        return;
    }
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video,0,0);
    let imgUrl = canvas.toDataURL("image/png");
    let a = document.createElement("a");
    a.href = imgUrl;
    a.download = "snapshot.png";
    a.click();
}

// 关闭摄像头
closeCamBtn.onclick = function(){
    if(mediaStream){
        mediaStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        mediaStream = null;
        alert("✅摄像头已关闭");
    }else{
        alert("摄像头没有开启");
    }
}


// TTS朗读
const ttsBtn = document.getElementById('ttsBtn');
ttsBtn.onclick = function(){
    let statusTextContent = statusText.innerText;
    const utter = new SpeechSynthesisUtterance("当前环境状态：" + statusTextContent);
    utter.lang = 'zh-CN';
    speechSynthesis.speak(utter);
}

// ========== M3 ASR语音识别【带2条指令：朗读状态、拍照】 ==========
startAsrBtn.onclick = function() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("❌ 你的浏览器不支持语音识别，推荐Edge浏览器");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "zh-CN";
    recognition.start();
    asrResultText.innerText = "正在聆听...";

    recognition.onresult = function(e) {
        const text = e.results[0][0].transcript;
        asrResultText.innerText = text;

        // 指令1：朗读状态
        if(text.includes("朗读状态")){
            let statusTextContent = statusText.innerText;
            const utter = new SpeechSynthesisUtterance("当前环境状态：" + statusTextContent);
            utter.lang = 'zh-CN';
            speechSynthesis.speak(utter);
        }
        // 指令2：拍照
        if(text.includes("拍照")){
            takePhotoBtn.click();
        }

         //指令3：关闭摄像头
        if(text.includes("关闭摄像头")){
            closeCamBtn.click();
        }
    }
    recognition.onerror = function(e) {
        asrResultText.innerText = "识别失败";
    }
}
