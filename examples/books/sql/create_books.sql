create table books (
   id                int unsigned not null primary key,
   isbn              varchar(13),
   name              varchar(255),
   published         int unsigned comment 'Publication year',
   classification    enum('Novel', 'Nonfiction', 'Play', 'Poetry')
) 
engine InnoDB default charset=utf8;
;
