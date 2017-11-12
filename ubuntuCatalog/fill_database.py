from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalog@localhost/catalogdb')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# User
user = User(
    name="Derek Harmann",
    email="derekhar2468@gmail.com",
    picture="http://www.diaglobal.org/_Images/member/Generic_Image_Missing-Profile.jpg"
)
session.add(user)

# Categories
categories = ["Snowboarding", "Soccer", "Basketball", "Baseball", "Rock Climbing", "Frisbee"]
for category in categories:
    session.add(Category(name=category))

# Items
items = [
    Item(
        name="Helmet",
        description="Protective item for your head.",
        category_id=1,
        user_id=1
    ),
    Item(
        name="Snowpants",
        description="Warm leg apparel.",
        category_id=1,
        user_id=1
    )
]
for item in items:
    session.add(item)

session.commit()