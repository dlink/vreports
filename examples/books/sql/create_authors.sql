set foreign_key_checks = 0;
 
drop table /*! if exists */ authors;

create table authors (
   id                int unsigned not null primary key,
   first_name        varchar(255),
   middle_name       varchar(255),
   last_name         varchar(255),
   country_id        int unsigned,
   born              int unsigned,
   died              int unsigned,

   foreign key (country_id) references countries (id)
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/authors.csv' into table authors
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from authors;


