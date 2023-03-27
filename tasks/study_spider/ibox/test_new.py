import execjs

print(execjs.get().name)

js_method = '''
var y = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

function base64ToArrayBufferMock(e) {
    for (var t = function(e) {
        var t = String(e).replace(/=+$/, "")
            , r = "";
        if (t.length % 4 == 1)
            throw new Error('"atob" failed');
        for (var n = 0, i = void 0, o = void 0, a = 0;
             o = t.charAt(a++);
             ~o && (i = n % 4 ? 64 * i + o : o, n++ % 4) ? r += String.fromCharCode(255 & i >> (-2 * n & 6)) : 0)
            o = y.indexOf(o);
        return r
    }(e), r = t.length, n = new Uint8Array(r), i = 0; i < r; i++)
        n[i] = t.charCodeAt(i);
    return n
}
'''
loader = execjs.compile(js_method)


def get_bytes(secret_key):
    result = loader.call('base64ToArrayBufferMock', secret_key)
    print(result)
    arr = []
    for k, v in result.items():
        arr.append(v)
    print(arr)
    secret_key_bytes = bytes(arr)
    return secret_key_bytes


if __name__ == '__main__':
    result = get_bytes("zkXsdQURgkDefISbA6prjw==")
    print(result)
