CREATE DATABASE lcu_database;

USE lcu_database;

CREATE TABLE Students_lcu (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(255), NOT NULL,
  last_name VARCHAR(255), NOT NULL,
  username VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  
);

INSERT INTO Students_lcu (first_name, last_name, username, password)
VALUES
  ('John', 'Doe', 'johndoe', 'password1'),
  ('Jane', 'Smith', 'janesmith', 'password2'),
  ('Michael', 'Johnson', 'michaelj', 'password3'),
  ('Emily', 'Davis', 'emilyd', 'password4'),
  ('David', 'Anderson', 'davida', 'password5'),
  ('Sarah', 'Wilson', 'sarahw', 'password6'),
  ('Robert', 'Martinez', 'robertm', 'password7'),
  ('Jessica', 'Taylor', 'jessicat', 'password8'),
  ('William', 'Thomas', 'williamt', 'password9'),
  ('Olivia', 'White', 'oliviaw', 'password10');


