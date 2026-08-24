const CryptoJS = require('crypto-js')

function dec_response(enc_data) {
    let key = CryptoJS.enc.Utf8.parse("C8EB5514AF5ADDB94B2207B08C66601C")
    let iv = CryptoJS.enc.Utf8.parse("55DD79C6F04E1A67")
    let cfg = {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    }
    const n = CryptoJS.AES.decrypt(enc_data, key, cfg).toString(CryptoJS.enc.Utf8)
    return n
}

