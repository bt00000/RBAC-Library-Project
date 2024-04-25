class Config:
    SECRET_KEY = 'your_secret_key'  # ensure this is a secure key
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://brennan:123@localhost/sjsulibrary'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
