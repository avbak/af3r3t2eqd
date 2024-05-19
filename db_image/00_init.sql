CREATE TABLE IF NOT EXISTS phones (
    ID SERIAL PRIMARY KEY,
    Phone VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS emails (
    ID SERIAL PRIMARY KEY,
    Email VARCHAR(100) NOT NULL
);

INSERT INTO phones (Phone) VALUES
('80000000000');

INSERT INTO emails (Email) VALUES
('test@test.test');

CREATE UNIQUE INDEX email_unique_idx ON emails(email);
CREATE UNIQUE INDEX phone_unique_idx ON phones(phone);
