ALTER SYSTEM SET log_replication_commands TO 'on';
ALTER SYSTEM SET archive_mode TO 'on';
ALTER SYSTEM SET archive_command TO 'cp %p /postgres_archive/%f';
ALTER SYSTEM SET max_wal_senders TO 10;
ALTER SYSTEM SET wal_level TO 'replica';
ALTER SYSTEM SET wal_log_hints TO 'on';

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
ALTER TABLE Phones OWNER TO CHANGE_OWNER;
ALTER TABLE Emails OWNER TO CHANGE_OWNER;
SELECT pg_reload_conf();