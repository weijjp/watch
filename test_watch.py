import unittest
from watch import app, db
from watch.models import Movie, User
from watch.commands import forge, initdb

# 定义测试用例，继承unittest.TestCase类
class WatchlTestCase(unittest.TestCase):
################################################################################测试固件
    ###### 测试之前加载测试程序所需要的相关设置
    def setUp(self):
        ### 更新配置：
            # TESTING=True：启动测试模式
            # SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'设为内存型数据库，即把测试的数据存储于内存
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')

        ### 创建数据库和表
        db.create_all()
        # 创建测试数据(一条用户记录)：用户名name='Test', 管理员username='test'
        user = User(name='Test', username='test')
        # 设置管理员登录密码：调用对象user的set_password()方法
        # 该方法将密码'123'转成密码散列值，并把散列值赋给对象的password_hash属性
        user.set_password('123')
        # 创建测试数据(一条电影条目记录)：title='Test Movie Title', year='2019'
        movie = Movie(title='Test Movie Title', year='2019')
        # add_all():将给定的实例集合添加到此会话
        # 将列表[记录user和记录movie]添加到数据库会话
        db.session.add_all([user, movie])
        # 将更新后的会话信息提交给数据库
        db.session.commit()

        ### 测试需要的新属性：
        # 定义一个实例对象属性变量client，创建测试客户端对象，并赋给变量client，者用来模拟客户端请求
        self.client = app.test_client()
        # 定义一个实例对象属性变量runner，创建测试命令运行器对象，并赋给变量runner，用来触发自定义命令
        self.runner = app.test_cli_runner()

    ###### 测试完成后拆卸（删除）测试过程在数据库所形成的记录
    def tearDown(self):
        # 清除数据库会话
        db.session.remove()
        # 删除数据库表
        db.drop_all()

    ##### 为测试创建一个管理员登入的方法
       #  只有执行了这个方法，需要登录才能执行编辑、删除等操作才可以测试
       #  在执行特定方法时，先调用本方法进行模拟登录
    def login(self):
        # 客户端client用post方法访问URL('/login')
            # 用 data 关键字以字典的形式传入请求数据dict(username='test', password='123')
            # follow_redirects=True：可以跟随重定向，最终返回的会是重定向后的响应
        self.client.post('/login', data=dict(username='test', password='123'), follow_redirects=True)

    ###### 测试程序实例是否存在
    def test_app_exist(self):
        # assertIsNotNone(x，[msg])：断言x是否None，不是None则测试用例通过；
        self.assertIsNotNone(app)

    ###### 测试程序是否处于测试模式
    def test_app_is_testing(self):
        # assertTrue(x，[msg])：断言x是否True，是True则测试用例通过；
        self.assertTrue(app.config['TESTING'])

################################################################################测试自定义命令行命令
    ###### 测试初始化数据库函数initdb--报建表
    def test_initdb_command(self):
        # 调用运行器对象的invoke()执行initdb命令，返回的Result对象赋给变量result
        result = self.runner.invoke(initdb)
        # 解析或转换执行结果：
           # result.output：将Result对象输出为unicode字符串, 赋值给变量result_output
        result_output = result.output
        # 自定义断言：'Initialized database.'在 result_output中
        self.assertIn('Initialized database.', result_output)
    ###### 测试初始化数据库函数initdb--删除表
    def test_initdb_drop_command(self):
        result = self.runner.invoke(initdb, '--drop')
        # 相当于 result = self.runner.invoke(args=['initdb', '--drop'])
        self.assertIn('Delete all tables.', result.output)

    ###### 测试创建虚拟数据forge函数
    def test_forge_command(self):
        # 调用运行器对象的invoke()执行forge命令，返回的Result对象赋给变量result
        result = self.runner.invoke(forge)
        # 解析或转换执行结果：
           # result.output：将Result对象输出为unicode字符串, 赋值给变量result_output
        result_output = result.output
           # Movie.query.count()：调用Movie类的子类query的count()方法查询数据的记录，返回查询结果的数量
        Movie_count = Movie.query.count

        # 自定义断言：'Done'在 result.output中
        self.assertIn('Done.', result_output)
        # 自定义断言：Movie.query.count() != 0
        self.assertNotEqual(Movie.query.count(), 0)

################################################################################测试index函数
    ##### 测试通过表单用POST方式创建条目的方法
    def test_create_item(self):
        # 调用、执行上面定义的login()方法，完成管理员登录
        self.login()

        ### 测试创建条目操作
        # 客户端client用post方法访问URL('/')，获得的返回的response对象赋给变量response
            # 用 data 关键字以字典的形式传入请求数据dict(title='New Movie',year='2019')
            # follow_redirects=True：可以跟随重定向，最终返回的会是重定向后的响应
        response = self.client.post('/', data=dict(title='New Movie',year='2019'), follow_redirects=True)
        # 调用get_data(as_text=True)方法，以返回值为字符串的方式读取response对象中的数据，然后赋给变量data
            # as_text=True：将返回值转成字符串
        data = response.get_data(as_text=True)
        # 在app中我们定义了闪现信息flash('Item created.')
        # 自定义断言：'Item created'在 data变量中
        self.assertIn('Item created.', data)
        # 上面我们传入请求数据dict(title='New Movie',year='2019')
        # 自定义断言：'New Movie'在 data变量中
        self.assertIn('New Movie', data)

        ### 测试创建条目操作，但电影标题为空
        # 注释：参考上面
        response = self.client.post('/', data=dict(title='', year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        # 自定义断言：'Item created'不在 data变量中
        self.assertNotIn('Item created.', data)
        # 自定义断言：'Invalid input.'在 data变量中
        self.assertIn('Invalid input.', data)

        ### 测试创建条目操作，但电影年份为空
        # 注释：参考上面
        response = self.client.post('/', data=dict(title='New Movie',year=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    ##### 测试用GET方式访问主页的方法
    def test_index_page(self):
        # 客户端client用get方法访问URL('/'),获得的返回的response对象赋给变量response
        response = self.client.get('/')
        # 调用get_data(as_text=True)方法，以返回值为字符串的方式读取response对象中的数据，然后赋给变量data
            # as_text=True：将返回值转成字符串
        data = response.get_data(as_text=True)
        # 自定义断言：'Test\'s Watchlist'在 data变量中，
        #设置（as_text=True）在转化数据成字符串时，用 \ 用来转义 '
        self.assertIn('Test\'s Watch', data)
        # 上面定义了一个电影条目：movie = Movie(title='Test Movie Title', year='2019')
        # 自定义断言：'Test Movie Title'在 data变量中
        self.assertIn('Test Movie Title', data)
        # 自定义断言：response.status_code==200，即访问成功 （response.status_code--响应状态码）
        self.assertEqual(response.status_code, 200)

################################################################################测试 edit函数
    ###### 测试编辑条目的方法
    def test_edit_item(self):
        # 调用、执行上面定义的login()方法，完成管理员登录
        self.login()

        # 测试GET方法更新页面
        # 客户端client用get方法访问URL('/movie/edit/1'),获得的返回的response对象赋给变量response
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        # 自定义断言：'Edit item'在 data变量中
        self.assertIn('Edit item', data)
        # 上面定义了一个电影条目：movie = Movie(title='Test Movie Title', year='2019')
        # 自定义断言：'Test Movie Title'在 data变量中
        self.assertIn('Test Movie Title', data)
        # 自定义断言：'2019'在 data变量中
        self.assertIn('2019', data)

        # 测试POST方法更新条目操作，注释参考上面
        response = self.client.post('/movie/edit/1', data=dict(title='New Movie Edited',year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated/更新成功.', data)
        self.assertIn('New Movie Edited', data)

        # 测试POST方法更新条目操作，但电影标题为空，注释参考上面
        response = self.client.post('/movie/edit/1', data=dict(title='',year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        # 测试POST方法更新条目操作，但电影年份为空，注释,参考上面
        response = self.client.post('/movie/edit/1', data=dict(title='New Movie Edited Again',year=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input.', data)

################################################################################测试 delete 函数
    def test_delete_item(self):
        # 调用、执行上面定义的login()方法，完成管理员登录
        self.login()
        # 客户端client用post方法访问URL('/movie/delete/1'，这个URL带有参数1)，获得的返回的response对象赋给变量response
            # follow_redirects=True：可以跟随重定向，最终返回的会是重定向后的响应
        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        # 自定义断言：'Item deleted'在 data变量中
        self.assertIn('Item deleted.', data)
        # 自定义断言：'Test Movie Title'不在 data变量中
        self.assertNotIn('Test Movie Title', data)

################################################################################测试 page_not_found 函数
    ###### 自定义测试404页面的方法
    def test_404_page(self):
        # 调用客户端client用get方法以GET方式访问URL('/nothing'，一个无效URL),获得的返回的response对象赋给变量response
        response = self.client.get('/nothing')
        # 调用request对象的get_data(as_text=True)方法，以返回值为字符串的方式读取response对象中的数据，然后赋给变量data
            # as_text=True：将返回值转成字符串
        data = response.get_data(as_text=True)
        # 自定义断言：'Page Not Found - 404'在 data变量中
        self.assertIn('Page Not Found - 404', data)
        # 自定义断言：'Go Back'在 data变量中
        self.assertIn('Go Back', data)
        # 自定义断言：response.status_code==404，即无效RUL访问失败 （response.status_code--响应状态码）
        self.assertEqual(response.status_code, 404)

################################################################################测试 admin 函数
    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'grey', '--password','123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        # Movie.query.count()：调用Movie类的子类query的count()方法查询数据的记录，返回查询结果的数量
        # 自定义断言：Movie.query.count() == 0
        self.assertEqual(User.query.count(), 1)
        # User.query.first()：调用Movie类的子类query的count()方法查询第一条的记录
        # User.query.first().username：第一条记录username键对应的值
        # 自定义断言：User.query.first().username == 'grey'
        self.assertEqual(User.query.first().username, 'grey')
        # app模块中自定义方法：def validate_password(password):
        #                         return check_password_hash(self.password_hash, password)
        # 调用app模块中的validate_password()方法，比对User.query.first()的password_hash与字符串'123'
        # 自定义断言：比对的结果为 True
        self.assertTrue(User.query.first().validate_password('123'))

    # 测试更新管理员账户
    def test_admin_command_update(self):
        # 使用 args 参数给出完整的命令参数列表
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password','456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))

################################################################################测试 login 函数
    ##### 测试登录保护（未登录状态下的返回页面）
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    ##### 测试登录（登录状态下的返回页面）
    def test_login(self):
        response = self.client.post('/login', data=dict(username='test',password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(username='test',password='456'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(username='wrong',password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(username='',password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(username='test',password=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

################################################################################测试 logout 函数
    ##### 测试登出
    def test_logout(self):
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

################################################################################测试 settings 函数
    ##### 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(name='Grey Li',), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('Grey Li', data)

        # 测试更新设置，名称为空
        response = self.client.post('/settings', data=dict(name='',), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)

################################################################################运行测试
if __name__ == '__main__':
    unittest.main()
