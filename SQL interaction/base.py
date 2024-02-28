import db

db = db.BD()

st = 'test'

db.add_users([11, 1, '01.01.2024', 1])
print(db.get_users()[-1])