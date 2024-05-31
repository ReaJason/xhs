from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Comment(Base):

    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(String(100))
    ip_location = Column(String(100))
    content = Column(String(1000))
    create_time = Column(String(100))
    user_id = Column(String(100))
    nickname = Column(String(100))
    comment_id = Column(String(100))
    title = Column(String(1000))
    image = Column(String(1000))
    status = Column(String(1000))
    gender = Column(String(1000))
    desc = Column(String(1000))
    ip_2_location = Column(String(1000))
    status_115 = Column(String(1000))

class HasComments(Base):
    __tablename__ = 'has_comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(100))