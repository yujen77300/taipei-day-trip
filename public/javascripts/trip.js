
let attractionList = document.querySelector('.attraction-list')
let attractionCard = document.querySelector('.attraction-card')
let body = document.querySelector('.body')
let searchingCat = document.querySelector('.searching-cat')
let searchBar = document.querySelector('.search-bar')
let title = document.querySelector('.title')
let noReuslt = document.querySelector('.no-result')
let loginEmail = document.getElementById("login-email")
let loginPassword = document.getElementById("login-password")
let loginFail = document.getElementById("login-fail")
let signupName = document.getElementById("signup-name")
let signupEmail = document.getElementById("signup-email")
let signupPassword = document.getElementById("signup-password")
let signupFail = document.getElementById("signup-fail")
let signupSuccess = document.getElementById("signup-success")
let loginLogout = document.getElementById("login-logout")
// 預定行程
let scheduleBtn = document.getElementById("schedule-btn")

// 假設有沒有顯示loginpopup視窗
let loginPopup = 0
// 是否有載入
let isLoading = 1
// 是否有搜尋
let isSearching = 0
// 類別是否有點擊過
let isSearchingCat = 0

// 點擊searchbar以外的地方會關掉searchingCat，點擊popup以外的要跳出popup
window.onload = function () {

  document.onclick = function (div) {
    // console.log(div.target.className)
    if (div.target.className != "searching-cat" && div.target.className != "search-bar") {
      searchingCat.style.display = "none"
    }
    // console.log(div.target)
    // console.log(div.target.className)
    // let background = document.querySelector('.background')
    // console.log(background)
    // if (typeof (background) != 'undefined' && background != null) {
    //   loginPopup++
    // } else {
    //   if (loginPopup > 0) {
    //     loginPopup++
    //   }
    // }
    // console.log(loginPopup)
    // if (loginPopup > 1) {
    //   console.log("有近來inpopup裡面")
    //   console.log(background)
    //   let popupActive = document.querySelector('.popup.active')
    //   let signupActive = document.querySelector('.signup.active')
    //   // 判斷是在登入視窗(loginpopup)還是註冊視窗(signup)
    //   // 如果在登入視窗(loginpopup)
    //   console.log(signupActive)
    //   console.log(popupActive)
    //   if (typeof (popupActive) != 'undefined' && popupActive != null) {
    //     if (popupActive.contains(div.target)) {
    //     } else {
    //       background.remove()
    //       document.querySelector(".popup").classList.remove("active")
    //       // 有要跳出去Popup，popup才會變成0
    //       loginPopup = 0
    //     }
    //     // 如果在註冊視窗(signup)
    //   }else{
    //     console.log(signupActive)
    //     if (signupActive.contains(div.target)) {
    //     } else {
    //       background.remove()
    //       document.querySelector(".signup").classList.remove("active")
    //       loginPopup = 0
    //     }
    //   }
    // } else {
    //   console.log("沒有近來inpopup裡面")
    // }

  }
}

// 新增一個陣列存放所有旅遊景點的資料
const touristSpot = []

searchBar.addEventListener('click', () => {
  // if條件式判斷只有第一次需要渲染分類區塊
  if (isSearchingCat == 0) {
    let categories = []
    fetch(
      "/api/categories"
    ).then(function (response) {
      return response.json();
    }).then(function (data) {
      categories.push(...data.data)
      // console.log(categories)
      categories.forEach(category => {
        searchingCat.innerHTML += `<div class="categories" onclick="getCategory(this.firstChild.innerHTML)"><div class="cat-text">${category}</div></div>`
      })
      searchingCat.style.display = "flex"
      // console.log(searchingCat)
      // searchingCat.style.visibility = "visible"
      isSearchingCat++
      // categoriesButton.addEventListener('click', () => {
      //   console.log(categoriesButton)
      // })
    })
  } else {
    searchingCat.style.display = "flex"
    console.log(searchingCat)
  }

})

function renderAttractionList(touristSpot, keyword) {
  // 如果有關鍵字的分類要把原有一開始預設有跑出來的刪除
  if (keyword != null && isSearching == 0) {
    attractionList.removeChild(attractionCard)
    console.log(attractionList)
    attractionCard = document.createElement('div')
    attractionCard.className = ".attraction-card"
    attractionCard.style.cssText = 'display:flex;flex-wrap: wrap;justify-content: center;gap:30px';
    attractionList.appendChild(attractionCard)
    console.log(touristSpot)
    touristSpot.forEach(spot => {
      let attraction = document.createElement('div')
      attraction.className = "attraction"
      attraction.setAttribute("onclick", `window.location='/attraction/${spot["id"]}';`)
      // attraction.setAttribute('data-id', `${spot["id"]}`)
      attraction.innerHTML = `
          <div class="attraction-pic" style="background-image: url(${spot["image"][0]});" >
            <div class="name-back">
              <div class="name">${spot['name']}</div>
            </div>
          </div>
          <div class="image-below">
            <div class="mrt">${spot['mrt']}</div>
            <div class="category">${spot['category']}</div>
          </div>
     `
      attractionCard.appendChild(attraction)
      isSearching++
    });
  } else {
    touristSpot.forEach(spot => {
      let attraction = document.createElement('div')
      attraction.className = "attraction"
      // 讓前端可以運用dataset的方法來抓特定景點id
      // attraction.setAttribute('data-id', `${spot["id"]}`)
      attraction.setAttribute("onclick", `window.location='/attraction/${spot["id"]}';`)

      attraction.innerHTML = `
        <div class="attraction-pic" style="background-image: url(${spot["image"][0]});">
          <div class="name-back">
            <div class="name">${spot['name']}</div>
          </div>
        </div>
        <div class="image-below">
          <div class="mrt">${spot['mrt']}</div>
          <div class="category">${spot['category']}</div>
        </div>
   `
      attractionCard.appendChild(attraction)
    });
  }
}

let lastCard = document.querySelector(".last-card")
// console.log(lastCard)
// console.log(attractionCard)
// console.log(attractionList)

// // 使用Intersection observer api
// 當下page的頁數
let page = 0
let footer = document.querySelector(".footer")
// console.log(footer)

// 設定和控制在哪些情況下，呼叫 callback 函式
let options = {
  root: null,   //代表footer會跟我們跟這個root互動
  rootMargin: "0px 0px 0px 0px",
  threshold: 0   // 當重疊到某個百分比時，呼叫我的 callback function 做某件事，背景監控元素的重疊程度，只在你設定的條件發生時呼叫你所提供的 callback
}

// #沒有輸入任何字時候在page=0 和page=1之後會不一樣，用zeroInput來判斷跑幾次了
let zeroIpunt = 0


// 載入圖片的函式
function fetchImages(touristSpot, keyword) {
  // 建立一個存放下一頁的變數
  let nextPage = 0
  let url = ``
  if (keyword != null) {

    // 如果沒有輸入任何字，從原先一開始的資料載入
    if (keyword.length == 0 && zeroIpunt == 0) {
      page = 0
      url = `/api/attractions?page=${page}`
      // 重新變成1才可以繼續載入
      isLoading = 1
      zeroIpunt++
    } else if (keyword.length == 0 && zeroIpunt > 0) {
      url = `/api/attractions?page=${page}`
    } else {
      if (isSearching == 0) {
        page = 0
        // 重新變成1才可以繼續載入
        isLoading = 1
        url = `/api/attractions?page=${page}&keyword=${keyword}`
      } else {
        url = `/api/attractions?page=${page}&keyword=${keyword}`
      }
    }

  } else {
    url = `/api/attractions?page=${page}`
  }
  fetch(
    url
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    nextPage = data["nextpage"]
    touristSpot.push(...data.data)
    //判斷如果沒有搜尋到資料
    if (touristSpot.length === 0) {
      noReuslt.style.display = "flex"
      attractionCard.style.display = "none"
    } else {
      noReuslt.style.display = "none"
      if (nextPage == null) {
        isLoading = 0
      }

      if (keyword != null) {

        renderAttractionList(touristSpot, keyword)
        page = page + 1
      } else {
        console.log(touristSpot)
        renderAttractionList(touristSpot)
        // console.log(page)
        page = page + 1
        // console.log(page)
      }

    }
  })
}
let keyword = null
// 條件達成做什麼：符合設定條件下，目標進入或離開 viewport 時觸發此 callback 函式
let callback = ([entry]) => {
  if (entry && entry.isIntersecting) {
    if (isLoading == 1) {
      let touristSpot = []
      fetchImages(touristSpot, keyword)
    }
  }
}

// 建立一個 intersection observer，帶入相關設定資訊
let observer = new IntersectionObserver(callback, options)

// 設定觀察對象：告訴 observer 要觀察哪個目標元素
observer.observe(footer)


function getAttraction() {
  // 再次搜尋isSearching 改回成0
  isSearching = 0
  let input = document.querySelector(".search-bar")
  keyword = input.value
  // console.log("這個是搜尋")
  // console.log(keyword)
  // console.log(typeof (keyword))
  // console.log(keyword.length)
  if (keyword.length == 0) {
    zeroIpunt = 0
  }
  let touristSpot = []
  fetchImages(touristSpot, keyword)

}

function getCategory(category) {
  searchBar.value = category
}

function login() {
  let loginInputEmail = loginEmail.value
  let loginInputPassword = loginPassword.value
  if (loginInputEmail.length != 0 && loginInputPassword != 0) {
    let loginData = {
      "email": loginInputEmail,
      "password": loginInputPassword
    };
    loginAccount(loginData)
  } else {
    loginFail.textContent = "請輸入帳號與密碼"
  }
}


function signup() {
  let signupInputName = signupName.value
  let signupInputEmail = signupEmail.value
  let signupInputPassword = signupPassword.value
  if (signupInputName.length != 0 && signupInputEmail != 0 && signupInputPassword != 0) {
    if (!emailValidation(signupInputEmail) && !passwordValidation(signupInputPassword)) {
      signupFail.textContent = "密碼與信箱格式錯誤"
      signupEmail.value = ""
      signupPassword.value = ""
    } else if (!emailValidation(signupInputEmail)) {
      signupFail.textContent = "信箱格式錯誤"
      signupEmail.value = ""
    } else if (!passwordValidation(signupInputPassword)) {
      signupFail.textContent = "密碼須包含至少一個數字與一個英文字母"
      signupPassword.value = ""
    } else {
      let signupData = {
        "name": signupInputName,
        "email": signupInputEmail,
        "password": signupInputPassword
      };
      signupAccount(signupData)

    }
  } else {
    signupFail.textContent = "請輸入姓名、電子郵件與密碼"
  }
}

// Regular Expression驗證信箱
function emailValidation(email) {
  if (email.search(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/) != -1) {
    return true
  } else {
    return false
  }
}
// Regular Expression驗證密碼至少包含數字、英文字母
function passwordValidation(password) {
  if (password.search(/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$/) != -1) {
    return true
  } else {
    return false
  }
}


async function signupAccount(data) {
  let url = "/api/user"
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
      signupFail.textContent = ""
      signupSuccess.textContent = "註冊成功請登入系統"
    } else if (response.status === 400) {
      signupFail.textContent = result.message;
      signupName.value = ""
      signupEmail.value = ""
      signupPassword.value = ""
      // return false;
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}


async function loginAccount(data) {
  let url = "/api/user/auth"
  let options = {
    method: "PUT",
    body: JSON.stringify(data),
    headers: {
      "Content-type": "application/json",
    }
  }
  try {
    let response = await fetch(url, options);
    let result = await response.json();
    if (response.status === 200) {
      window.location.reload();
    } else if (response.status === 400) {
      loginFail.textContent = result.message;
      loginEmail.value = ""
      loginPassword.value = ""
    }
  } catch (err) {
    console.log({ "error": err.message });
  }
}

async function deleteAccount() {
  let url = "/api/user/auth"
  let options = {
    method: "DELETE",
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


// popup視窗
document.querySelector("#login-logout").addEventListener("click", function () {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data.data != undefined) {
      deleteAccount()
    } else {
      document.querySelector(".popup").classList.add("active");
      background = document.createElement('div')
      background.className = "background"
      background.style.cssText = 'background-color: rgba(15, 15, 15, 0.25);z-index:1;position:absolute;left:0;right:0;top:0;bottom:0;'
      body.appendChild(background)
      body.style.overflow = "hidden"
    }
  })

});

document
  .querySelector(".popup .close-btn")
  .addEventListener("click", function () {
    loginFail.textContent = ""
    loginEmail.value = ""
    loginPassword.value = ""
    body.style.overflow = "visible"
    document.querySelector(".popup").classList.remove("active");
    background.remove()
  });

document
  .querySelector(".signup .close-btn")
  .addEventListener("click", function () {
    signupFail.textContent = ""
    signupName.value = ""
    signupEmail.value = ""
    signupPassword.value = ""
    body.style.overflow = "visible"
    document.querySelector(".signup").classList.remove("active");
    background.remove()
  });


//到註冊視窗
function tosignup() {
  document.querySelector(".popup").classList.remove("active");
  document.querySelector(".signup").classList.add("active");
  loginFail.textContent = ""
  loginEmail.value = ""
  loginPassword.value = ""

}

// 從註冊到登入視窗
function tologin() {
  document.querySelector(".signup").classList.remove("active");
  document.querySelector(".popup").classList.add("active");
  signupFail.textContent = ""
  signupName.value = ""
  signupEmail.value = ""
  signupPassword.value = ""
}

// 每次載入頁面都要做的驗證
reload()
function reload() {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data.data != undefined) {
      loginLogout.textContent = "登出系統"
    } else {
      loginLogout.textContent = "登入/註冊"
    }
  })
}


// 預定行程相關
document.getElementById("schedule-btn").addEventListener('click', function () {
  fetch(
    "/api/user/auth"
  ).then(function (response) {
    return response.json();
  }).then(function (data) {
    if (data.data != undefined) {
      document.location.href = '/booking'
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