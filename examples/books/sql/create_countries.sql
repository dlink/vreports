create table countries (
   id                int unsigned not null primary key,
   iso2              varchar(2)   not null,
   iso3              varchar(3)   not null,
   name              varchar(255) not null,
   nationality       varchar(255) not null
) 
engine InnoDB default charset=utf8;
;
