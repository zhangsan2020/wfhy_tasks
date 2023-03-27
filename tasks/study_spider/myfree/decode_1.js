
var crypto = require('crypto');  //引入crypto模块


location = {
    'host' : 'tools.liumingye.cn',
    'protocol': 'http:',
};

function encode(_0xa6f0d) {
    function md5(message){
    var md5 = crypto.createHash('md5');
    var digest = md5.update(message, 'utf8').digest('hex'); //hex转化为十六进制
    console.log(digest);
    return digest;
}
  function _0x29d94f() {
    if (location.host.indexOf("www.qqyy.com") == -1 && location.host.indexOf("liumingye.cn") == -1 && location.host.indexOf("ubuntu") == -1) {
      location.href = "http://tool.liumingye.cn/music/";
    }
  }

  function _0x38a65a() {
    if (location.protocol.indexOf("http") == -1) {
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

  var _0x116169 = md5(_0x5c5c1c);

  var _0xc8e1be = md5(_0x116169.substr(0, 16));

  var _0x5f48b3 = md5(_0x116169.substr(16, 32));

  var _0x271eea = md5(new Date().getTime()+'').substr(-_0x21ce6c);

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
};

// data = encode('text=晴天 - 周杰伦&page=7&type=migu');
// console.log(data);