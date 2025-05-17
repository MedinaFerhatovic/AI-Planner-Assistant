CREATE DATABASE aiplannerassistant;

USE aiplannerassistant;

CREATE TABLE plannerassistant (
    id INT auto_increment PRIMARY KEY,
    timestamp timestamp default current_timestamp,
    message varchar(1000),
    response varchar(2000)
);