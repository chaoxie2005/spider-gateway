const cryptoJs = require("crypto-js")

let url = "/api/author/search"
function decryptAES(text) {
    try {
        const str = function (str) {
            const encode2 = encodeURI(str);
            return btoa(encode2)
        }(url).repeat(3)
            , orgKey = str.slice(0, 16)
            , orgIv = str.slice(12, 28)
            , ikey = cryptoJs.enc.Utf8.parse(orgKey)
            , iiv = cryptoJs.enc.Utf8.parse(orgIv);
        result = cryptoJs.AES.decrypt(text, ikey, {
            iv: iiv,
            mode: cryptoJs.mode.CBC,
            padding: cryptoJs.pad.Pkcs7
        })
        return cryptoJs.enc.Base64.stringify(result)
    } catch (e) {
        return "JS_AES_ERROR:" + e.toString();
}
}


module.exports = {
    decryptAES
};