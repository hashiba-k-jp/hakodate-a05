
   
function load() {
  alert("ページが読み込まれました！");
  var param = location.search;
  alert(param);
  userID = getParam('userID');
  if(userID == null){alert('userID is null!');}
  warningCode = getParam('warningCode');
  if(warningCode == null){alert('warningCode is null!');}
}
window.onload = load;

function test() {
  if (window.confirm("現在地を取得します。")){
    navigator.geolocation.getCurrentPosition(success,fail);
  }else{
    window.alert('キャンセルしました。');
  }
}

function success(pos){
  const lat = pos.coords.latitude;   //緯度を取得して定数latに代入
  const lng = pos.coords.longitude;  //経度を取得して定数lngに代入
  const accuracy = pos.coords.accuracy;  //同じく精度を定数accuracyに代入
  // window.alert('pos');
  var url = 'http://localhost:8000'; // リクエスト先URL
  var data = 'lat=' + lat + '&lng=' + lng; // 送信データ ('param=value&...')
  var request = new XMLHttpRequest();
  request.open('POST', url);
  request.onreadystatechange = function () {
      if (request.readyState != 4) {
        // リクエスト中
      } else if (request.status != 200) {
        // 失敗
        console.log(request.status);
        console.log('bad!')
      } else {
        // 送信成功
        console.log('good!')
        var result = request.responseText;
        console.log(result)
      }
  };
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  request.send(data);
  window.alert('位置情報を送信しました。\nこのタブは閉じて下さい。')
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
