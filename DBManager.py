import sqlite3
import os

add_user_query = """INSERT INTO Users
                    SELECT ?, ?, ?
                    WHERE NOT EXISTS (SELECT *
                                      FROM Users U
                                      WHERE U.id = ?);"""

add_follows_query = """INSERT INTO Follows
                       SELECT ?, ?
                       WHERE NOT EXISTS (SELECT *
	                                     FROM Follows F
	                                     WHERE F.id1 = ? AND F.id2 = ?);"""

get_friends_query = 'SELECT * FROM Follows'

get_friends_by_attr_query = """SELECT u1.{0}, u2.{0}        
                               FROM users u1, users u2             
                               WHERE exists(SELECT *                    
                                            FROM follows F              
                                            WHERE F.id1 = u1.id AND F.id2 = u2.id)"""


class DBManager:
    """
    This object is the pipe to the database. It can insert and retrieve data.
    """

    def __init__(self, database):
        """
        :param database: string, the filename of the database
        """
        if not os.path.isfile(database):
            raise FileNotFoundError("database doesn't exist")
        self._database = database

    def add_user(self, user_data):
        """
        :param user_data: tuple (id, screen_name, name)
        """
        id, scr, name = user_data
        conn = sqlite3.connect(self._database, check_same_thread=False)
        conn.execute(add_user_query, (id, scr, name, id))
        conn.commit()
        conn.close()

    def add_follows(self, id1_list, id2_list):
        """
        add all pairs (id1,id2) from the cartesian product id1_list X id2_list to
        the table 'Follows'

        :param id1_list: list of integers
        :param id2_list: list of integers
        :return:
        """
        conn = sqlite3.connect(self._database, check_same_thread=False)
        for id1 in id1_list:
            for id2 in id2_list:
                conn.execute(add_follows_query, (id1, id2, id1, id2))
        conn.commit()
        conn.close()

    def get_friends(self, attr='id'):
        """
        returns a list of pairs (follower, followee).

        :param attr: the attribute that is returned to identify the users. should be one
                     of the strings 'id', 'screen_name', 'name'
        :return: list of pairs (tuples)
        """
        if attr == 'id':
            q = get_friends_query
        else:
            q = get_friends_by_attr_query.format(attr)
        conn = sqlite3.connect(self._database, check_same_thread=False)
        cursor = conn.execute(q)
        res = cursor.fetchall()
        conn.close()
        return res
