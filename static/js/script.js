function load() {
  // alert("ページが読み込まれました！");
  var param = location.search;
  console.log(param);
  userID = getParam('userID');
  if(userID == null){
    console.log('userID is null!');
  }else{
    console.log('userID is ' + userID);
  }
  warningCode = getParam('warningCode');
  if(warningCode == null){
    console.log('warningCode is null!');
  }else{
    console.log('warningCode is ' + warningCode);
  }
  // ?userID=12345&warningCode=30
}
window.onload = load;

function test() {
  navigator.geolocation.getCurrentPosition(success,fail);
}

function success(pos){
  const lat = pos.coords.latitude;   //緯度を取得して定数latに代入
  const lng = pos.coords.longitude;  //経度を取得して定数lngに代入
  const accuracy = pos.coords.accuracy;  //同じく精度を定数accuracyに代入
  // window.alert('pos');
  var url = 'http://localhost:5001/location'; // リクエスト先URL
  var data = 'lat=' + lat + '&lng=' + lng + '&userID=' + userID + '&warningCode=' + warningCode ; // 送信データ ('param=value&...')
  var request = new XMLHttpRequest();
  var postUrl = location.protocol + '//' + location.hostname + ':' + location.port + '' + location.pathname;
  request.open('POST', postUrl);
  document.getElementById('sendButton').textContent = '送信中';
  document.getElementById('sendButton').disabled = true;
  request.onreadystatechange = function () {
      if (request.readyState != 4) {
        // リクエスト中
      } else if (request.status != 200) {
        // 失敗
        console.log(request.status);
        console.log('bad!')
        document.getElementById('sendButton').textContent = '現在地情報を送信';
        document.getElementById('sendButton').disabled = false;
        document.getElementById('afterSend').innerHTML = '送信に失敗しました。<br>再送信してください。';
        document.getElementById('afterSend').classList.add = 'py-1';
      } else {
        // 送信成功
        console.log('good!')
        var result = request.responseText;
        console.log(result)
        document.getElementById('sendButton').textContent = '送信完了';
        document.getElementById('sendButton').disabled = true;
        document.getElementById('afterSend').innerHTML = 'このタブは閉じてください。<br>LINE通知が届きます。';
        document.getElementById('afterSend').classList.add = 'py-1';
      }
  };
  console.log(request.status);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  request.send(data);
}

function fail(error){
  window.alert('位置情報の取得に失敗しました。エラーコード：' + error.code)
}

function getParam(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
