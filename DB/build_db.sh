echo -e "create table users(id integer primary key,                     \
				   screen_name varchar[15] not null,                    \
				   name varchar[50] not null);                          \
-- names length limit as specified here:                                \
https://help.twitter.com/en/managing-your-account/change-twitter-handle \n \
                                                                        \
create table follows(id1 integer not null,                              \
					   id2 integer not null,                            \
					   primary key (id1, id2),                          \
					   foreign key (id1) references users(id),          \
					   foreign key (id2) references users(id));"        | sqlite3 TwitterMineDB.db
