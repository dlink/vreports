create table book_genres (
   id                int unsigned not null primary key,
   book_id           int unsigned not null,
   genre_id         int unsigned not null,

   foreign key (book_id)   references books (id),
   foreign key (genre_id) references genres (id)
) 
engine InnoDB default charset=utf8;
;
