# 从 watch 包中导入 db对象
from watch import db
# 从flask_login扩展中导入LoginManager类，UserMixin类, login_user方法，logout_user方法，current_user属性
from flask_login import UserMixin
# 从Flask的依赖Werkzeug的security子模块中导入其内置的用于生成和验证密码散列值的函数
from werkzeug.security import generate_password_hash, check_password_hash

################################################################################创建数据库模型:
# 定义第一个表：User,表名将自动以小写处理生成 user
    # 定义类User，它继承Flask- SQLAlchemy(数据库)的子类db.Model类，flask_login(用户认证)的UserMixin类
class User(db.Model, UserMixin):
    # 用db的Column方法定义数据库的一个列叫id，db.Integer定义id列的数据类型为整型，primary_key=True定义id列为主键
    id = db.Column(db.Integer, primary_key=True)
    # 用db的Column方法定义数据库的一个列叫name，db.String(20)定义name列的数据类型为字符串，最长为20字符
    # 普通用户：只能浏览
    nickname = db.Column(db.String(20))
    # 增加一个管理用户名属性
    # 管理员用户：可能浏览、编辑
    username = db.Column(db.String(20))
    # 增加一个管理用户名的登录密码属性
    password_hash = db.Column(db.String(128))

    # 自定义方法set_password()用来设置密码，接受password作为参数
    def set_password(self, password):
        # 调用werkzeug的generate_password_hash()方法将参数password转成密码散列值
        # 然后把密码散列值赋给User类实例对象的password_hash属性
        self.password_hash = generate_password_hash(password)

    # 自定义validate_password()方法用于验证密码，接受password作为参数
    def validate_password(self, password):
        # 读取User类实例对象的password_hash属性，
        # 然后调用werkzeug的check_password_hash()方法，将password_hash属性与参数password进行比对
        # 返回比对的布尔值，一致返回True,不则是False
        return check_password_hash(self.password_hash, password)

# 定义第二个表：Movie,表名将自动以小写处理生成 movie
    # 定义类User，它继承db.Model类
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 见上面
    title = db.Column(db.String(60))             # 见上面
    year = db.Column(db.String(4))               # 见上面
