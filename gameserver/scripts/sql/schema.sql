drop table users CASCADE;
drop table consumptions CASCADE;
drop table events CASCADE;

create table users (
    name varchar(255),
    pass varchar(255),

    primary key(name)
);

create table consumptions (
    username varchar(255),
    area varchar(255),
    timestamp DATE NOT NULL DEFAULT CURRENT_DATE,
    energy float,
    water float,
    gas float,

    primary key(area),
    foreign key(username) references users(name)
);

create table events (
    created_by varchar(255),
    timestamp DATE NOT NULL DEFAULT CURRENT_DATE,
    description varchar(255),
    title varchar(255),
    
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
