
var y = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
function m(e) {
    for (var t = [], r = 0; r < e.length; r++) {
        var n = e.charCodeAt(r);
        n < 128 ? t.push(n) : n < 2048 ? t.push(192 | n >> 6, 128 | 63 & n) : n < 55296 || n >= 57344 ? t.push(224 | n >> 12, 128 | n >> 6 & 63, 128 | 63 & n) : (r++,
        n = 65536 + ((1023 & n) << 10 | 1023 & e.charCodeAt(r)),
        t.push(240 | n >> 18, 128 | n >> 12 & 63, 128 | n >> 6 & 63, 128 | 63 & n))
    }
    return new Uint8Array(t);
}

function get_b(o,v,g){
    b = new Uint8Array(m(JSON.stringify({
                                    method: "POST",
                                    header: o,
                                    body: v,
                                    call_id: g
                                })).buffer);
    console.log(b);
    return b;
}
var O = [
    {
        "key": "x-wx-exclude-credentials",
        "value": "unionid, cloudbase-access-token, openid"
    },
    {
        "key": "x-wx-region",
        "value": "ap-beijing"
    },
    {
        "key": "x-wx-gateway-id",
        "value": "gw-1-1g2n1gd143d56b56"
    },
    {
        "key": "host",
        "value": "api-h5-tgw.ibox.art"
    },
    {
        "key": "accept-language",
        "value": "zh-CN"
    },
    {
        "key": "ib-device-id",
        "value": "1e3fb1a68efe4ada8b1f700165d93d25"
    },
    {
        "key": "ib-trans-id",
        "value": "4ca9072c9525499684f36c2fbb22a168"
    },
    {
        "key": "x-cloudbase-phone",
        "value": ""
    },
    {
        "key": "ib-platform-type",
        "value": "web"
    },
    {
        "key": "content-type",
        "value": "application/json"
    },
    {
        "key": "user-agent",
        "value": ""
    },
    {
        "key": "x-wx-env",
        "value": "ibox-3gldlr1u1a8322d4"
    },
    {
        "key": "x-wx-call-id",
        "value": "0.8025826435162247_1673407180378"
    },
    {
        "key": "x-wx-resource-appid",
        "value": "wxb5b2c81edbd4cf69"
    },
    {
        "key": "x-wx-container-path",
        "value": "/nft-mall-web/nft/contentList"
    }
]


function s(e) {
    return e instanceof ArrayBuffer
}
function c(e) {
    this.array = e
}

function maxCompressedLength(e) {
    console.log('这是this.array')
    console.log(this.array);
    var e = e.length;
    console.log('这是e: ',)
    return 32 + e + Math.floor(e / 6)
}


function n(e, t) {
        return 506832829 * e >>> t
    }
function i(e, t) {
    return e[t] + (e[t + 1] << 8) + (e[t + 2] << 16) + (e[t + 3] << 24)
}
function o(e, t, r) {
    return e[t] === e[r] && e[t + 1] === e[r + 1] && e[t + 2] === e[r + 2] && e[t + 3] === e[r + 3]
}
function a(e, t, r, n, i) {
    return r <= 60 ? (n[i] = r - 1 << 2,
    i += 1) : r < 256 ? (n[i] = 240,
    n[i + 1] = r - 1,
    i += 2) : (n[i] = 244,
    n[i + 1] = r - 1 & 255,
    n[i + 2] = r - 1 >>> 8,
    i += 3),
    function(e, t, r, n, i) {
        var o;
        for (o = 0; o < i; o++)
            r[n + o] = e[t + o]
    }(e, t, n, i, r),
    i + r
}
function s(e, t, r, n) {
    return n < 12 && r < 2048 ? (e[t] = 1 + (n - 4 << 2) + (r >>> 8 << 5),
    e[t + 1] = 255 & r,
    t + 2) : (e[t] = 2 + (n - 1 << 2),
    e[t + 1] = 255 & r,
    e[t + 2] = r >>> 8,
    t + 3)
}
function u(e, t, r, n) {
    for (; n >= 68; )
        t = s(e, t, r, 64),
        n -= 64;
    return n > 64 && (t = s(e, t, r, 60),
    n -= 60),
    s(e, t, r, n)
}
var l = 14
  , d = new Array(l + 1);
function f(e, t, r, s, f) {
    for (var c = 1; 1 << c <= r && c <= l; )
        c += 1;
    var h = 32 - (c -= 1);
    void 0 === d[c] && (d[c] = new Uint16Array(1 << c));
    var _, p = d[c];
    for (_ = 0; _ < p.length; _++)
        p[_] = 0;
    var E, g, y, m, v, S, A, T, C, w, b = t + r, O = t, I = t, R = !0;
    if (r >= 15)
        for (E = b - 15,
        y = n(i(e, t += 1), h); R; ) {
            S = 32,
            m = t;
            do {
                if (g = y,
                A = S >>> 5,
                S += 1,
                m = (t = m) + A,
                t > E) {
                    R = !1;
                    break
                }
                y = n(i(e, m), h),
                v = O + p[g],
                p[g] = t - O
            } while (!o(e, t, v));
            if (!R)
                break;
            f = a(e, I, t - I, s, f);
            do {
                for (T = t,
                C = 4; t + C < b && e[t + C] === e[v + C]; )
                    C += 1;
                if (t += C,
                f = u(s, f, T - v, C),
                I = t,
                t >= E) {
                    R = !1;
                    break
                }
                p[n(i(e, t - 1), h)] = t - 1 - O,
                v = O + p[w = n(i(e, t), h)],
                p[w] = t - O
            } while (o(e, t, v));
            if (!R)
                break;
            y = n(i(e, t += 1), h)
        }
    return I < b && (f = a(e, I, b - I, s, f)),
    f
}
function compressToBuffer(e) {
    var t, r = this.array, n = r.length, i = 0, o = 0;
    for (o = function(e, t, r) {
        do {
            t[r] = 127 & e,
            (e >>>= 7) > 0 && (t[r] += 128),
            r += 1
        } while (e > 0);
        return r
    }(n, e, o); i < n; )
        o = f(r, i, t = Math.min(n - i, 65536), e, o),
        i += t;
    return o
}


function compress(e) {

    var t = !1
      , n = !1;
    true ? t = !0 : s(e) && (n = !0, e = new Uint8Array(e));

    var i, o, f, d = new c(e), h = maxCompressedLength(e);
    this.array = e;
    console.log('这是H: ',h)

    return t ? (i = new Uint8Array(h),
    f = compressToBuffer(i)) : n ? (i = new ArrayBuffer(h),
    o = new Uint8Array(i),
    f = d.compressToBuffer(o)) : (i = r.alloc(h),
    f = d.compressToBuffer(i)),
    i.slice(0, f)
}

// N = compress(b)
// console.log(N);

function base64ToArrayBuffer(e) {
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

function get_x(key){
    var x = new Uint8Array(base64ToArrayBuffer(key))
    return x;
}

// x = get_x(key)
// console.log('这是x: ',x)
// console.log('这是N: ',N)
// L = D.AES_CBC.encrypt(N, x, void 0, x);

function get_params(key){
    v = 'undefined'
    g = '0.8025826435162247_1673407180378'
    b = get_b(O,v,g);
    console.log(b);
    N = compress(b);
    x = get_x(key);
    return {'x':x,'N':N}
}

// data = get_params(key)
// console.log(data)