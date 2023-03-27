var rotateLeft = function(lValue, iShiftBits) {
    return (lValue << iShiftBits) | (lValue >>> (32 - iShiftBits));
}

var addUnsigned = function(lX, lY) {
    var lX4, lY4, lX8, lY8, lResult;
    lX8 = (lX & 0x80000000);
    lY8 = (lY & 0x80000000);
    lX4 = (lX & 0x40000000);
    lY4 = (lY & 0x40000000);
    lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF);
    if (lX4 & lY4) return (lResult ^ 0x80000000 ^ lX8 ^ lY8);
    if (lX4 | lY4) {
        if (lResult & 0x40000000) return (lResult ^ 0xC0000000 ^ lX8 ^ lY8);
        else return (lResult ^ 0x40000000 ^ lX8 ^ lY8);
    } else {
        return (lResult ^ lX8 ^ lY8);
    }
}

var F = function(x, y, z) {
    return (x & y) | ((~x) & z);
}

var G = function(x, y, z) {
    return (x & z) | (y & (~z));
}

var H = function(x, y, z) {
    return (x ^ y ^ z);
}

var I = function(x, y, z) {
    return (y ^ (x | (~z)));
}

var FF = function(a, b, c, d, x, s, ac) {
    a = addUnsigned(a, addUnsigned(addUnsigned(F(b, c, d), x), ac));
    return addUnsigned(rotateLeft(a, s), b);
};

var GG = function(a, b, c, d, x, s, ac) {
    a = addUnsigned(a, addUnsigned(addUnsigned(G(b, c, d), x), ac));
    return addUnsigned(rotateLeft(a, s), b);
};

var HH = function(a, b, c, d, x, s, ac) {
    a = addUnsigned(a, addUnsigned(addUnsigned(H(b, c, d), x), ac));
    return addUnsigned(rotateLeft(a, s), b);
};

var II = function(a, b, c, d, x, s, ac) {
    a = addUnsigned(a, addUnsigned(addUnsigned(I(b, c, d), x), ac));
    return addUnsigned(rotateLeft(a, s), b);
};

var convertToWordArray = function(string) {
    var lWordCount;
    var lMessageLength = string.length;
    var lNumberOfWordsTempOne = lMessageLength + 8;
    var lNumberOfWordsTempTwo = (lNumberOfWordsTempOne - (lNumberOfWordsTempOne % 64)) / 64;
    var lNumberOfWords = (lNumberOfWordsTempTwo + 1) * 16;
    var lWordArray = Array(lNumberOfWords - 1);
    var lBytePosition = 0;
    var lByteCount = 0;
    while (lByteCount < lMessageLength) {
        lWordCount = (lByteCount - (lByteCount % 4)) / 4;
        lBytePosition = (lByteCount % 4) * 8;
        lWordArray[lWordCount] = (lWordArray[lWordCount] | (string.charCodeAt(lByteCount) << lBytePosition));
        lByteCount++;
    }
    lWordCount = (lByteCount - (lByteCount % 4)) / 4;
    lBytePosition = (lByteCount % 4) * 8;
    lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition);
    lWordArray[lNumberOfWords - 2] = lMessageLength << 3;
    lWordArray[lNumberOfWords - 1] = lMessageLength >>> 29;
    return lWordArray;
};

var wordToHex = function(lValue) {
    var WordToHexValue = "",
        WordToHexValueTemp = "",
        lByte, lCount;
    for (lCount = 0; lCount <= 3; lCount++) {
        lByte = (lValue >>> (lCount * 8)) & 255;
        WordToHexValueTemp = "0" + lByte.toString(16);
        WordToHexValue = WordToHexValue + WordToHexValueTemp.substr(WordToHexValueTemp.length - 2, 2);
    }
    return WordToHexValue;
};

var uTF8Encode = function(string) {
    console.log(string);
    string = string.replace(/\x0d\x0a/g, "\x0a");
    var output = "";
    for (var n = 0; n < string.length; n++) {
        var c = string.charCodeAt(n);
        if (c < 128) {
            output += String.fromCharCode(c);
        } else if ((c > 127) && (c < 2048)) {
            output += String.fromCharCode((c >> 6) | 192);
            output += String.fromCharCode((c & 63) | 128);
        } else {
            output += String.fromCharCode((c >> 12) | 224);
            output += String.fromCharCode(((c >> 6) & 63) | 128);
            output += String.fromCharCode((c & 63) | 128);
        }
    }
    return output;
};

function md5(string) {
    var x = Array();
    var k, AA, BB, CC, DD, a, b, c, d;
    var S11 = 7,
        S12 = 12,
        S13 = 17,
        S14 = 22;
    var S21 = 5,
        S22 = 9,
        S23 = 14,
        S24 = 20;
    var S31 = 4,
        S32 = 11,
        S33 = 16,
        S34 = 23;
    var S41 = 6,
        S42 = 10,
        S43 = 15,
        S44 = 21;
    string = string + '';
    console.log('这是string');
    console.log(string);
    string = uTF8Encode(string);
    x = convertToWordArray(string);
    a = 0x67452301;
    b = 0xEFCDAB89;
    c = 0x98BADCFE;
    d = 0x10325476;
    for (k = 0; k < x.length; k += 16) {
        AA = a;
        BB = b;
        CC = c;
        DD = d;
        a = FF(a, b, c, d, x[k + 0], S11, 0xD76AA478);
        d = FF(d, a, b, c, x[k + 1], S12, 0xE8C7B756);
        c = FF(c, d, a, b, x[k + 2], S13, 0x242070DB);
        b = FF(b, c, d, a, x[k + 3], S14, 0xC1BDCEEE);
        a = FF(a, b, c, d, x[k + 4], S11, 0xF57C0FAF);
        d = FF(d, a, b, c, x[k + 5], S12, 0x4787C62A);
        c = FF(c, d, a, b, x[k + 6], S13, 0xA8304613);
        b = FF(b, c, d, a, x[k + 7], S14, 0xFD469501);
        a = FF(a, b, c, d, x[k + 8], S11, 0x698098D8);
        d = FF(d, a, b, c, x[k + 9], S12, 0x8B44F7AF);
        c = FF(c, d, a, b, x[k + 10], S13, 0xFFFF5BB1);
        b = FF(b, c, d, a, x[k + 11], S14, 0x895CD7BE);
        a = FF(a, b, c, d, x[k + 12], S11, 0x6B901122);
        d = FF(d, a, b, c, x[k + 13], S12, 0xFD987193);
        c = FF(c, d, a, b, x[k + 14], S13, 0xA679438E);
        b = FF(b, c, d, a, x[k + 15], S14, 0x49B40821);
        a = GG(a, b, c, d, x[k + 1], S21, 0xF61E2562);
        d = GG(d, a, b, c, x[k + 6], S22, 0xC040B340);
        c = GG(c, d, a, b, x[k + 11], S23, 0x265E5A51);
        b = GG(b, c, d, a, x[k + 0], S24, 0xE9B6C7AA);
        a = GG(a, b, c, d, x[k + 5], S21, 0xD62F105D);
        d = GG(d, a, b, c, x[k + 10], S22, 0x2441453);
        c = GG(c, d, a, b, x[k + 15], S23, 0xD8A1E681);
        b = GG(b, c, d, a, x[k + 4], S24, 0xE7D3FBC8);
        a = GG(a, b, c, d, x[k + 9], S21, 0x21E1CDE6);
        d = GG(d, a, b, c, x[k + 14], S22, 0xC33707D6);
        c = GG(c, d, a, b, x[k + 3], S23, 0xF4D50D87);
        b = GG(b, c, d, a, x[k + 8], S24, 0x455A14ED);
        a = GG(a, b, c, d, x[k + 13], S21, 0xA9E3E905);
        d = GG(d, a, b, c, x[k + 2], S22, 0xFCEFA3F8);
        c = GG(c, d, a, b, x[k + 7], S23, 0x676F02D9);
        b = GG(b, c, d, a, x[k + 12], S24, 0x8D2A4C8A);
        a = HH(a, b, c, d, x[k + 5], S31, 0xFFFA3942);
        d = HH(d, a, b, c, x[k + 8], S32, 0x8771F681);
        c = HH(c, d, a, b, x[k + 11], S33, 0x6D9D6122);
        b = HH(b, c, d, a, x[k + 14], S34, 0xFDE5380C);
        a = HH(a, b, c, d, x[k + 1], S31, 0xA4BEEA44);
        d = HH(d, a, b, c, x[k + 4], S32, 0x4BDECFA9);
        c = HH(c, d, a, b, x[k + 7], S33, 0xF6BB4B60);
        b = HH(b, c, d, a, x[k + 10], S34, 0xBEBFBC70);
        a = HH(a, b, c, d, x[k + 13], S31, 0x289B7EC6);
        d = HH(d, a, b, c, x[k + 0], S32, 0xEAA127FA);
        c = HH(c, d, a, b, x[k + 3], S33, 0xD4EF3085);
        b = HH(b, c, d, a, x[k + 6], S34, 0x4881D05);
        a = HH(a, b, c, d, x[k + 9], S31, 0xD9D4D039);
        d = HH(d, a, b, c, x[k + 12], S32, 0xE6DB99E5);
        c = HH(c, d, a, b, x[k + 15], S33, 0x1FA27CF8);
        b = HH(b, c, d, a, x[k + 2], S34, 0xC4AC5665);
        a = II(a, b, c, d, x[k + 0], S41, 0xF4292244);
        d = II(d, a, b, c, x[k + 7], S42, 0x432AFF97);
        c = II(c, d, a, b, x[k + 14], S43, 0xAB9423A7);
        b = II(b, c, d, a, x[k + 5], S44, 0xFC93A039);
        a = II(a, b, c, d, x[k + 12], S41, 0x655B59C3);
        d = II(d, a, b, c, x[k + 3], S42, 0x8F0CCC92);
        c = II(c, d, a, b, x[k + 10], S43, 0xFFEFF47D);
        b = II(b, c, d, a, x[k + 1], S44, 0x85845DD1);
        a = II(a, b, c, d, x[k + 8], S41, 0x6FA87E4F);
        d = II(d, a, b, c, x[k + 15], S42, 0xFE2CE6E0);
        c = II(c, d, a, b, x[k + 6], S43, 0xA3014314);
        b = II(b, c, d, a, x[k + 13], S44, 0x4E0811A1);
        a = II(a, b, c, d, x[k + 4], S41, 0xF7537E82);
        d = II(d, a, b, c, x[k + 11], S42, 0xBD3AF235);
        c = II(c, d, a, b, x[k + 2], S43, 0x2AD7D2BB);
        b = II(b, c, d, a, x[k + 9], S44, 0xEB86D391);
        a = addUnsigned(a, AA);
        b = addUnsigned(b, BB);
        c = addUnsigned(c, CC);
        d = addUnsigned(d, DD);
    }
    var tempValue = wordToHex(a) + wordToHex(b) + wordToHex(c) + wordToHex(d);
    return tempValue.toLowerCase();
}






function encode(_0xa6f0d) {
    function _0x29d94f() {
        var location = {};
        location.host = 'tools.liumingye.cn'
        if (location.host.indexOf("www.qqyy.com") == -1 && location.host.indexOf("liumingye.cn") == -1 && location.host.indexOf("ubuntu") == -1) {
            location.href = "http://tool.liumingye.cn/music/";
        }
    }

    function _0x38a65a() {
        if ('http:'.indexOf("http") == -1) {
            return String.fromCharCode(65 + Math.ceil(Math.random() * 25));
        } else {
            return "";
        }
    }

    function _0x3f0d0f() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "<Z8B" + _0x3f0d0f + "tBRG" + _0x3f0d0f;
    }

    function _0x690bea() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "6Owh" + _0x3f0d0f + "XG5s" + _0x3f0d0f;
    }

    function _0x73330() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "XbQd" + _0x3f0d0f + "kVw," + _0x3f0d0f;
    }

    function _0x440b81() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "LjH~" + _0x3f0d0f + "z?*k" + _0x3f0d0f;
    }

    function _0x46ed76() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "~lK%" + _0x3f0d0f + "Ly.^" + _0x3f0d0f;
    }

    function _0x1a9fbd() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "2Z)E" + _0x3f0d0f + "jr9:" + _0x3f0d0f;
    }

    function _0x5e0558() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "YS4=" + _0x3f0d0f + "|H?%" + _0x3f0d0f;
    }

    function _0x2a4585() {
        _0x29d94f();

        var _0x3f0d0f = _0x38a65a();

        return _0x3f0d0f + "4[mQ" + _0x3f0d0f + "O/-Z" + _0x3f0d0f;
    }

    var _0x21ce6c = 4;
    var _0x5c5c1c = "";
    var _0x2e950d = [_0x3f0d0f(), _0x690bea(), _0x73330(), _0x440b81(), _0x46ed76(), _0x1a9fbd(), _0x5e0558(), _0x2a4585()];

    for (var _0x46ed76 = 0; _0x46ed76 < _0x2e950d.length; _0x46ed76++) {
        var _0x32c37a = _0x2e950d[_0x46ed76].split("");

        _0x5c5c1c += _0x32c37a.shift();
        _0x5c5c1c += _0x32c37a.pop();
    }
    console.log(_0x5c5c1c);
    var _0x116169 = md5(_0x5c5c1c);

    var _0xc8e1be = md5(_0x116169.substr(0, 16));

    var _0x5f48b3 = md5(_0x116169.substr(16, 32));

    var _0x271eea = md5(new Date().getTime()).substr(-_0x21ce6c);

    var _0x40be14 = _0xc8e1be + md5(_0xc8e1be + _0x271eea);

    var _0x52d62e = _0x40be14.length;

    var _0x2136fc = (new Date().getTime() / 1000 + 86400 >> 0) + md5(_0xa6f0d + _0x5f48b3).substr(0, 16) + _0xa6f0d;

    var _0x1f1a76 = "";

    for (var _0x1dbf2f = 0, _0xdb3d7b = _0x2136fc.length; _0x1dbf2f < _0xdb3d7b; _0x1dbf2f++) {
        var _0x690bea = _0x2136fc.charCodeAt(_0x1dbf2f);

        if (_0x690bea < 128) {
            _0x1f1a76 += String.fromCharCode(_0x690bea);
        } else if (_0x690bea > 127 && _0x690bea < 2048) {
            _0x1f1a76 += String.fromCharCode(_0x690bea >> 6 | 192);
            _0x1f1a76 += String.fromCharCode(_0x690bea & 63 | 128);
        } else {
            _0x1f1a76 += String.fromCharCode(_0x690bea >> 12 | 224);
            _0x1f1a76 += String.fromCharCode(_0x690bea >> 6 & 63 | 128);
            _0x1f1a76 += String.fromCharCode(_0x690bea & 63 | 128);
        }
    }

    var _0x435ba7 = _0x1f1a76.length;
    var _0xacf36b = [];

    for (var _0x46ed76 = 0; _0x46ed76 <= 255; _0x46ed76++) {
        _0xacf36b[_0x46ed76] = _0x40be14[_0x46ed76 % _0x52d62e].charCodeAt();
    }

    var _0x36be3d = [];

    for (var _0x46ed76 = 0; _0x46ed76 < 256; _0x46ed76++) {
        _0x36be3d.push(_0x46ed76);
    }

    for (var _0x54d439 = 0, _0x46ed76 = 0; _0x46ed76 < 256; _0x46ed76++) {
        _0x54d439 = (_0x54d439 + _0x36be3d[_0x46ed76] + _0xacf36b[_0x46ed76]) % 256;
        var _0x455821 = _0x36be3d[_0x46ed76];
        _0x36be3d[_0x46ed76] = _0x36be3d[_0x54d439];
        _0x36be3d[_0x54d439] = _0x455821;
    }

    var _0x3831d9 = "";

    for (var _0x3f0d0f = 0, _0x54d439 = 0, _0x46ed76 = 0; _0x46ed76 < _0x435ba7; _0x46ed76++) {
        _0x3f0d0f = (_0x3f0d0f + 1) % 256;
        _0x54d439 = (_0x54d439 + _0x36be3d[_0x3f0d0f]) % 256;
        var _0x455821 = _0x36be3d[_0x3f0d0f];
        _0x36be3d[_0x3f0d0f] = _0x36be3d[_0x54d439];
        _0x36be3d[_0x54d439] = _0x455821;
        _0x3831d9 += String.fromCharCode(_0x1f1a76[_0x46ed76].charCodeAt() ^ _0x36be3d[(_0x36be3d[_0x3f0d0f] + _0x36be3d[_0x54d439]) % 256]);
    }

    var _0x2a3493 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    for (var _0x6e4567, _0x3cae6e, _0x1e757f = 0, _0x34e10f = _0x2a3493, _0x2757aa = ""; _0x3831d9.charAt(_0x1e757f | 0) || (_0x34e10f = "=", _0x1e757f % 1); _0x2757aa += _0x34e10f.charAt(63 & _0x6e4567 >> 8 - _0x1e757f % 1 * 8)) {
        _0x3cae6e = _0x3831d9.charCodeAt(_0x1e757f += 0.75);
        _0x6e4567 = _0x6e4567 << 8 | _0x3cae6e;
    }

    _0x3831d9 = (_0x271eea + _0x2757aa.replace(/=/g, "")).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, ".");
    return "data=" + _0x3831d9 + "&v=2";
}

data = encode('text=周杰伦&page=1&type=migu');
console.log('最后结果为: ',data);
