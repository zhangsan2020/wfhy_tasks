import execjs

ctl = execjs.compile(open('./toutiao.js','r',encoding='utf-8').read())
sign = ctl.call('get_sign')
print(sign)

# print(sign)

# import PyV8  # 注意大小写
# # with PyV8.JSContext() as ctx:
# #     ctx.eval(""" function add(x, y) { return x + y; } """)
# #     print(ctx.locals.add(1, 2)) #3