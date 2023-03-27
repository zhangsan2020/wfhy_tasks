// const t = [], e = "0123456789abcdef";
// for (let n = 0; n < 36; n++)
//     t[n] = e.substr(Math.floor(16 * Math.random()), 1);
// t[14] = "4",
// t[19] = e.substr(3 & t[19] | 8, 1),
// t[8] = t[13] = t[18] = t[23] = "",
// t.join("")
// // get_device_id();
// console.log(t);
// const util = require('util');
var y = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

function stringToArrayBuffer_data(e) {
    for (var t = [], r = 0; r < e.length; r++) {
        var n = e.charCodeAt(r);
        n < 128 ? t.push(n) : n < 2048 ? t.push(192 | n >> 6, 128 | 63 & n) : n < 55296 || n >= 57344 ? t.push(224 | n >> 12, 128 | n >> 6 & 63, 128 | 63 & n) : (r++,
            n = 65536 + ((1023 & n) << 10 | 1023 & e.charCodeAt(r)),
            t.push(240 | n >> 18, 128 | n >> 12 & 63, 128 | n >> 6 & 63, 128 | 63 & n))
    }
    return new Uint8Array(t).buffer
}

params = '{"method":"GET","header":[{"key":"x-wx-exclude-credentials","value":"unionid, cloudbase-access-token, openid"},{"key":"x-wx-region","value":"ap-beijing"},{"key":"x-wx-gateway-id","value":"gw-1-1g2n1gd143d56b56"},{"key":"host","value":"api-h5-tgw.ibox.art"},{"key":"accept-language","value":"zh-CN"},{"key":"ib-device-id","value":"c96e15a5511b447987456d0156b2526d"},{"key":"ib-trans-id","value":"e6b8e0ea20e84c43851ad4830ebffe5b"},{"key":"x-cloudbase-phone","value":""},{"key":"ib-platform-type","value":"web"},{"key":"content-type","value":"application/json"},{"key":"user-agent","value":""},{"key":"x-wx-env","value":"ibox-3gldlr1u1a8322d4"},{"key":"x-wx-call-id","value":"0.513647608079469_1667542160205"},{"key":"x-wx-resource-appid","value":"wxa2d0710b1323fd96"},{"key":"x-wx-container-path","value":"/nft-mall-web/nft/contentList"}],"body":"undefined","call_id":"0.513647608079469_1667542160205"}'
// data = get_b(params)
// console.log(stringToArrayBuffer_data(params));
function c(e) {
    this.array = e
}

maxCompressedLength = function (e) {
    var l = e.length;
    return 32 + l + Math.floor(l / 6)
}


function compressToBuffer(e) {
    var t, r = this.array, n = r.length, i = 0, o = 0;
    for (o = function (e, t, r) {
        do {
            t[r] = 127 & e,
            (e >>>= 7) > 0 && (t[r] += 128),
                r += 1
        } while (e > 0);
        return r
    }(n, e, o); i < n;)
        o = f(r, i, t = Math.min(n - i, 65536), e, o),
            i += t;
    return o
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
        function (e, t, r, n, i) {
            var o;
            for (o = 0; o < i; o++)
                r[n + o] = e[t + o]
        }(e, t, n, i, r),
    i + r
}

function s(e, t, r, n) {
    return n < 12 && r < 2048 ? (e[t] = 1 + (n - 4 << 2) + (r >>> 8 << 5),
        e[t + 1] = 255 & r, t + 2) : (e[t] = 2 + (n - 1 << 2),
        e[t + 1] = 255 & r,
        e[t + 2] = r >>> 8,
    t + 3)
}

function u(e, t, r, n) {
    for (; n >= 68;)
        console.log('这是要看的')
    console.log(e, t, r, n)
    t = s(e, t, r, 64),
        n -= 64;
    return n > 64 && (t = s(e, t, r, 60),
        n -= 60),
        s(e, t, r, n)
}

function f(e, t, r, s, f) {
    for (var c = 1; 1 << c <= r && c <= l;)
        c += 1;
    var h = 32 - (c -= 1);
    void 0 === d[c] && (d[c] = new Uint16Array(1 << c));
    var _, p = d[c];
    for (_ = 0; _ < p.length; _++)
        p[_] = 0;
    var E, g, y, m, v, S, A, T, C, w, b = t + r, O = t, I = t, R = !0;
    if (r >= 15)
        for (E = b - 15,
                 y = n(i(e, t += 1), h); R;) {
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
                         C = 4; t + C < b && e[t + C] === e[v + C];)
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

function c(e) {
    this.array = e
}

var l = 14
    , d = new Array(l + 1);
c.prototype.maxCompressedLength = function () {
    var e = this.array.length;
    return 32 + e + Math.floor(e / 6)
}
    ,
    c.prototype.compressToBuffer = function (e) {
        var t, r = this.array, n = r.length, i = 0, o = 0;
        for (o = function (e, t, r) {
            do {
                t[r] = 127 & e,
                (e >>>= 7) > 0 && (t[r] += 128),
                    r += 1
            } while (e > 0);
            return r
        }(n, e, o); i < n;)
            console.log('当前要看的')
        console.log(r, i, t, e, o)
        o = f(r, i, t = Math.min(n - i, 65536), e, o),
            i += t;
        return o
    }

function compress(e) {
    this.array = e;
    var t = !1
        , n = !1;
    // a(e) ? t = !0 : s(e) && (n = !0,
    // e = new Uint8Array(e));
    var i, o, f, d = new c(e), h = maxCompressedLength(e);
    // console.log('这是e: ',e);
    i = new Uint8Array(h);
    // console.log('这是i: ',i);
    f = compressToBuffer(i);
    console.log(i.slice(0, f))
    return i.slice(0, f);
}

function get_N(e) {
    var data = new Uint8Array(stringToArrayBuffer_data(e));
    return compress(data);
}

NNN = get_N(params)
console.log('这是get_n的结果: ', NNN)
// console.log(N);
//
function base64ToArrayBuffer(e) {
    for (var t = function (e) {
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

var key = 'K8uNz7Eh8FGHiXzZLeTubg'
var x = new Uint8Array(base64ToArrayBuffer(key));
console.log(x)

// class MMM(e, t){
// u();
class MMM {
    function

    b(e, t, r, s, u, f, c, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        s = s | 0;
        u = u | 0;
        f = f | 0;
        c = c | 0;
        l = l | 0;
        var d = 0
            , h = 0
            , _ = 0
            , p = 0
            , E = 0
            , g = 0
            , y = 0
            , m = 0;
        d = r | 0x400,
            h = r | 0x800,
            _ = r | 0xc00;
        u = u ^ C[(e | 0) >> 2],
            f = f ^ C[(e | 4) >> 2],
            c = c ^ C[(e | 8) >> 2],
            l = l ^ C[(e | 12) >> 2];
        for (m = 16; (m | 0) <= s << 4; m = m + 16 | 0) {
            p = C[(r | u >> 22 & 1020) >> 2] ^ C[(d | f >> 14 & 1020) >> 2] ^ C[(h | c >> 6 & 1020) >> 2] ^ C[(_ | l << 2 & 1020) >> 2] ^ C[(e | m | 0) >> 2],
                E = C[(r | f >> 22 & 1020) >> 2] ^ C[(d | c >> 14 & 1020) >> 2] ^ C[(h | l >> 6 & 1020) >> 2] ^ C[(_ | u << 2 & 1020) >> 2] ^ C[(e | m | 4) >> 2],
                g = C[(r | c >> 22 & 1020) >> 2] ^ C[(d | l >> 14 & 1020) >> 2] ^ C[(h | u >> 6 & 1020) >> 2] ^ C[(_ | f << 2 & 1020) >> 2] ^ C[(e | m | 8) >> 2],
                y = C[(r | l >> 22 & 1020) >> 2] ^ C[(d | u >> 14 & 1020) >> 2] ^ C[(h | f >> 6 & 1020) >> 2] ^ C[(_ | c << 2 & 1020) >> 2] ^ C[(e | m | 12) >> 2];
            u = p,
                f = E,
                c = g,
                l = y
        }
        n = C[(t | u >> 22 & 1020) >> 2] << 24 ^ C[(t | f >> 14 & 1020) >> 2] << 16 ^ C[(t | c >> 6 & 1020) >> 2] << 8 ^ C[(t | l << 2 & 1020) >> 2] ^ C[(e | m | 0) >> 2],
            i = C[(t | f >> 22 & 1020) >> 2] << 24 ^ C[(t | c >> 14 & 1020) >> 2] << 16 ^ C[(t | l >> 6 & 1020) >> 2] << 8 ^ C[(t | u << 2 & 1020) >> 2] ^ C[(e | m | 4) >> 2],
            o = C[(t | c >> 22 & 1020) >> 2] << 24 ^ C[(t | l >> 14 & 1020) >> 2] << 16 ^ C[(t | u >> 6 & 1020) >> 2] << 8 ^ C[(t | f << 2 & 1020) >> 2] ^ C[(e | m | 8) >> 2],
            a = C[(t | l >> 22 & 1020) >> 2] << 24 ^ C[(t | u >> 14 & 1020) >> 2] << 16 ^ C[(t | f >> 6 & 1020) >> 2] << 8 ^ C[(t | c << 2 & 1020) >> 2] ^ C[(e | m | 12) >> 2]
    }

    function

    O(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        b(0x0000, 0x0800, 0x1000, T, e, t, r, n)
    }

    function

    I(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        var o = 0;
        b(0x0400, 0x0c00, 0x2000, T, e, n, r, t);
        o = i,
            i = a,
            a = o
    }

    function

    R(e, t, r, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        l = l | 0;
        b(0x0000, 0x0800, 0x1000, T, s ^ e, u ^ t, f ^ r, c ^ l);
        s = n,
            u = i,
            f = o,
            c = a
    }

    function

    N(e, t, r, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        l = l | 0;
        var d = 0;
        b(0x0400, 0x0c00, 0x2000, T, e, l, r, t);
        d = i,
            i = a,
            a = d;
        n = n ^ s,
            i = i ^ u,
            o = o ^ f,
            a = a ^ c;
        s = e,
            u = t,
            f = r,
            c = l
    }

    function

    D(e, t, r, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        l = l | 0;
        b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
        s = n = n ^ e,
            u = i = i ^ t,
            f = o = o ^ r,
            c = a = a ^ l
    }

    function

    x(e, t, r, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        l = l | 0;
        b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
        n = n ^ e,
            i = i ^ t,
            o = o ^ r,
            a = a ^ l;
        s = e,
            u = t,
            f = r,
            c = l
    }

    function

    L(e, t, r, l) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        l = l | 0;
        b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
        s = n,
            u = i,
            f = o,
            c = a;
        n = n ^ e,
            i = i ^ t,
            o = o ^ r,
            a = a ^ l
    }

    function

    M(e, t, r, s) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        s = s | 0;
        b(0x0000, 0x0800, 0x1000, T, l, d, h, _);
        _ = ~y & _ | y & _ + 1;
        h = ~g & h | g & h + ((_ | 0) == 0);
        d = ~E & d | E & d + ((h | 0) == 0);
        l = ~p & l | p & l + ((d | 0) == 0);
        n = n ^ e;
        i = i ^ t;
        o = o ^ r;
        a = a ^ s
    }

    function

    P(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        var i = 0
            , o = 0
            , a = 0
            , l = 0
            , d = 0
            , h = 0
            , _ = 0
            , p = 0
            , E = 0
            , g = 0;
        e = e ^ s,
            t = t ^ u,
            r = r ^ f,
            n = n ^ c;
        i = m | 0,
            o = v | 0,
            a = S | 0,
            l = A | 0;
        for (; (E | 0) < 128; E = E + 1 | 0) {
            if (i >>> 31) {
                d = d ^ e,
                    h = h ^ t,
                    _ = _ ^ r,
                    p = p ^ n
            }
            i = i << 1 | o >>> 31,
                o = o << 1 | a >>> 31,
                a = a << 1 | l >>> 31,
                l = l << 1;
            g = n & 1;
            n = n >>> 1 | r << 31,
                r = r >>> 1 | t << 31,
                t = t >>> 1 | e << 31,
                e = e >>> 1;
            if (g)
                e = e ^ 0xe1000000
        }
        s = d,
            u = h,
            f = _,
            c = p
    }

    function

    U(e) {
        e = e | 0;
        T = e
    }

    function

    B(e, t, r, s) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        s = s | 0;
        n = e,
            i = t,
            o = r,
            a = s
    }

    function

    k(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        s = e,
            u = t,
            f = r,
            c = n
    }

    function

    G(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        l = e,
            d = t,
            h = r,
            _ = n
    }

    function

    q(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        p = e,
            E = t,
            g = r,
            y = n
    }

    function

    F(e, t, r, n) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        n = n | 0;
        _ = ~y & _ | y & n,
            h = ~g & h | g & r,
            d = ~E & d | E & t,
            l = ~p & l | p & e
    }

    function

    W(e) {
        e = e | 0;
        if (e & 15)
            return -1;
        w[e | 0] = n >>> 24,
            w[e | 1] = n >>> 16 & 255,
            w[e | 2] = n >>> 8 & 255,
            w[e | 3] = n & 255,
            w[e | 4] = i >>> 24,
            w[e | 5] = i >>> 16 & 255,
            w[e | 6] = i >>> 8 & 255,
            w[e | 7] = i & 255,
            w[e | 8] = o >>> 24,
            w[e | 9] = o >>> 16 & 255,
            w[e | 10] = o >>> 8 & 255,
            w[e | 11] = o & 255,
            w[e | 12] = a >>> 24,
            w[e | 13] = a >>> 16 & 255,
            w[e | 14] = a >>> 8 & 255,
            w[e | 15] = a & 255;
        return 16
    }

    function

    j(e) {
        e = e | 0;
        if (e & 15)
            return -1;
        w[e | 0] = s >>> 24,
            w[e | 1] = s >>> 16 & 255,
            w[e | 2] = s >>> 8 & 255,
            w[e | 3] = s & 255,
            w[e | 4] = u >>> 24,
            w[e | 5] = u >>> 16 & 255,
            w[e | 6] = u >>> 8 & 255,
            w[e | 7] = u & 255,
            w[e | 8] = f >>> 24,
            w[e | 9] = f >>> 16 & 255,
            w[e | 10] = f >>> 8 & 255,
            w[e | 11] = f & 255,
            w[e | 12] = c >>> 24,
            w[e | 13] = c >>> 16 & 255,
            w[e | 14] = c >>> 8 & 255,
            w[e | 15] = c & 255;
        return 16
    }

    function

    K() {
        O(0, 0, 0, 0);
        m = n,
            v = i,
            S = o,
            A = a
    }

    function

    // V(e, t) {
    //     if (void 0 === e)
    //         throw new SyntaxError("data required");
    //     if (void 0 === t)
    //         throw new SyntaxError("key required");
    //     return new Y(t).process(e).finish().result
    // }

    function

    H(e, t, r) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        var s = 0;
        if (t & 15)
            return -1;
        while ((r | 0) >= 16) {
            V(w[t | 0] << 24 | w[t | 1] << 16 | w[t | 2] << 8 | w[t | 3], w[t | 4] << 24 | w[t | 5] << 16 | w[t | 6] << 8 | w[t | 7], w[t | 8] << 24 | w[t | 9] << 16 | w[t | 10] << 8 | w[t | 11], w[t | 12] << 24 | w[t | 13] << 16 | w[t | 14] << 8 | w[t | 15]);
            w[t | 0] = n >>> 24,
                w[t | 1] = n >>> 16 & 255,
                w[t | 2] = n >>> 8 & 255,
                w[t | 3] = n & 255,
                w[t | 4] = i >>> 24,
                w[t | 5] = i >>> 16 & 255,
                w[t | 6] = i >>> 8 & 255,
                w[t | 7] = i & 255,
                w[t | 8] = o >>> 24,
                w[t | 9] = o >>> 16 & 255,
                w[t | 10] = o >>> 8 & 255,
                w[t | 11] = o & 255,
                w[t | 12] = a >>> 24,
                w[t | 13] = a >>> 16 & 255,
                w[t | 14] = a >>> 8 & 255,
                w[t | 15] = a & 255;
            s = s + 16 | 0,
                t = t + 16 | 0,
                r = r - 16 | 0
        }
        return s | 0
    }

    function

    Y(e, t, r) {
        e = e | 0;
        t = t | 0;
        r = r | 0;
        var n = 0;
        if (t & 15)
            return -1;
        while ((r | 0) >= 16) {
            J[e & 1](w[t | 0] << 24 | w[t | 1] << 16 | w[t | 2] << 8 | w[t | 3], w[t | 4] << 24 | w[t | 5] << 16 | w[t | 6] << 8 | w[t | 7], w[t | 8] << 24 | w[t | 9] << 16 | w[t | 10] << 8 | w[t | 11], w[t | 12] << 24 | w[t | 13] << 16 | w[t | 14] << 8 | w[t | 15]);
            n = n + 16 | 0,
                t = t + 16 | 0,
                r = r - 16 | 0
        }
        return n | 0
    }
}

// var V = [O, I, R, N, D, x, L, M];
// var J = [R, P];
// return {
//     set_rounds: U,
//     set_state: B,
//     set_iv: k,
//     set_nonce: G,
//     set_mask: q,
//     set_counter: F,
//     get_state: W,
//     get_iv: j,
//     gcm_init: K,
//     cipher: H,
//     mac: Y
// }
// }


function g(e, t, r, n, i) {
    var o = e.length - t
        , a = o < i ? o : i;
    return e.set(r.subarray(n, n + a), t),
        a
}


var HEAP_DATA = 16384;

class CC {
    constructor(e, t, r, n, i) {
        this.nonce = null,
            this.counter = 0,
            this.counterSize = 0,
            this.heap = n.subarray(HEAP_DATA),
            this.asm = i || S(null, this.heap.buffer),
            this.mode = null,
            this.key = null
        // this.AES_reset(e, t, r)
    }

    AES_set_key(e) {
        if (void 0 !== e) {
            var t = e.length;
            if (16 !== t && 24 !== t && 32 !== t)
                throw new m("illegal key size");
            var r = new DataView(e.buffer, e.byteOffset, e.byteLength);
            ff.set_key(t >> 2, r.getUint32(0), r.getUint32(4), r.getUint32(8), r.getUint32(12), t > 16 ? r.getUint32(16) : 0, t > 16 ? r.getUint32(20) : 0, t > 24 ? r.getUint32(24) : 0, t > 24 ? r.getUint32(28) : 0),
                this.key = e
        } else if (!this.key)
            throw new Error("key is required")
    }

    AES_CTR_set_options(e, t, r) {
        if (void 0 !== r) {
            if (r < 8 || r > 48)
                throw new m("illegal counter size");
            this.counterSize = r;
            var n = Math.pow(2, r) - 1;
            this.asm.set_mask(0, 0, n / 4294967296 | 0, 0 | n)
        } else
            this.counterSize = r = 48,
                this.asm.set_mask(0, 0, 65535, 4294967295);
        if (void 0 === e)
            throw new Error("nonce is required");
        if (!_(e))
            throw new TypeError("unexpected nonce type");
        var i = e.length;
        if (!i || i > 16)
            throw new m("illegal nonce size");
        this.nonce = e;
        var o = new DataView(new ArrayBuffer(16));
        if (new Uint8Array(o.buffer).set(e),
            this.asm.set_nonce(o.getUint32(0), o.getUint32(4), o.getUint32(8), o.getUint32(12)),
        void 0 !== t) {
            if (!l(t))
                throw new TypeError("unexpected counter type");
            if (t < 0 || t >= Math.pow(2, r))
                throw new m("illegal counter value");
            this.counter = t,
                this.asm.set_counter(0, 0, t / 4294967296 | 0, 0 | t)
        } else
            this.counter = 0
    }

    AES_set_iv(e) {
        if (void 0 !== e) {
            if (!_(e))
                throw new TypeError("unexpected iv type");
            if (16 !== e.length)
                throw new m("illegal iv size");
            var t = new DataView(e.buffer, e.byteOffset, e.byteLength);
            this.iv = e,
                this.asm.set_iv(t.getUint32(0), t.getUint32(4), t.getUint32(8), t.getUint32(12))
        } else
            this.iv = null,
                this.asm.set_iv(0, 0, 0, 0)
    }

    AES_set_padding(e) {
        this.padding = void 0 === e || !!e
    }

    AES_reset(e, t, r) {
        return this.result = null,
            this.pos = 0,
            this.len = 0,
            this.AES_set_key(e),
            this.AES_set_iv(t),
            this.AES_set_padding(r),
            this
    }

    AES_Encrypt_process(e) {
        for (var t = this.asm, r = this.heap, n = 2, i = 16384, o = this.pos, a = this.len, s = 0, u = e.length || 0, f = 0, c = 0, l = new Uint8Array(a + u & -16); u > 0;)
            a += c = g(r, o + a, e, s, u),
                s += c,
                u -= c,
            (c = MMMM.H(n, i + o, a)) && l.set(r.subarray(o, o + c), f),
                f += c,
                c < a ? (o += c,
                    a -= c) : (o = 0,
                    a = 0);
        return this.result = l,
            this.pos = o,
            this.len = a,
            this
    }

    AES_Encrypt_finish(e) {
        console.log('这是eeee')
        console.log(e);
        var t = null
            , r = 0;
        void 0 !== e && (r = (t = this.AES_Encrypt_process(e).result).length);
        var n = this.asm
            , i = this.heap
            , o = 2
            , a = 16384
            , s = this.pos
            , u = this.len
            , f = 16 - u % 16
            , c = u;
        if (this.hasOwnProperty("padding")) {
            if (this.padding) {
                for (var l = 0; l < f; ++l)
                    i[s + u + l] = f;
                c = u += f
            } else if (u % 16)
                throw new m("data length must be a multiple of the block size")
        } else
            u += f;
        var d = new Uint8Array(r + c);
        return r && d.set(t),
        u && MMMM.H(o, a + s, u),
        c && d.set(i.subarray(s, s + c), r),
            this.result = d,
            this.pos = 0,
            this.len = 0,
            this
    }

    AES_Decrypt_process(e) {
        if (!_(e))
            throw new TypeError("data isn't of expected type");
        var t = this.asm
            , r = this.heap
            , n = S.DEC[this.mode]
            , i = S.HEAP_DATA
            , o = this.pos
            , a = this.len
            , s = 0
            , u = e.length || 0
            , f = 0
            , c = a + u & -16
            , l = 0
            , d = 0;
        this.padding && (c -= l = a + u - c || 16);
        for (var h = new Uint8Array(c); u > 0;)
            a += d = g(r, o + a, e, s, u),
                s += d,
                u -= d,
            (d = t.cipher(n, i + o, a - (u ? 0 : l))) && h.set(r.subarray(o, o + d), f),
                f += d,
                d < a ? (o += d,
                    a -= d) : (o = 0,
                    a = 0);
        return this.result = h,
            this.pos = o,
            this.len = a,
            this
    }

    AES_Decrypt_finish(e) {
        var t = null
            , r = 0;
        void 0 !== e && (r = (t = this.AES_Decrypt_process(e).result).length);
        var n = this.asm
            , i = this.heap
            , o = S.DEC[this.mode]
            , a = S.HEAP_DATA
            , s = this.pos
            , u = this.len
            , f = u;
        if (u > 0) {
            if (u % 16) {
                if (this.hasOwnProperty("padding"))
                    throw new m("data length must be a multiple of the block size");
                u += 16 - u % 16
            }
            if (n.cipher(o, a + s, u),
            this.hasOwnProperty("padding") && this.padding) {
                var c = i[s + f - 1];
                if (c < 1 || c > 16 || c > f)
                    throw new v("bad padding");
                for (var l = 0, d = c; d > 1; d--)
                    l |= c ^ i[s + f - d];
                if (l)
                    throw new v("bad padding");
                f -= c
            }
        }
        var h = new Uint8Array(r + f);
        return r > 0 && h.set(t),
        f > 0 && h.set(i.subarray(s, s + f), r),
            this.result = h,
            this.pos = 0,
            this.len = 0,
            this
    }
};

var w = (() => {
        class e extends CC {
            constructor(e) {
                super(e, arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : null, !(arguments.length > 2 && void 0 !== arguments[2]) || arguments[2], arguments.length > 3 ? arguments[3] : void 0, arguments.length > 4 ? arguments[4] : void 0),
                    this.mode = "CBC",
                    this.BLOCK_SIZE = 16
            }

            encrypt(e) {
                return this.AES_Encrypt_finish(e)
            }

            decrypt(e) {
                return this.AES_Decrypt_finish(e)
            }
        }

        return e;
    }
)();
var W = (()=>{
    class e extends CC {
        constructor(e, t, r) {
            super(e, void 0, !1, t, r),
            this.mode = "ECB",
            this.BLOCK_SIZE = 16
        }
        encrypt(e) {
            return this.AES_Encrypt_finish(e)
        }
        decrypt(e) {
            return this.AES_Decrypt_finish(e)
        }
    }
    return e
    // e.decrypt = Q,
    // e
}
)();
var Y = (()=>{
            class e {
                constructor(e) {
                    this.k = new W(e).encrypt(new Uint8Array(16)).result,
                    H(this.k),
                    this.cbc = new b(e,new Uint8Array(16),!1),
                    this.buffer = new Uint8Array(16),
                    this.bufferLength = 0,
                    this.result = null
                }
                process(e) {
                    if (this.bufferLength + e.length > 16) {
                        this.cbc.process(this.buffer.subarray(0, this.bufferLength));
                        const t = (this.bufferLength + e.length - 1 & -16) - this.bufferLength;
                        this.cbc.process(e.subarray(0, t)),
                        this.buffer.set(e.subarray(t)),
                        this.bufferLength = e.length - t
                    } else
                        this.buffer.set(e, this.bufferLength),
                        this.bufferLength += e.length;
                    return this
                }
                finish() {
                    if (16 !== this.bufferLength) {
                        this.buffer[this.bufferLength] = 128;
                        for (let e = this.bufferLength + 1; e < 16; e++)
                            this.buffer[e] = 0;
                        H(this.k)
                    }
                    for (let e = 0; e < 16; e++)
                        this.buffer[e] ^= this.k[e];
                    return this.result = this.cbc.process(this.buffer).result,
                    this
                }
            }
            return e.bytes = V,
            e
        }
        )();
function V(e, t) {
    if (void 0 === e)
        throw new SyntaxError("data required");
    if (void 0 === t)
        throw new SyntaxError("key required");
    return new Y(t).process(e).finish().result
}
A = new Uint8Array(1048576);
T = {};
var t = new Uint8Array(1048576);
var MMMM = new MMM();
console.log(MMMM.H);

function I(eee, t, r, n) {
    console.log('要看的....')
    console.log(eee)
    return new w(t, n, r, A, T).encrypt(eee).result;
}

// console.log('这是N: ', NNN)
// console.log('这是x: ', x)
//
data = I(NNN, x, void 0, x)
console.log('这是结果!!')
// console.log(data);