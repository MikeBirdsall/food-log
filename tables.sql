-- table definitions for creating db examples for food

create table course(
    id                 integer primary key autoincrement not null,
    orig_description   text,
    orig_comment       text,
    orig_servings      decimal,
    orig_calories      decimal,
    orig_fat           decimal,
    orig_protein       decimal,
    orig_carbs         decimal,
    orig_time          time,
    orig_day           date,
    orig_meal          text,
    orig_size          text,
    image_file         text,
    description        text,
    comment            text,
    servings           decimal,
    calories           decimal,
    fat                decimal,
    protein            decimal,
    carbs              decimal,
    day                date,
    time               time,
    meal               text,
    size               text,
    ini_id             text,
    thumb_id           text
);

create table template(
    id                 integer primary key autoincrement not null,
    description        text,
    comment            text,
    calories           decimal,
    fat                decimal,
    protein            decimal,
    carbs              decimal,
    size               text
);
