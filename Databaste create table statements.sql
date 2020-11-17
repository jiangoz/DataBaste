DROP DATABASE IF EXISTS databaste;
CREATE DATABASE  IF NOT EXISTS databaste;
USE databaste;

create table recipe (
recipe_id int,
recipe_name varchar(150) not null,
prep_time int,
cook_time int,
total_time int,
servings int,
primary key (recipe_id)
);

create table review (
rating int not null,
recipe_id int,
foreign key (recipe_id) references recipe(recipe_id)
);

create table flavor (
flavor_id int,
flavor_name varchar(45) not null,
primary key (flavor_id)
);

create table molecule (
pubchem_id int,
molecule_name varchar(120) not null,
primary key (pubchem_id)
);

create table property (
pubchem_id int,
flavor_id int,
foreign key (pubchem_id) references molecule(pubchem_id),
foreign key (flavor_id) references flavor(flavor_id)
);

create table category (
category_id int,
category_name varchar(60),
primary key (category_id)
);

create table ingredient (
ingredient_id int,
ingredient_name varchar(60) not null,
category_id int,
primary key (ingreient_id),
foreign key (category_id) references category(category_id)
);

create table composition (
ingredient_id int,
pubchem_id int,
foreign key (ingredient_id) references ingredient(ingredient_id),
foreign key (pubchem_id) references molecule(pubchem_id)
);

create table amount (
amount int not null,
unit varchar(45),
recipe_id int,
ingredient_id int,
foreign key (recipe_id) references recipe(recipe_id),
foreign key (ingredient_id) references ingredient(ingredient_id)
);