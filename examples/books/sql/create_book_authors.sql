set foreign_key_checks = 0;
 
drop table /*! if exists */ book_authors;

create table book_authors (
   id                int unsigned not null primary key,
   book_id           int unsigned not null,
   author_id         int unsigned not null,

   foreign key (book_id)   references books (id),
   foreign key (author_id) references authors (id)
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/book_authors.csv' into table book_authors
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from book_authors;


