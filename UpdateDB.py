from classes.AmusedDB import AmusedDB


db = AmusedDB()

insert1 = "INSERT INTO videos (videos_name, videos_category_SO, videos_level_SO, videos_background_SO, videos_description, videos_duration) values "

SQLString = insert1 +  "('Flesjes nemen kamer.mp4', 2, 1, 2, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen kamer.mp4', 2, 2, 2, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen kamer.mp4', 2, 3, 2, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen kamer.mp4', 2, 4, 2, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen kamer.mp4', 2, 5, 2, 'Flesjes nemen',  55)"
db.execute(SQLString)


SQLString = insert1 +  "('Flesjes nemen zee.mp4', 2, 1, 1, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen zee.mp4', 2, 2, 1, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen zee.mp4', 2, 3, 1, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen zee.mp4', 2, 4, 1, 'Flesjes nemen',  55)"
db.execute(SQLString)
SQLString = insert1 +  "('Flesjes nemen zee.mp4', 2, 5, 1, 'Flesjes nemen',  55)"
db.execute(SQLString)



