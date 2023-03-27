var y = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

function base64ToArrayBuffer(e){
            for (var t = function(e) {
                var t = String(e).replace(/=+$/, "")
                  , r = "";
                if (t.length % 4 == 1)
                    throw new Error('"atob" failed');
                for (var n = 0, i = void 0, o = void 0, a = 0; o = t.charAt(a++); ~o && (i = n % 4 ? 64 * i + o : o,
                n++ % 4) ? r += String.fromCharCode(255 & i >> (-2 * n & 6)) : 0)
                    o = y.indexOf(o);
                return r
            }(e), r = t.length, n = new Uint8Array(r), i = 0; i < r; i++)
                n[i] = t.charCodeAt(i);
            return n.buffer

}

// data = base64ToArrayBuffer("VbYSxasiGQ/QSslCZ2LfJg==");
// console.log(data);


var y = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
function stringToArrayBuffer(e) {
    for (var t = [], r = 0; r < e.length; r++) {
        var n = e.charCodeAt(r);
        n < 128 ? t.push(n) : n < 2048 ? t.push(192 | n >> 6, 128 | 63 & n) : n < 55296 || n >= 57344 ? t.push(224 | n >> 12, 128 | n >> 6 & 63, 128 | 63 & n) : (r++,
        n = 65536 + ((1023 & n) << 10 | 1023 & e.charCodeAt(r)),
        t.push(240 | n >> 18, 128 | n >> 12 & 63, 128 | n >> 6 & 63, 128 | 63 & n))
    }
    return new Uint8Array(t)
}

// e = '{"method": "GET", "header": [{"key": "x-wx-exclude-credentials", "value": "unionid, cloudbase-access-token, openid"}, {"key": "x-wx-region", "value": "ap-beijing"}, {"key": "x-wx-gateway-id", "value": "gw-1-1g2n1gd143d56b56"}, {"key": "host", "value": "api-h5-tgw.ibox.art"}, {"key": "accept-language", "value": "zh-CN"}, {"key": "ib-device-id", "value": "61cf1eb7576d4c09846ff97fcb394faa"}, {"key": "ib-trans-id", "value": "faec51704a2041c185d9477153f39791"}, {"key": "x-cloudbase-phone", "value": ""}, {"key": "ib-platform-type", "value": "web"}, {"key": "content-type", "value": "application/json"}, {"key": "user-agent", "value": ""}, {"key": "x-wx-env", "value": "ibox-3gldlr1u1a8322d4"}, {"key": "x-wx-call-id", "value": "0.6665500568418836_1664525317354"}, {"key": "x-wx-resource-appid", "value": "wxe77e91c2fdb64e85"}, {"key": "x-wx-container-path", "value": "/nft-mall-web/v1.2/nft/product/getProductDetail?albumId=100514841&gId=105744516"}], "body": "", "call_id": "0.6665500568418836_1664525317354"}'
// medata = stringToArrayBuffer(e);
// console.log(medata);

function get_b(e){
    return new Uint8Array(stringToArrayBuffer(e));
}
// get_b()
// b = g


