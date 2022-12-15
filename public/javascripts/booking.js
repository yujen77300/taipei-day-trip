let topTitle = document.querySelector('.top-title')
let bookingName = document.querySelector('.booking-name')
let scheduledDate = document.getElementById('scheduled-date')
let scheduledFee = document.getElementById('scheduled-fee')
let totalFee = document.querySelector('.total-fee')
let scheduledTime = document.getElementById('scheduled-time')
let scheduledPlace = document.getElementById('scheduled-place')
let scheduledImg = document.querySelector('.booking-left')
let scehduledUsername = document.getElementById('scehduled-username')
let scehduledEmail = document.getElementById('scehduled-email')
let bookingDeleteBtn = document.querySelector('.bookingDelete-btn')
let noSchedule = document.querySelector('.no-schedule')
let bookInfo = document.querySelector('.booking-info')
let bookMiddle = document.querySelector('.booking-middle')
let bookBottom = document.querySelector('.booking-bottom')
let bookTotal = document.querySelector('.booking-total')
let divider = document.querySelectorAll('.divider')
let footerExtend = document.querySelector('.footer-extend')



renderBooking()
function renderBooking() {
  // 前端使⽤ fetch() 檢查使⽤者是否登入，若未登入，直接導回⾸⾴
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data["error"] === true) {
      document.location.href = '/'
    }
    else {
      fetch(
        "/api/booking"
      ).then(function (response) {
        return response.json();
      }).then(function (data) {
        // 判斷如果是空的object
        if (Object.keys(data["data"]).length === 0) {
          fetch(
            "/api/user/auth"
          ).then(function (response) {
            return response.json();
          }).then(function (data) {
            topTitle.textContent = `您好，${data["data"]["name"]}，待預訂的行程如下 : `
          })
          noSchedule.style.display = "block"
          bookInfo.style.display = "none"
          bookMiddle.style.display = "none"
          bookBottom.style.display = "none"
          bookTotal.style.display = "none"
          divider[0].style.display = "none"
          divider[1].style.display = "none"
          divider[2].style.display = "none"
          footerExtend.style.display = "block"
        }
        else {
          fetch(
            "/api/user/auth"
          ).then(function (response) {
            return response.json();
          }).then(function (data) {
            topTitle.textContent = `您好，${data["data"]["name"]}，待預訂的行程如下 : `
            scehduledUsername.value = data["data"]["name"]
            scehduledEmail.value = data["data"]["email"]
          })
          bookingName.textContent = `台北一日遊 : ${data["data"]["attraction"]["name"]}`
          scheduledDate.innerHTML = `<span class="item">日期 : </span>${data["data"]["date"]}`
          scheduledPlace.innerHTML = `<span class="item">地點 : </span>${data["data"]["attraction"]["address"]}`
          scheduledImg.style.backgroundImage = `url(${data["data"]["attraction"]["image"]})`

          if (data["data"]["time"] === "afternoon") {
            scheduledTime.innerHTML = `<span class="item">時間 : </span>下午1點到下午5點`
            scheduledFee.innerHTML = `<span class="item">費用 : </span>新台幣2500元`
            totalFee.textContent = "總價 : 新台幣2500元"
          } else if (data["data"]["time"] === "morning") {
            scheduledTime.innerHTML = `<span class="item">時間 : </span>早上8點到中午12點`
            scheduledFee.innerHTML = `<span class="item">費用 : </span>新台幣2000元`
            totalFee.textContent = "總價 : 新台幣2000元"
          }

        }
      })
    }
  })

}




// 刪除行程
bookingDeleteBtn.addEventListener('click', function () {
  deleteSchedule()
})



// 刪除schedule
async function deleteSchedule() {
  let url = "/api/booking"
  let options = {
    method: "DELETE",
  }
  try {
    let response = await fetch(url, options);
    if (response.status === 200) {
      window.location.reload();
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}

