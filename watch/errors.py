# 从 watch 包中导入app 对象
from watch import app
from flask import render_template


################################################################################ 404 错误处理函数
# 当输入错误URL时，会触发404错误
# 注册错误处理函数及定义错误码404，当 404错误发生时，错误处理函数会被触发
@app.errorhandler(404)
# 定义错误处理函数，及接受异常对象作为参数
def page_not_found(e):
    # # 获取 User 模型的第一个记录，然后赋值给变量 user
    # user = User.query.first()  #  已经通过上下文处理函数处理，此处无需再定义与传值

    # 返回渲染后的模板及状态码（这里最好要设定状态码为404，不然屏幕上它将返回202状态码，会误导用户）
    return render_template('errors/404.html'), 404
    # return render_template('404.html', user=user), 404
    #  已经通过上下文处理函数处理，此处的user=user无需再传值

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500
