
网站名称: 中国临床试验注册中心
网站地址: http://www.chictr.org.cn/searchproj.aspx
文件信息: 
	包文件地址 	F:\万方\tasks\task\chictr\chictr_spider_detail.py
	执行文件地址: 	F:\万方\tasks\run_chictr_detail.py
抓取特点:  网站列表页每请求到第4页之后变会不停出现验证码, 后续发现验证码是假的验证码, 对于我们抓取数据毫无影响, 不过我们依然选用遍历urlid的方式进行抓取, 原因是页面上展示的数据仅仅是一部分, 通过urlID我们将获取3倍于网站展示的页面数据, 所以选择遍历ID
抓取思路:
	将抓取到的所有字段数据放入  chictr_all 表中, 同时将要提交的数据经过redis集合对手机号去重后放入到chictr_commit表中, 每次我们提交数据时, 需要在过一遍数据		清洗, 目前代码更新到版本一, 后续持续更新
表结构:
	mongo/wfhy_update/chictr_all 为包含所有字段数据表, 目的是用于数据分析
	mongo/wfhy_commit/chictr_commit 为经过redis对手机号进行去重后要提交的表, 里面含有目标字段以及commit_status字段, commit_status字段用于表示当前的		数据是否已经被提交
	redis/chictr 集合保存所有的用户手机号, 目的是用于做去重处理
非增量抓取:  堆数据
增量抓取设计:
	思路: 根据ID遍历的特点, 找出数据库中存储的最大url_id, 接着找出列表页前三页详情item的最大url_id, 两者比较, 如果页面显示ID大于mongo中id, 即为有数据更新, 以		页面最大id为  end_id, mongo存储最大id为 start_id进行正向遍历获取数据, 这样就可得到增量数据, 过程中以redis集合作为去重的依据将未重复数据依次填写到mongo数据表中
	