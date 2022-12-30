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
let payBtn = document.getElementById('book-and-pay')
let scehduledPhone = document.getElementById('scehduled-phone')
let bookingFailed = document.querySelector('.booking-failed')
let loading = document.getElementById('load')
let loadingBkgd = document.querySelector('.loading-background')
let contactInfo = {}

// import * as dotenv from '/Users/user/Desktop/selfstudy/WeHelp/Phase2 -Assignment/taipei-day-trip/node_modules/dotenv/'
// import dotenv from 'dotenv'
// import '../../node_modules/dotenv/config.js'
// // const dotenv = require('dotenv')

// console.log("我要開始了唷ㄎㄎ")
// console.log(dotenv.config())
// // console.log("來印出金鑰機密資訊")
// console.log(process.env.APP_KEY)

// require(['/node_modules/require.js/require.js'], function (dotenv) {
//   dotenv.config()
//   console.log("來印出金鑰機密資訊")
//   console.log(process.env.APP_KEY)

// });


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
            contactInfo = data
            topTitle.textContent = `您好，${data["data"]["name"]}，待預訂的行程如下 : `
            scehduledUsername.value = data["data"]["name"]
            scehduledEmail.value = data["data"]["email"]
            // 如果有機號碼有資訊就改，如果沒有顯示placeholder的
            if ((data["data"]["phone"]).length > 0){
              scehduledPhone.value = data["data"]["phone"]
            }
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

// tappay
// 方法一
// window.addEventListener('load', function () {
//   this.window.src = "https://js.tappaysdk.com/sdk/tpdirect/v5.14.0"
// })
// 方法二
const script = document.createElement('script');
script.src = 'https://js.tappaysdk.com/sdk/tpdirect/v5.14.0';
document.body.appendChild(script);
// 不同方法
script.onload = function () {

  TPDirect.setupSDK(`${APP_ID}`, `${APP_KEY}`, 'sandbox')
  TPDirect.card.setup({
    fields: {
      number: {
        element: '.form-control.card-number',
        placeholder: '**** **** **** ****'
      },
      expirationDate: {
        element: document.getElementById('tappay-expiration-date'),
        placeholder: 'MM / YY'
      },
      ccv: {
        element: document.querySelector('.form-control.cvv'),
        placeholder: '後三碼'
      }
    },
    styles: {
      'input': {
        'color': 'gray'
      },
      'input.ccv': {
        // 'font-size': '16px'
      },
      ':focus': {
        'color': 'black'
      },
      '.valid': {
        'color': 'green'
      },
      '.invalid': {
        'color': 'red'
      },
      '@media screen and (max-width: 400px)': {
        'input': {
          'color': 'orange'
        }
      }
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
      beginIndex: 6,
      endIndex: 11
    }
  })

  // listen for TapPay Field
  TPDirect.card.onUpdate(function (update) {
    /* Disable / enable submit button depend on update.canGetPrime  */
    /* ============================================================ */

    // update.canGetPrime === true
    //     --> you can call TPDirect.card.getPrime()
    // const submitButton = document.querySelector('button[type="submit"]')
    if (update.canGetPrime) {
      // submitButton.removeAttribute('disabled')
      console.log("我輸入成功")
    } else {
      console.log("我輸入失敗")
      // submitButton.setAttribute('disabled', true)
    }


    /* Change card image  */
    cardTypes = ['mastercard', 'visa', 'jcb', 'amex', 'unionpay', 'unknown']
    let newType = update.cardType === 'unknown' ? '' : update.cardType
    if (cardTypes.includes(newType)) {
      document.getElementById('cardimg').src = `/picture/${newType}.png`
    }



    /* Change form-group style when tappay field status change */
    /* ======================================================= */
    // if (update.status.number === 2) {
    // console.log('')
    // setNumberFormGroupToError('.card-number-group')
    // } else if (update.status.number === 0) {
    // setNumberFormGroupToSuccess('.card-number-group')
    // console.log('卡號輸入成功了啦')
    // } else {
    // setNumberFormGroupToNormal('.card-number-group')
    // }

    // if (update.status.expiry === 2) {
    //   setNumberFormGroupToError('.expiration-date-group')
    // } else if (update.status.expiry === 0) {
    //   setNumberFormGroupToSuccess('.expiration-date-group')
    // } else {
    //   setNumberFormGroupToNormal('.expiration-date-group')
    // }

    // if (update.status.ccv === 2) {
    //   setNumberFormGroupToError('.ccv-group')
    // } else if (update.status.ccv === 0) {
    //   setNumberFormGroupToSuccess('.ccv-group')
    // } else {
    //   setNumberFormGroupToNormal('.ccv-group')
    // }
  })

  // 監聽點擊按鈕
  payBtn.addEventListener('click', function () {
    // 確認是否可以getprime
    if (TPDirect.card.getTappayFieldsStatus().canGetPrime === false) {
      bookingFailed.textContent = "請輸入正確信用卡資訊"
      return
    } else if (scehduledPhone.value === "") {
      bookingFailed.textContent = "請輸入手機號碼"
      return
    } else {
      // Get prime
      TPDirect.card.getPrime((result) => {
        console.log('成功後的狀態 : ')
        console.log(result)
        if (result.status !== 0) {
          alert('get prime error ' + result.msg)
          return
        } else {
          console.log('成功後取得prime : ')
          console.log(result.card.prime)
          // 成功後將資料給後端
          fetch(
            "/api/booking"
          ).then(function (response) {
            return response.json();
          }).then(function (data) {
            let orderData = {}
            let order = {}
            let contact = {}
            order["price"] = data.data["price"]
            order["trip"] = data.data["attraction"]
            order["date"] = data.data["date"]
            order["time"] = data.data["time"]
            contact["name"] = contactInfo.data["name"]
            contact["email"] = contactInfo.data["email"]
            contact["phone"] = scehduledPhone.value
            order["contact"] = contact
            orderData["prime"] = result.card.prime
            orderData["order"] = order

            console.log("目前的訂單資訊")
            console.log(data)
            console.log("目前帳號資訊")
            console.log(contactInfo)
            console.log("request body")
            console.log(orderData)
            payByPrime(orderData)
            // console.log(order)
            // console.log(contact)

          })
        }
        // send prime to your server, to pay with Pay by Prime API .
        // Pay By Prime Docs: https://docs.tappaysdk.com/tutorial/zh/back.html#pay-by-prime-api
      })
    }
  })


}



async function payByPrime(data) {
  let url = "/api/orders"
  let options = {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-type": "application/json",
    }
  }
  // background = document.createElement('div')
  // background.className = "background"
  // background.style.cssText = 'background-color: rgba(15, 15, 15, 0.25);z-index:1;position:absolute;left:0;right:0;top:0;bottom:0;'
  // body.appendChild(background)
  loading.style.display = "block"
  loadingBkgd.style.display = "block"
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      console.log(result)
      let orderNumber = result["data"]["number"]
      loadThankyou(orderNumber)

      // window.location.reload();
    } else if (response.status === 400) {
      console.log("近來手機號碼這邊")
      console.log(result["message"])
      bookingFailed.textContent = result["message"]
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}

function loadThankyou(orderNumber) {
  document.location.href = '/thankyou'
  sessionStorage.setItem("orderNumber", orderNumber);
}
