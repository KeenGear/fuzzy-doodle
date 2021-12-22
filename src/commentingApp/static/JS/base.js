// const feedElement = document.getElementById("feedid")
// const xhr = new XMLHttpRequest()
// const method = 'GET'
// const url = "/feed"
// const responseType = "json"

// function Like() {
//     return "<button class='btn btn-primary>Like</button>'"
// }

// function formatFeedElement(feed) {
//     var formattedFeed = "<h1>" + feed.id + "</h1>" + "<p>" + feed.content + "</p>"
//     return formattedFeed
// }

// xhr.responseType = responseType
// xhr.open(method, url)
// xhr.onload = function() {
//     const serverResponse = xhr.response
//     var listedItems = serverResponse.response
//     var feedShowStr = ""
//     var i;
//     for (i = 0; i < listedItems.lenght; i++) {
//         var feedObj = listedItems[i]
//         var currentItem = formatFeedElement(feedObj)
//         feedShowStr += currentItem
//     }
//     feedElement.innerHTML = feedShowStr
// }
// xhr.send()