set foreign_key_checks = 0;
 
drop table /*! if exists */ book_genres;

create table book_genres (
   id                int unsigned not null primary key,
   book_id           int unsigned not null,
   genre_id         int unsigned not null,

   foreign key (book_id)   references books (id),
   foreign key (genre_id) references genres (id)
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/book_genres.csv' into table book_genres
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from book_genres;


