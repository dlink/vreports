set foreign_key_checks = 0;
 
drop table /*! if exists */ books;

create table books (
   id                int unsigned not null primary key,
   isbn              varchar(13),
   name              varchar(255),
   published         int unsigned comment 'Publication year',
   classification    enum('Novel', 'Nonfiction', 'Play', 'Poetry')
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/books.csv' into table books
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from books;


