import sqlite3
import os


class DB:
    """
    This object is the pipe to the database. It can insert and retrieve data.
    """

    def __init__(self, database):
        """
        :param database: string, the filename of the database
        """
        if not os.path.isfile(database):
            raise FileNotFoundError("database doesn't exist")
        self.conn = sqlite3.connect(database)

    def add_user(self, user_data):
        """
        :param user_data: tuple (id, screen_name, name)
        """
        self.conn.execute('INSERT INTO users(id,screen_name,name) VALUES (?,?,?)', user_data)

    def add_follows(self, id1_list, id2_list):
        """
        add all pairs (id1,id2) to the table 'Follows', s.t. (id1,id2) is in
        the cartesian product  id1_list X id2_list
        :param id1_list: list of integers
        :param id2_list: list of integers
        :return:
        """
        for id1 in id1_list:
            for id2 in id2_list:
                self.conn.execute('INSERT INTO Follows(id1,id2) VALUES (?,?)', (id1, id2))
        self.conn.commit()

    def get_friends(self, attr='id'):
        """
        returns a list of pairs (follower, followee).

        :param attr: the attribute that is returned to identify the users. should be one
                     of the strings 'id', 'screen_name', 'name'
        :return: list of pairs (tuples)
        """
        if attr == 'id':
            sql_query = 'SELECT * FROM Follows'
        else:
            sql_query = """SELECT u1.name, u2.name        
                           FROM users u1, users u2             
                           WHERE exists(                       
			                SELECT *                    
			                FROM follows F              
			                WHERE F.id1 = u1.id AND F.id2 = u2.id)"""

        cursor = self.conn.execute(sql_query)
        return cursor.fetchall()
