# 从 watch 包中导入app 对象、db 对象
from watch import app, db
# 导入Flask的依赖clink
import click
# 从 watch包的models模块中导入User类 和 Movie类
# 因为我们在__init__.py文件没有导入models模块，所以写成watch.models
from watch.models import User, Movie

################################################################################用命令创建数据库表格:
# 自定义创建数据库表的函数initdb()的Flask命令initdb，用命令执行下面函数
# 定义完之后，在flask shell下执行flask initdb 或者 flask initdb --drop 命令
@app.cli.command()
# 设置命令initdb的位置参数及输入方式:drop = True,help='Create after drop.'
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database(初始化数据库)."""
# 根据命令行输入的选项参数执行不同的动作：
    # 如果drop = True：
    if drop:
        # 执行删除数据库所有表格
        db.drop_all()
        # 在屏幕上打印出提示信息
        print('Delete all tables.')
    # 否则（drop = False）
    else:
        # 创建数据库所有表格（创建一个空表格）
        db.create_all()
        # click.echo():将消息加上换行符打印到给定文件或标准输出,即在屏幕上输出提示信息
        click.echo('Initialized database.')

################################################################################数据库操作--用命令创建记录
################-----创建数据库记录
###方法一：在命令行 flask shell中用命令创建
      # 第一步：创建表格
          # >>> from app import db 从模块app中导入数据库对象db
          # >>> db.create_all() 调用数据库对象db的create_all()方法创建空表格
              # 注意：如果模型类有修改（表格有修改），想重新生成新的表模式，必须先使用 db.drop_all() 删除所有表，然后再重新创建表
                     # >>> db.drop_all()
                     # >>> db.create_all()
      # 第二步：创建记录
        # >>> from app import User, Movie # 导入模型类
        # >>> user = User(name='Grey Li') # 创建一个 User 记录
        # >>> m1 = Movie(title='Leon', year='1994') # 创建一个 Movie 记录
        # >>> m2 = Movie(title='Mahjong', year='1996') # 再创建一个 Movie 记录
        # >>> db.session.add(user) # 把新创建的记录添加到数据库会话
        # >>> db.session.add(m1)
        # >>> db.session.add(m2)
        # >>> db.session.commit() # 提交数据库会话，只需要在最后调用一次即可

###方法二：自定义一个函数帮我们创建：
# 自定义生成数据的函数forge()的Flask命令forge，用命令执行下面函数
@app.cli.command()
def forge():
    """Generate fake data(生成虚拟数据)."""
    # 创建数据库所有表格（创建一个空表格）
    # db.create_all()
    # 定义变量name
    nickname = 'Beginners'
    # 定义字典变量movie
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    # 将变量name(即weijp)传User类的name列，实例化User类创建表格user(表格name列的数据为weijp),即在空表格中创建一条记录
    user = User(nickname=nickname)
    # 将表格的实例对象user(一条记录name=weijp)添加到数据库会话
    db.session.add(user)
    # 将列表变量movie的字典元素遍历赋给变量m
    for m in movies:
        # 然后，把字典m的title键和year键对应的值分别赋给Movie类的title列和year列，再实例化创建movie对象，即在表格中创建movie记录
        # 即用for语句在表格中逐条创建记录
        movie = Movie(title=m['title'], year=m['year'])
        # 用for语把表格的对象movie(movie记录)逐条添加到数据库会话
        db.session.add(movie)
    # 遍历完成后，把数据库会话记录提交到数据库，只需要在最后调用一次即可
    db.session.commit()
    # 在屏幕上打印出提示信息
    click.echo('Done.')


################################################################################用命令在User模型中注册管理员帐户
# 自定义创建数据库表的函数admin()的Flask命令admin，用命令执行下面函数
# 定义完之后，在flask shell下执行flask admin 命令：
#   方法一：分两步输入，先输入flask admin执行，然后按提示username:weijp和password:123输入执行
#   方法二：一步输入执行：flask admin --username:weijp --password:123
@app.cli.command()
# 设置命令admin的位置参数username及输入方式：
@click.option('--username',prompt=True,help='The username used to login.')  #
# 设置命令admin的位置参数password及输入方式：prompt=True提示用户输入，hide_input=True隐藏输入信息，confirmation_prompt=为True需要做信息二次确认
@click.option('--password', prompt=True,hide_input=True, confirmation_prompt=True, help='The password used to login.')
def register(username, password):
    """Create user."""
    # 创建数据库所有表格（创建一个空表格）
    # 考虑到第一次创建数据库，如果上面已经初始过，数据库已经存在，就不需要这一步创建一个新的数据库
    db.create_all()
    # 读取User表格的第一个记录(一个实例)，然后赋值给变量 user
    # 如果上面forget()被执行过，这个记录就是weijp,如果没有被执行过，这个记录就是一个空值
    user = User.query.first()
    # 如果变量user不是空值（已存在记录），会话已存在只要更新即可
    if user is not None:
        # click.echo():将消息加上换行符打印到给定文件或标准输出,即输出提示信息：更新用户记录
        click.echo('Updating user...')
        # 把参数username赋给记录user的username列（以前是空值，现在重写user实例对象的username属性）
        user.username = username
        # 利用user记录的set_password()方法为参数password设置一个加密的密码
              # 该方法又把加密后的密码赋值给实例对象user的password_hash属性（以前是空值，现在重写user实例对象的password_hash属性）
        user.set_password(password)

        # 更新后的记录内容：name='原有记录weijp'，username=参数username, password_hash = generate_password_hash(参数password)
    # 否则(变量user是空值,即User表格是空的没有任何记录)
    else:
        # click.echo():将消息加上换行符打印到给定文件或标准输出,即输出提示信息：创建用户记录
        click.echo('Creating user...')
        # 把参数username赋给User类的username属性，把字符串'Admin'赋给User类的name属性，然后实例化创建一条记录user(User类实例化对象)
        user = User(username=username, nickname='Admin')
        # 利用user记录的set_password()方法为参数password设置一个加密的密码
              # 该方法又把加密后的密码赋值给实例对象user的password_hash属性
        user.set_password(password)
        # 将表格的实例对象user(一条记录)添加到数据库会话
        # 记录内容：name='Admin'，username=参数username, password_hash = generate_password_hash(参数password)
        db.session.add(user)
    # 将上面的会话信息提交数据库
    db.session.commit()
    # 这个记录为：name='weijp'或'Admin'，username=参数username, password_hash = generate_password_hash(参数password)

    # click.echo():将消息加上换行符打印到给定文件或标准输出,即输出提示信息：完成，即数据库已有一条管理员用户记录
    click.echo('Done.')
