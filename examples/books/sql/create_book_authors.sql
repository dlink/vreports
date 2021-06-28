create table book_authors (
   id                int unsigned not null primary key,
   book_id           int unsigned not null,
   author_id         int unsigned not null,

   foreign key (book_id)   references books (id),
   foreign key (author_id) references authors (id)
) 
engine InnoDB default charset=utf8;
;
