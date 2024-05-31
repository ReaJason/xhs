from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

from plus.model.Model import Base, Comment

SQLiteURL = 'sqlite:///data.db'

# 创建engine，即数据库驱动信息
engine = create_engine(
    url=SQLiteURL,
    echo=True,    # 打开sqlalchemy ORM过程中的详细信息
    connect_args={
        'check_same_thread':False   # 是否多线程
    }
)


# User.__table__.create(engine, checkfirst=True)
# 映射创建表
# User.__table__
Base.metadata.create_all(engine, checkfirst=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=True,
    expire_on_commit=True
)
# 创建session实例（实例化）
db = SessionLocal()


class DB_UTILS():

    DB = db
    @staticmethod
    def save(data):
        db.add(data)
        db.commit()

if __name__ == '__main__':
    DB_UTILS.save(Comment(name='xiaoming', age=18, address='beijing'))