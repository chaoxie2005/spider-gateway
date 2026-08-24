const CryptoJS = require('crypto-js')
const JSEncrypt = require('node-jsencrypt')
options = {
    "url": "https://api.birdreport.cn/front/record/activity/search",
    "type": "POST",
    "isLocal": false,
    "global": true,
    "processData": true,
    "async": true,
    "contentType": "application/x-www-form-urlencoded; charset=UTF-8",
    "accepts": {
        "*": "*/*",
        "text": "text/plain",
        "html": "text/html",
        "xml": "application/xml, text/xml",
        "json": "application/json, text/javascript",
        "script": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript"
    },
    "contents": {
        "xml": {},
        "html": {},
        "json": {},
        "script": {}
    },
    "responseFields": {
        "xml": "responseXML",
        "text": "responseText",
        "json": "responseJSON"
    },
    "converters": {
        "text html": true
    },
    "flatOptions": {
        "url": true,
        "context": true
    },
    "jsonp": "callback",
    "data": "CuHoRfX7ymdxMUQpvXws+b/98d4dvgVv4hKIyx39iIIm2qOYA1t6achxp3zGWlrWCU3484xDK5TgGFBa3iwe/wG1RS+rVAQTXQm/YDji/RoK6wZvf995CEOaN605ecdWEpme0laClyXckKZ6xzMBACzQbDf8YgOCB+D1FNelews=",
    "dataType": "json",
    "headers": {},
    "dataTypes": [
        "json"
    ],
    "crossDomain": true,
    "hasContent": true
}

function getUuid() {
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 32; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 16), 1)
    }
    s[14] = "4";
    s[19] = hexDigits.substr(s[19] & 3 | 8, 1);
    s[8] = s[13] = s[18] = s[23];
    var uuid = s.join("");
    return uuid
}

function sort_ASCII(obj) {
    var arr = new Array;
    var num = 0;
    for (var i in obj) {
        arr[num] = i;
        num++
    }
    var sortArr = arr.sort();
    var sortObj = {};
    for (var i in sortArr) {
        sortObj[sortArr[i]] = obj[sortArr[i]]
    }
    return sortObj
}

function dataTojson(data) {
    var arr = [];
    var res = {};
    arr = data.split("&");
    for (var i = 0; i < arr.length; i++) {
        if (arr[i].indexOf("=") != -1) {
            var str = arr[i].split("=");
            if (str.length == 2) {
                res[str[0]] = str[1]
            } else {
                res[str[0]] = ""
            }
        } else {
            res[arr[i]] = ""
        }
    }
    return res
}
function get_sign(data) {
    var paramPublicKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvxXa98E1uWXnBzXkS2yHUfnBM6n3PCwLdfIox03T91joBvjtoDqiQ5x3tTOfpHs3LtiqMMEafls6b0YWtgB1dse1W5m+FpeusVkCOkQxB4SZDH6tuerIknnmB/Hsq5wgEkIvO5Pff9biig6AyoAkdWpSek/1/B7zYIepYY0lxKQIDAQAB";
    var encrypt = new JSEncrypt;
    encrypt.setPublicKey(paramPublicKey);
    let json_data = JSON.stringify(data)
    var timestamp = Date.parse(new Date);
    var requestId = getUuid();
    let post_data = encrypt.encrypt(json_data);
    let data_concat = json_data + requestId + timestamp
    var sign = CryptoJS.MD5(`${data_concat}`).toString();
    return [sign, requestId, timestamp, post_data]
}


