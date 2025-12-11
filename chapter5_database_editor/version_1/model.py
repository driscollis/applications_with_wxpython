# model.py

from sqlalchemy import Column, create_engine
from sqlalchemy import Integer, ForeignKey, String, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

engine = create_engine("sqlite:///books.db", echo=True)
Base = declarative_base()
metadata = Base.metadata


class OlvBook(object):
    """
    Book model for ObjectListView
    """

    def __init__(self, id, title, author, isbn, publisher,
                 last_name, first_name):
        self.id = id  # unique row id from database
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.last_name = last_name
        self.first_name = first_name


class Person(Base):
    """"""
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    first_name = mapped_column("first_name", String(50))
    last_name = mapped_column("last_name", String(50))
    books = relationship("Book", back_populates="person")

    def __repr__(self):
        """"""
        return "<Person: %s %s>" % (self.first_name, self.last_name)


class Book(Base):
    """"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    author_id = mapped_column(Integer, ForeignKey("people.id"))
    title = mapped_column("title", Unicode)
    isbn = mapped_column("isbn", Unicode)
    publisher = mapped_column("publisher", Unicode)
    person = relationship("Person", back_populates="books")

metadata.create_all(engine)