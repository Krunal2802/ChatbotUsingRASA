-- create database chatbot_data;

-- create table "price_weight" 
use chatbot_data;
create table price_weight(
min_range int,
max_range int,
price int);

-- insert the price values for weight price
use chatbot_data;
insert into price_weight values (0,3,20);
insert into price_weight values (3,8,30);
insert into price_weight values (8,20,50);
insert into price_weight values (20,40,100);
insert into price_weight values (40,70,160);
insert into price_weight values (70,100,200);
insert into price_weight values (100,500,400);
insert into price_weight values (500,1000,600);

-- create table "price_polygon"
use chatbot_data;
create table price_polygon(
source_polygon varchar(1),
dest_polygon varchar(1),
price int);

-- insert the price values for polygon price
use chatbot_data;
insert into price_polygon values ('A','A',20);
insert into price_polygon values ('A','B',30);
insert into price_polygon values ('A','C',35);
insert into price_polygon values ('A','E',40);
insert into price_polygon values ('A','F',45);
insert into price_polygon values ('A','G',50);
insert into price_polygon values ('A','H',60);

insert into price_polygon values ('B','A',30);
insert into price_polygon values ('B','B',20);
insert into price_polygon values ('B','C',30);
insert into price_polygon values ('B','E',30);
insert into price_polygon values ('B','F',40);
insert into price_polygon values ('B','G',40);
insert into price_polygon values ('B','H',50);

insert into price_polygon values ('C','A',35);
insert into price_polygon values ('C','B',30);
insert into price_polygon values ('C','C',20);
insert into price_polygon values ('C','E',30);
insert into price_polygon values ('C','F',30);
insert into price_polygon values ('C','G',40);
insert into price_polygon values ('C','H',45);

insert into price_polygon values ('E','A',40);
insert into price_polygon values ('E','B',30);
insert into price_polygon values ('E','C',35);
insert into price_polygon values ('E','E',20);
insert into price_polygon values ('E','F',30);
insert into price_polygon values ('E','G',30);
insert into price_polygon values ('E','H',40);

insert into price_polygon values ('F','A',45);
insert into price_polygon values ('F','B',40);
insert into price_polygon values ('F','C',20);
insert into price_polygon values ('F','E',30);
insert into price_polygon values ('F','F',20);
insert into price_polygon values ('F','G',35);
insert into price_polygon values ('F','H',35);

insert into price_polygon values ('G','A',50);
insert into price_polygon values ('G','B',40);
insert into price_polygon values ('G','C',40);
insert into price_polygon values ('G','E',30);
insert into price_polygon values ('G','F',35);
insert into price_polygon values ('G','G',20);
insert into price_polygon values ('G','H',30);

insert into price_polygon values ('H','A',60);
insert into price_polygon values ('H','B',50);
insert into price_polygon values ('H','C',45);
insert into price_polygon values ('H','E',40);
insert into price_polygon values ('H','F',35);
insert into price_polygon values ('H','G',30);
insert into price_polygon values ('H','H',20);

-- create table "deliveries" 
use chatbot_data;
create table deliveries_data(
order_id varchar(24) not null,
username varchar(30),
source_address varchar(255) not null,
dest_address varchar(255)not null,
source_city varchar(255) not null,
dest_city varchar(255) not null,
source_polygon varchar(255) not null,
dest_polygon varchar(255) not null,
product varchar(20) not null,
parcel_weight float not null,
total_price int not null,
phone_number bigint,
timestamp datetime not null,
status varchar(255),
primary key(order_id)
);

use chatbot_data;
create table users(	
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(255) UNIQUE NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
password VARCHAR(255) NOT NULL
);