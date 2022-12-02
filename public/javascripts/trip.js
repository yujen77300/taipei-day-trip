
let attractionList = document.querySelector('.attraction-list')
let attractionCard = document.querySelector('.attraction-card')
let body = document.querySelector('.body')
let searchingCat = document.querySelector('.searching-cat')
let searchBar = document.querySelector('.search-bar')
let title = document.querySelector('.title')
let noReuslt = document.querySelector('.no-result')



// 是否有載入
let isLoading = 1
// 是否有搜尋
let isSearching = 0
// 類別是否有點擊過
let isSearchingCat = 0

// 點擊searchbar以外的地方會關掉searchingCat
window.onload = function () {

  document.onclick = function (div) {
    // console.log(div.target.className)
    if (div.target.className != "searching-cat" && div.target.className != "search-bar") {
      searchingCat.style.display = "none"
      // searchingCat.style.visibility = "hidden"
    }
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
console.log(lastCard)
console.log(attractionCard)
console.log(attractionList)

// // 使用Intersection observer api
// 當下page的頁數
let page = 0
let footer = document.querySelector(".footer")
console.log(footer)

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
  console.log("這個是搜尋")
  console.log(keyword)
  console.log(typeof (keyword))
  console.log(keyword.length)
  if (keyword.length == 0) {
    zeroIpunt = 0
  }
  let touristSpot = []
  fetchImages(touristSpot, keyword)

}

function getCategory(category) {
  searchBar.value = category
}

// let attraction = document.querySelector('.attraction')
// attraction.addEventListener('click', e => {
//   console.log(e.target)
// })