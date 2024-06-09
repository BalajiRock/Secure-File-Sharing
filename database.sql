use Users;

CREATE TABLE user(
    user_name varchar(255) NOT NULL,
    user_email varchar(255) NOT NULL,
    email_verified TINYINT(1) Default 0,
    verification_token varchar(255),
    salt varchar(16) NOT NULL,
    hashed_password varchar(255) NOT NULL,
    user_type TINYINT(1) NOT NULL,
    PRIMARY KEY (user_name)
)

CREATE TABLE files(
    user_name varchar(255) NOT NULL,
    file_name varchar(255) NOT NULL
    PRIMARY KEY(user_name,file_name)
)    