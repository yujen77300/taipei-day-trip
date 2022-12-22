let afternoonSection = document.querySelector('.afternoon-section')
let morningSection = document.querySelector('.morning-section')
let slides = document.querySelector('.slides')
let slide = document.querySelector('.slide')
let fee = document.querySelector('.fee')
let controlsVisible = document.querySelector('.controls-visible')
let firstSlide = document.querySelector('#firstSlide')
let bookingButton = document.querySelector('.booking-button')
let tripDate = document.getElementById("trip-date")
let bookingFail = document.getElementById('booking-fail')
// 取得id的資料
let id = window.location.href.split("/").slice(-1)[0]
const url = "/api/attraction/" + id;
// 圖片的預設位置
let imgIndex = 0
//圖片按鈕是向右
let isRight = 1

let allImage = []
let controlButton = []



fetch(
  url
).then(function (response) {
  return response.json();
}).then(function (data) {
  let category = data.data["category"]
  let mrt = data.data["mrt"]
  document.querySelector('.name').innerHTML = data.data["name"]
  document.querySelector('.cat-location').innerHTML = `${category} at ${mrt}`
  document.querySelector('.description').innerHTML = data.data["description"]
  document.querySelector('.address').innerHTML = data.data["address"]
  document.querySelector('.transportation').innerHTML = data.data["transport"]
  // 圖片陣列
  let img = data.data["image"]
  let imgAmount = img.length
  // 像左移動距離
  let leftMove = 0
  slide.style.backgroundImage = `url(${img[0]})`
  for (let i = 1; i < imgAmount; i++) {
    // 先新增圖片slide張數
    leftMove = i * 100
    slide = document.createElement('div')
    slide.className = "slide"
    slide.style.cssText = `background-image:url(${img[i]});left:${leftMove}%`
    slides.insertBefore(slide, controlsVisible)
    //新增圖片的下排按鈕
    label = document.createElement('label')
    label.setAttribute('for', `control-${i + 1}`)
    label.setAttribute('class', "control-button")
    controlsVisible.appendChild(label)
    // 新增圖片被隱藏按鈕
    input = document.createElement('input')
    input.setAttribute("name", "control")
    input.setAttribute("type", "radio")
    input.setAttribute("id", `control-${i + 1}`)
    slides.insertBefore(input, firstSlide)
  }
  allImage = document.querySelectorAll('.slide');
  controlButton = document.querySelectorAll('.control-button')
})


// 選擇上半天下半天方案的監聽器
afternoonSection.addEventListener('click', () => {
  if (afternoonSection.firstElementChild.classList.contains('clicked')) {

  } else {
    // toggle => 有class就會刪除，沒有class就會增加
    afternoonSection.firstElementChild.classList.toggle("clicked")
    morningSection.firstElementChild.classList.toggle("clicked")
    fee.innerHTML = "新台幣2500元"
  }

})

morningSection.addEventListener('click', () => {
  if (morningSection.firstElementChild.classList.contains('clicked')) {

  } else {
    afternoonSection.firstElementChild.classList.toggle("clicked")
    morningSection.firstElementChild.classList.toggle("clicked")
    fee.innerHTML = "新台幣2000元"
  }
})





// 圖片輪播開始

function refresh(index, direction) {

  // 向右邊
  if (direction == 1) {
    let leftMove = (index + 1) * 100
    for (var i = 0; i < allImage.length; i++) {
      allImage[i].style.transform = `translatex(-${leftMove}%)`
    }
    controlButton[index].style.backgroundColor = "#fff"
    controlButton[index + 1].style.backgroundColor = "#000"
    // 向左邊
  } else {
    let leftMove = (index - 1) * 100
    for (var i = 0; i < allImage.length; i++) {
      allImage[i].style.transform = `translatex(-${leftMove}%)`
    }
    controlButton[index].style.backgroundColor = "#fff"
    controlButton[index - 1].style.backgroundColor = "#000"
  }

}

function leftShift() {
  if (imgIndex == 0) {
    for (var i = 0; i < allImage.length; i++) {
      allImage[i].style.transform = `translatex(-${(allImage.length - 1) * 100}%)`
    }
    // 處理黑色圈圈
    controlButton[0].style.backgroundColor = "#fff"
    controlButton[allImage.length - 1].style.backgroundColor = "#000"
    imgIndex = allImage.length - 1
  } else {
    isRight = 0
    refresh(imgIndex, isRight)
    imgIndex--
  }

}

function rightShift() {
  if (imgIndex + 1 >= allImage.length) {
    for (var i = 0; i < allImage.length; i++) {
      allImage[i].style.transform = "translatex(0%)"
    }
    // 處理黑色圈圈
    controlButton[allImage.length - 1].style.backgroundColor = "#fff"
    controlButton[0].style.backgroundColor = "#000"
    imgIndex = 0
  } else {
    isRight = 1
    refresh(imgIndex, isRight)
    imgIndex++
  }
}


// 預訂行程
bookingButton.addEventListener('click', function () {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data.data != undefined) {
      // 如果驗證的api有存在資料就跳到預訂行程
      newBookingData = {}
      newBookingData["attractionId"] = id
      newBookingData["date"] = tripDate.value
      if (parseInt((fee.textContent).substr(3, 4), 0) == 2500) {
        newBookingData["time"] = "afternoon"
      } else {
        newBookingData["time"] = "morning"
      }
      newBookingData["price"] = parseInt((fee.textContent).substr(3, 4), 0)
      bookNewSchedule(newBookingData)

    } else {
      document.querySelector(".popup").classList.add("active");
      background = document.createElement('div')
      background.className = "background"
      background.style.cssText = 'background-color: rgba(15, 15, 15, 0.25);z-index:1;position:absolute;left:0;right:0;top:0;bottom:0;'
      body.appendChild(background)
      body.style.overflow = "hidden"
    }
  })
})



async function bookNewSchedule(data) {
  let url = "/api/booking"
  let options = {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-type": "application/json",
    }
  }
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      console.log("成功新增")
      document.location.href = '/booking'
    } else if (response.status === 400) {
      console.log(result["message"])
      bookingFail.textContent = result["message"]
      bookingFail.style.marginTop = "10px"
      bookingButton.style.marginTop = "10px"
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}