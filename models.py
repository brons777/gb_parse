from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DATE

Base = declarative_base()

"""
one to one
one to many - many to one
many to many 
"""

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)



class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    date_post = Column(DATE, unique=False, nullable=False)
    title = Column(String, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author")
    tags = relationship('Tag', secondary=tag_post)
    comments = relationship('Comment')


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False)
    posts = relationship("Post")


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    posts = relationship("Post", secondary=tag_post)


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, ForeignKey('post.id'), autoincrement=True, primary_key=True)
    comment_author = Column(String, unique=False)
    comment_text = Column(String, unique=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author")