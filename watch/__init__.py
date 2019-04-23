# 导入os, sys模块，本实例中需要将数据库创建在项目的根目录下，使用python内置os库可以很方便的定位到项目路径
import os, sys
# 导入Flask的依赖clink
import click
# 从flask大模块中导入Flask类
from flask import Flask
# 从flask-sqlchemy扩展中将其内置的SQLAlchemy类引用到本程序下
from flask_sqlalchemy import SQLAlchemy
# 从flask_login扩展中导入LoginManager类
from flask_login import LoginManager

# 给Flask类传值__name__或者字符串"__main__"，将为本程序创建一个Flask类实例对象app
app = Flask(__name__)

################################################################################设置数据库URI及其它环境变量:
# 判断当前运行的操作系统
   # sys.platform: 获取当前系统平台，结果 win32
   # str.startswith('win'):判断字符串是否以 win开头，是返回True，否则返回 Fals
WIN = sys.platform.startswith('win')
# 如果 WIN = True，即是Windows系统，使用三个斜线，这个是sqlite的规则
if WIN:
    prefix = 'sqlite:///'
# 否则，使用四个斜线
else:
    prefix = 'sqlite:////'

# 在扩展类实例化前加载配置
# 定义数据库的 URI
  # os.path.join(path,name):连接目录与文件名或目录
  # app.root_path：返回程序实例所在模块的路径（目前来说，即项目根目录），
  #配置键SQLALCHEMY_DATABASE_URI：用于连接数据的数据库路径及名称
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
# os.getenv()获取一个环境变量，如果没有返回none
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
# 关闭对模型修改的监控
# 配置键SQLALCHEMY_TRACK_MODIFICATIONS：如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
#                                      这需要额外的内存， 如果不必要的可以禁用它：
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 设置Session密钥SECRET_KEY
# app.config['SECRET_KEY'] = 'dev'

# 示读取系统环境变量 SECRET_KEY 的值，如果没有获取到，则使用 dev
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

################################################################################创建数据库对象:
# 将app进行扩展：给类SQLAlchemy传递一个对象app，实例化创建一个SQLAlchemy类对象db
db = SQLAlchemy(app)

################################################################################创建用户登录管理器:
# 将app进行扩展：给类LoginManager传递一个对象app，实例化创建一个LoginManager类对象login_manager
login_manager = LoginManager(app)

#注册用户加载回调函数,即定义Flask-Login的current_user变量
@login_manager.user_loader
# 定义用户加载回调函数，接受用户ID作为参数
def load_user(user_id):
    from watch.models import User
    # 读取User表主建为参数user_id的记录(User类的一个实例对象)，赋给变量user
    user = User.query.get(int(user_id))
    # 返回变量user(这个实例对象，即主建user_id对应的一条记录)，完成对current_user变量的赋值
    return user

############# 设置违法操作的响应和提示
# 凡是用@login_required装饰器装饰的视图函数，当在无登录的状态下调用时，会被重定到视图函数login()
login_manager.login_view = 'login'
# 凡是用@login_required装饰器装饰的视图函数，当在无登录的状态下调用时，会在重定到页面闪现信息：Login failed
login_manager.login_message = "Login failed/登录失败"

########--模板上下文处理函数
# 注册模板上下文处理器函数，就时将模样与该函数映射关联起来
@app.context_processor
def inject_user():
    from watch.models import User
    # 把多个模板需要使用的变量一次性在这里定义、传值
    # 获取 User 模型的第一个记录，然后赋值给变量 user
    user = User.query.first()
    # 用dict()函数创建一个映射字典，结果{'user': user}
    dic = dict(user=user)
    # 返回映射字典
    return dic

from watch import views, errors, commands
