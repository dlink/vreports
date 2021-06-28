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
