import sqlite3

DB_FILE = "/cs/usr/jonahar/PythonProjects/TwitterMine/DB/TwitterMineDB.db"

# connecting to the DB (assuming DB already exist with the relevant tables)
conn = sqlite3.connect(DB_FILE)

# get all pairs of (follower, followee)
cursor = conn.execute("""SELECT u1.name, u2.name
                FROM users u1, users u2
                WHERE exists(
			                SELECT *
			                FROM follows F
			                WHERE F.id1 = u1.id AND F.id2 = u2.id) """)
for line in cursor:
    print(line)
