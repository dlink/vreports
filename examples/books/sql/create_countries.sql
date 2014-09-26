set foreign_key_checks = 0;
 
drop table /*! if exists */ countries;

create table countries (
   id                int unsigned not null primary key,
   iso2              varchar(2)   not null,
   iso3              varchar(3)   not null,
   name              varchar(255) not null,
   nationality       varchar(255) not null
) 
engine InnoDB default charset=utf8;
;

load data local infile 'data/countries.csv' into table countries
fields terminated by ',' optionally enclosed by '"' ignore 1 lines;

show count(*) warnings;
show warnings;

set foreign_key_checks = 1;

select * from countries;


