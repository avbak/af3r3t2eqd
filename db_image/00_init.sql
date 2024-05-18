CREATE TABLE IF NOT EXISTS Phones (
    ID SERIAL PRIMARY KEY,
    Phone VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Emails (
    ID SERIAL PRIMARY KEY,
    Email VARCHAR(100) NOT NULL
);

INSERT INTO phones (Phone) VALUES
('80000000000');

INSERT INTO emails (Email) VALUES
('test@test.test');

CREATE UNIQUE INDEX email_unique_idx ON Emails(email);
CREATE UNIQUE INDEX phone_unique_idx ON Phones(phone);
