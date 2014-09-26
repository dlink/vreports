set foreign_key_checks = 0;
 
drop table /*! if exists */ genres;

create table genres (
   id                int unsigned not null primary key,
   name              varchar(255)
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/genres.csv' into table genres
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from genres;


