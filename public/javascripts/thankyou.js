
let thankMiddle = document.querySelector('.thank-middle')
let number = sessionStorage.getItem('orderNumber');
thankMiddle.textContent = number



renderThankyou()
function renderThankyou() {
  // 前端使⽤ fetch() 檢查使⽤者是否登入，若未登入，直接導回⾸⾴
  // 檢查有沒有sessionstorage，沒有的話導到首頁
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data["error"] === true || number.length===0) {
      document.location.href = '/'
    }
    else{
      window.history.pushState({}, "", `/thankyou?number=${number}`)
    }
  })

}




