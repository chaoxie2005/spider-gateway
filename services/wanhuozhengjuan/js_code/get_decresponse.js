const CryptoJS = require("crypto-js")

function decrypt(e) {
    var t = CryptoJS.enc.Utf8.parse('rewin-swhysc1234')
        , n = CryptoJS.AES.decrypt(e, t, {
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7
        });
    // 返回 base64 而非原文：避免 Windows 下 execjs 用 GBK 读 UTF-8 输出的乱码问题
    return CryptoJS.enc.Base64.stringify(n).toString()
}
