from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Database model for catalog users.
    Attributes:
        id (int): User's id.
        name (str): User's name.
        email (str): User's email.
        picture (str): URL string for picture.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """Database model for categories.
    Attributes:
        id (int): Category id.
        name (str): Category name.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    """Database model for category items.
    Attributes:
        id (int): Item id.
        name (str): Item name.
        description (str): Short description of item.
        image_url (str): URL string for image.
        category_id (int): Id of category the item belongs to.
        category (reference): Links the item to the category.
        user_id (int): Id of the user that created the item.
        user (reference): Links the item to the user.
    """
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=False)
    image_url = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


engine = create_engine('postgresql://catalog:catalog@52.15.112.148/catalogwithusers.db')
Base.metadata.create_all(engine)