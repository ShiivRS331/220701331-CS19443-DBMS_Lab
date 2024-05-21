drop table users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);
insert into users(username,password,role) values('Shiiv','shiiv123','doctor');

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    family_history TEXT,
    surgeries TEXT,
    allergies TEXT,
    symptoms TEXT,
    diagnosis TEXT,
    tests TEXT,
    medications TEXT,
    report TEXT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_login BOOLEAN DEFAULT TRUE
);


truncate table patients
select * from patients 

select * from users
