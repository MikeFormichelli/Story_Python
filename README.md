This is a small character database app for writing or RPG games. Though it is system agnostic and lacks stat blocks, it can be used to work out a character's general shape, etc.
I wrote it two ways, so there is a terminal app (app.py) and a main visual app done with PyQT6 (my first time making an app with PyQT6).
To run the 100% visual app (and in my opinion, the better one), run visual_app.py.
It uses a Mongo Database, but doesn't have to (it doubles storage in a local JSON file in the same folder. If it doesn't find a MongoDB it just runs off the database).

To set up your own database create a .env file and set MONGO_URI and DB_NAME as you see fit.
It could also be modified to run off a SQL/POSTGRE database. (Potentially my next major change).
