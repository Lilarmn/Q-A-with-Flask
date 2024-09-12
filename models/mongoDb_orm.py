"""
write orm for having better experience

"""
from pymongo import MongoClient
import bcrypt


def get_database():
    client = MongoClient('localhost', 27017)
    db = client['flask_project']

    if 'users' not in db.list_collection_names():
        collection = db.create_collection('users')
    else:
        collection = db.get_collection('users')

    return db, collection
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def create_user(username, instagram_id,password):
    hashed_password = hash_password(password)
    user = {
        "username": username,
        "instagram_id": instagram_id,
        "password": hashed_password
    }
    db,collection = get_database()
    collection.insert_one(user)
    print(f"User {username} saved with hashed password.")




def search_user(username):
    db,collection = get_database()
    return collection.find_one({ "username": username })

