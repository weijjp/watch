# 从 watch 包中导入app 对象、db 对象
from watch import app, db
# 从flask大模块中导入Flask类，request对象，render_template方法，url_for方法，redirect方法，flash方法
from flask import render_template, request, url_for, redirect, flash
# 从flask_login扩展中导入LoginManager类，UserMixin类, login_user方法，logout_user方法，current_user属性
from flask_login import login_user, login_required, logout_user, current_user
# 从 watch包的models模块中导入User类 和 Movie类
# 因为我们在__init__.py文件没有导入models模块，所以写成watch.models
from watch.models import User, Movie

############ 数据库操作-------从数据库中读取数据
@app.route('/', methods=['GET', 'POST']) #####版本1.2
def index():
# 第一部分：通过表单创建电影数据库记录
    # 如果是 POST 请求方式
    if request.method == 'POST':
        # 当前用户如果当前用户未认证
            # current_user：当前用户
            # is_authenticated：如果用户经过身份验证，则此属性返回True
        if not current_user.is_authenticated:
            # 重定向到index主页
            return redirect(url_for('index'))
        # 将request对象的表单的title键对应的值，赋给变量title(表单name值所对应的输入字段)
        title = request.form.get('title')
        # 将request对象的表单的year键对应的值，赋给变量year(表单name值所对应的输入字段)
        year = request.form.get('year')
        # 验证数据，即如果数据为空值，或者数据长度超过表格列限制要求
        if not title or not year or len(year) > 4 or len(title) > 60:
            # 在后续的页面闪现：无效输入
            flash('Invalid input.')
            # 重定向返回主页
            return redirect(url_for('index'))
        # 把变量title和变量year分别赋给Movie类的title列和year列，再实例化创建movie对象，即创建一条记录
        movie = Movie(title=title, year=year)
        # 将表格的对象movie(movie记录)添加到数据库会话
        db.session.add(movie)
        # 把数据库会话记录提交到数据库，
        db.session.commit()
        # 消息闪现，显示成功创建的提示
        flash('Item created.')
        return redirect(url_for('index'))
# 第二部分：读取数据库记录
    # 否则（是 GET 请求方式）
    else:
        # # 获取 User 模型的第一个记录，然后赋值给变量 user
        # user = User.query.first()   #  已经通过上下文处理函数处理，此处无需再定义与传值

        # 获取 Movie 模型的所有记录(返回包含多个模型类实例的列表)，然后赋值给变量 movies(记录列表或对象列表)
        movies = Movie.query.all()
        # 消息闪现，显示成功创建的提示
        flash1 ='欢迎光临'
        # 将变量user和movies传HTML文件，渲染后返回该文件
        return render_template('index.html', movies=movies, flash1=flash1)
        # return render_template('index.html', user=user, movies=movies)
                     #  已经通过上下文处理函数处理，此的user=user处无需再传值

################################################################################用表单编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
# 此装饰器将确保在调用实际视图之前登录并验证当前用户
@login_required
def edit(movie_id):
    # 获取 Movie 模型的主键为movie_id的一条记录，然后把这条记录赋值给变量 movie
    # 如果未找到这个主键，则返回404错误响应
    movie = Movie.query.get_or_404(movie_id)
    # 如果以post方式访问
    if request.method == 'POST':
        # 把request对象中表单的'title'键对应的值赋给变量 title
        title = request.form['title']
        # 把request对象中表单的'year'键对应的值赋给变量 year
        year = request.form['year']
        # 如果表单中输入的title和year的值为空值，且长度超过数据库表要求
        if not title or not year or len(year) > 4 or len(title) > 60:
            # 闪现提示信息：无效输入
            flash('Invalid input.')
            # 重定向回edit页面，同时带回RUL参数
            return redirect(url_for('edit', movie_id=movie_id))
        else:
            pass
        # 更新标题:把变量title(表单输入的标题)赋给movie对象的title属性(即记录的title列)
        movie.title = title
        # 更新年份:year(表单输入的年份)赋给movie对象的year属性(即记录的year列)
        movie.year = year
        # 将修改后的会话信息提交给数据库
        db.session.commit()
        # 闪现提示信息：记录更新成功
        flash('Item updated/更新成功.')
        # 重定向回index首页
        return redirect(url_for('index'))
    # 否则（以GET方式访问）
    else:
        # 将上面的变量movie(一条电影记录)传给edit.html模块进行渲染
        # 然后返回渲染后的edit.html，即显示编辑页面
        return render_template('edit.html', movie=movie)

################################################################################用表单删除电影条目
# 限定只接受 POST 请求，也可以接受 GET 请求
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
# 此装饰器将确保在调用实际视图之前登录并验证当前用户
@login_required
def delete(movie_id):
    # 获取 Movie 模型的主键为movie_id的一条记录，然后把这条记录赋值给变量 movie
    # 如果未找到这个主键，则返回404错误响应
    movie = Movie.query.get_or_404(movie_id)
    # 删除会话中对应的记录
    db.session.delete(movie)
    # 将修改后的会话信息提交给数据库
    db.session.commit()
    flash('Item deleted.')
    # 重定向回index首页
    return redirect(url_for('index'))


################################################################################用户登录页面
@app.route('/login', methods=['GET', 'POST'])
# 自定义一个用户登录页面
def login():
    # 如果以post方式访问
    if request.method == 'POST':
        # 读取表单：将request对象的表单的username键对应的值,赋给变量username
        username = request.form['username']
        # 读取表单：将request对象的表单的username键对应的值,赋给变量username
        password = request.form['password']

        # 如果上面表单的输入是个空值
        if not username or not password:
            # 提示：无效输入
            flash('Invalid input.')
            # 重新返回登录页面
            return redirect(url_for('login'))
        # 读取User表格的第一个记录(一个实例)，然后赋值给变量 user
        user = User.query.first()
        # 如果：
             # 变量username(表单输入的值)==user.username(User表格的第一个记录username列对应的值)
             # 并且，调用对象user的自定义validate_password()方法核对password，结果为True
        if username == user.username and user.validate_password(password):
            # 允许该对象登录
            login_user(user)
            # 在后续的页面闪现：登录成功
            flash('Login success.')
            # 重定向到index主页
            return redirect(url_for('index'))
        # 否则：(用户名与密码不正确)
        else:
            # 在后续的页面闪现：无效用户名与密码
            flash('Invalid username or password.')
            # 重定向回登录login页面
            return redirect(url_for('login'))
    # 否则：(以GET方式访问)
    else:
        # 返回login.html内容，即登录的页面
        return render_template('login.html')

################################################################################用户登出页面
@app.route('/logout')
# 该修饰器确保当前用户在调用实际视图之前必须已登录并通过身份验证；
@login_required
def logout():
    # 将用户退出登录
    logout_user()
    # 在后续的页面闪现：再见
    flash('Goodbye.')
    # 重定向回index首页
    return redirect(url_for('index'))

################################################################################设置用户名字
# 设置 name属性，即{{ user.name }}'s Watchlist

@app.route('/settings', methods=['GET', 'POST'])
# 该修饰器确保当前用户在调用实际视图之前必须已登录并通过身份验证；
@login_required
# 自定义用户名称设置函数
def settings():
    # 如果以post方式访问
    if request.method == 'POST':
        # 读取表单：将request对象的表单的name键对应的值,赋给变量name
        name = request.form['name']
        # 如果表单输入为空值，或者输入值长度大于20个字符
        if not name or len(name) > 20:
            # 在后续页面闪现：无效输入
            flash('Invalid input.')
            # 重定向到settings设置页面
            return redirect(url_for('settings'))
        else:
            # 上面50行已完成了注册用户加载回调函数,即已完成Flask-Login的current_user变量的赋值
            # current_user即当前用户代理，将上面变量name(表单输入值)重写当前用户对象的name属性
            current_user.name = name
            # current_user 会返回当前登录用户的数据库记录对象，等同于下面的用法：
            # user = User.query.first()
            # user.name = name

            # 将更新后的会话信息提交给数据库
            db.session.commit()
            # 在后续页面闪现：设置已更新
            flash('Settings updated.')
            # 重定向回index首页
            return redirect(url_for('index'))
    # 否则：(以GET方式访问)
    else:
        # 返回settings设置页面
        return render_template('settings.html')
