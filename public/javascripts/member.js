// 景點、旅遊日期、時間、建立日期、付款狀態
let tripOrder = document.querySelector('.trip-order')
let tripName = document.querySelector('.trip-name')
let tripDate = document.querySelector('.trip-date')
let tripTime = document.querySelector('.trip-time')
let tripCreated = document.querySelector('.trip-created')
let tripStatus = document.querySelector('.trip-status')
let tbody = document.querySelector('.tbody')
let noSchedule = document.querySelector('.no-schedule')
let memberMiddle = document.querySelector('.member-middle')
const avatorUploadBtn = document.querySelector('.avator-upload-button')
const hiddenInput = document.querySelector('.avator-upload-input')
const avator = document.querySelector('.avator')
const usernameInfo = document.querySelector('.username-info')
const leftBarUsername = document.querySelector('.left-bar-username')
const infoEditBtn = document.querySelector('.info-edit-btn')
const emailInputBox = document.querySelector('.email-input-box')
const phoneInputBox = document.querySelector('.phone-input-box')
const pwdEditBtn = document.querySelector('.pwd-edit-btn')
const oldPwdBox = document.querySelector('.old-pwd-box')
const newPwdBox = document.querySelector('.new-pwd-box')
const repeatPwdBox = document.querySelector('.repeat-pwd-box')
const pwdHint = document.querySelector('.pwd-hint')
const infoRightBody = document.querySelector('.info-right-body')
const pwdRightBody = document.querySelector('.pwd-right-body')
const listRightBody = document.querySelector('.list-right-body')
const myInfo = document.getElementById('my-info')
const updatePwd = document.getElementById('update-pwd')
const shoppingList = document.getElementById('shopping-list')


let avatorUrl = ''
let avatorName = ''
let shoppingListClick = 0



renderMember()
function renderMember() {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data["error"] === true) {
      document.location.href = '/'
    } else {
      usernameInfo.textContent = data.data["name"]
      leftBarUsername.textContent = data.data["name"]
      emailInputBox.value = data.data["email"]
      // 如果有下過訂單(代表有電話號碼)
      if ((data["data"]["phone"]).length > 0) {
        phoneInputBox.value = data["data"]["phone"]
      }
      // 如果有更改過大頭貼
      if ((data["data"]["avatorName"]) !== "user.png") {
        avator.style.backgroundImage = `url("${data["data"]["avatorUrl"]}")`
      }
      avatorUrl = data["data"]["avatorUrl"]
      avatorName = data["data"]["avatorName"]
    }
  })

}
function renderAllList() {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data["error"] === true) {
      document.location.href = '/'
    } else {
      fetch(
        "/api/user/order"
      ).then(function (response) {
        return response.json();
      }).then(function (data) {
        // 如果是空集合代表沒有訂單
        console.log(data)
        console.log(typeof (data))
        if (Object.keys(data["data"]).length === 1) {
          console.log("進來這裡")
          memberMiddle.style.display = "none"
        } else {
          noSchedule.style.display = "none"
          console.log(data["data"])
          console.log(Object.keys(data["data"]).length)
          tripOrder.textContent = data["data"]["1"]["orderNumber"]
          tripName.textContent = data["data"]["1"]["name"]
          tripDate.textContent = data["data"]["1"]["date"]
          tripTime.textContent = data["data"]["1"]["time"]
          tripCreated.textContent = data["data"]["1"]["createdAt"]
          tripStatus.textContent = data["data"]["1"]["status"]

          // 第一列是一開始就畫好，所以要減一
          for (let i = 2; i < Object.keys(data["data"]).length; i++) {
            console.log(i)
            newTableRow = document.createElement('tr')
            newTableRow.innerHTML = `
            <td class="trip-order${i}" style="padding: 5px;">The table body</td>
            <td class="trip-name${i}" style="padding: 5px;">with two columns</td>
            <td class="trip-date${i}" style="padding: 5px;">with two columns</td>
            <td class="trip-time${i}" style="padding: 5px;">with two columns</td>
            <td class="trip-created${i}" style="padding: 5px;">with two columns</td>
            <td class="trip-status${i}" style="padding: 5px;">with two columns</td>
          `
            tbody.appendChild(newTableRow)
            document.querySelector(`.trip-order${i}`).textContent = data["data"][`${i}`]["orderNumber"]
            document.querySelector(`.trip-name${i}`).textContent = data["data"][`${i}`]["name"]
            document.querySelector(`.trip-date${i}`).textContent = data["data"][`${i}`]["date"]
            document.querySelector(`.trip-time${i}`).textContent = data["data"][`${i}`]["time"]
            document.querySelector(`.trip-created${i}`).textContent = data["data"][`${i}`]["createdAt"]
            document.querySelector(`.trip-status${i}`).textContent = data["data"][`${i}`]["status"]
          }

        }

      })
    }
  })

}


avatorUploadBtn.addEventListener('click', function () {
  hiddenInput.click()
  hiddenInput.addEventListener('change', function (e) {
    let form = new FormData();
    form.append('form', e.target.files[0])
    uploadImage(form)
  })
})


infoEditBtn.addEventListener('click', function () {
  // let editData = {}
  // let allEditData ={}
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    let editData = {
      "userId": data['data']["id"],
      "userName": data['data']["name"],
      "email": emailInputBox.value,
      "phone": phoneInputBox.value,
      "avatorUrl": avatorUrl,
      "avatorName": avatorName,

    }

    editInfo(editData)

  })

})

pwdEditBtn.addEventListener('click', function (e) {
  // 現在的密碼到後端驗證
  if (oldPwdBox.value != '') {
    if (passwordValidation(newPwdBox.value)) {
      if (newPwdBox.value == repeatPwdBox.value) {

        let pwdData = {
          "oldPwd": oldPwdBox.value,
          "newPwd": newPwdBox.value,
          "repeatPwd": repeatPwdBox.value
        }
        editPwd(pwdData)
      } else {
        pwdHint.textContent = "新的密碼與確認密碼不一致"
      }
    } else {
      pwdHint.textContent = "密碼至少4位數，且包含至少一個數字與一個英文字母"
    }
  } else {
    pwdHint.textContent = "請輸入現在的密碼"
  }

})



myInfo.addEventListener('click', function () {
  // shoppingListClick = 0
  infoRightBody.style.display = "flex"
  pwdRightBody.style.display = "none"
  listRightBody.style.display = "none"
})

updatePwd.addEventListener('click', function () {
  // shoppingListClick = 0
  infoRightBody.style.display = "none"
  pwdRightBody.style.display = "block"
  listRightBody.style.display = "none"
})

shoppingList.addEventListener('click', function () {
  infoRightBody.style.display = "none"
  pwdRightBody.style.display = "none"
  listRightBody.style.display = "block"
  if (shoppingListClick === 0) {
    console.log("近來")
    renderAllList()
  }
  shoppingListClick++
})





function passwordValidation(password) {
  if (password.search(/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$/) != -1) {
    return true
  } else {
    return false
  }
}




async function uploadImage(form) {
  let url = "/api/upload/avator"
  let options = {
    body: form,
    method: "POST",
  }
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      avator.style.backgroundImage = `url('${result.data["avatorUrl"]}')`
      avatorName = result.data["fileName"]
      avatorUrl = result.data["avatorUrl"]
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}


async function editInfo(editData) {
  let url = "/api/edit/info"
  let options = {
    body: JSON.stringify(editData),
    method: "PATCH",
    headers: {
      "Content-type": "application/json",
    }
  }
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      window.location.reload();
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}

async function editPwd(pwdData) {
  let url = "/api/edit/password"
  let options = {
    body: JSON.stringify(pwdData),
    method: "PATCH",
    headers: {
      "Content-type": "application/json",
    }
  }
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      pwdHint.textContent = "更新成功下次請使用新密碼登入系統"
      // window.location.reload();
    } else if (response.status === 400) {
      pwdHint.textContent = result["message"]
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}