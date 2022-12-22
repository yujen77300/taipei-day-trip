// 景點、旅遊日期、時間、建立日期、付款狀態
let tripOrder = document.querySelector('.trip-order')
let tripName = document.querySelector('.trip-name')
let tripDate = document.querySelector('.trip-date')
let tripTime = document.querySelector('.trip-time')
let tripCreated = document.querySelector('.trip-created')
let tripStatus = document.querySelector('.trip-status')
let tbody = document.querySelector('.tbody')
let allOrders = document.querySelector('.all-orders')
let topTitle = document.querySelector('.top-title')
let noSchedule = document.querySelector('.no-schedule')
let memberMiddle = document.querySelector('.member-middle')



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
      fetch(
        "/api/member"
      ).then(function (response) {
        return response.json();
      }).then(function (data) {
        // 如果是空集合代表沒有訂單
        console.log(data)
        console.log(typeof(data))
        topTitle.textContent = `您好，${data["data"]["contact"]["name"]}，目前歷史訂單如下 : `
        if (Object.keys(data["data"]).length === 1) {
          console.log("進來這裡")
          memberMiddle.style.display = "none"
        } else {
          noSchedule.style.display = "none"
          console.log(data["data"])
          allOrders.textContent = `${data["data"]["contact"]["name"]}的台北一日遊歷史訂單`
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
            // tripOrder.textContent = data["data"][`${i}`]["orderNumber"]
            // tripName.textContent = data["data"][`${i}`]["name"]
            // tripDate.textContent = data["data"][`${i}`]["date"]
            // tripTime.textContent = data["data"][`${i}`]["time"]
            // tripCreated.textContent = data["data"][`${i}`]["createdAt"]
            // tripStatus.textContent = data["data"][`${i}`]["status"]
          }

        }

      })
    }
  })

}
