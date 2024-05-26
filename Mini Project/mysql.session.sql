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


-- Trigger to check unique username before insert
CREATE TRIGGER before_patient_insert
BEFORE INSERT ON patients
FOR EACH ROW
BEGIN
    DECLARE username_count INT;
    SELECT COUNT(*) INTO username_count FROM users WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists.';
    END IF;
END;

-- Trigger to generate report after insert
CREATE TRIGGER after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
    SET @report = CONCAT('Name: ', NEW.name, '\n',
                         'Age: ', NEW.age, '\n',
                         'Family History: ', NEW.family_history, '\n',
                         'Previous Surgeries: ', NEW.surgeries, '\n',
                         'Allergies: ', NEW.allergies, '\n',
                         'Symptoms: ', NEW.symptoms, '\n',
                         'Diagnosis: ', NEW.diagnosis, '\n',
                         'Tests: ', NEW.tests, '\n',
                         'Medications: ', NEW.medications);
    UPDATE patients SET report = @report WHERE id = NEW.id;
END;

