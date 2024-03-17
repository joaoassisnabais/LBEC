drop table users CASCADE;
drop table admins CASCADE;
drop table actions CASCADE;
drop table games CASCADE;
drop table game_players CASCADE;

create table users (
    name varchar(255),
    pass varchar(255),

    primary key(name)
);

create table admins (
    name varchar(255),

    primary key(name),
    foreign key(name) references users(name)
);

create table actions (
    player varchar(255),
    day integer,

    primary key(player, day),
    foreign key(player) references users(name)
);

create table games (
    name varchar(255),
    created_by varchar(255),
    creation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    primary key(name),
    foreign key(created_by) references users(name)
);

create table game_players (
    player_name varchar(255),
    game_id varchar(255),
    primary key(player_name, game_id),
    foreign key(player_name) references users(name),
    foreign key(game_id) references games(name)
);
