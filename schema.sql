DROP DATABASE IF EXISTS cs122a_hw2;
CREATE DATABASE cs122a_hw2;
USE cs122a_hw2;

CREATE TABLE Users (
	uid INTEGER AUTO_INCREMENT,
    nickname VARCHAR(20) NOT NULL,
    email VARCHAR(30) UNIQUE NOT NULL,
    street VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    genre_list TEXT,
    joined_date DATE,
    PRIMARY KEY (uid)
    );
    
CREATE TABLE Producers (
	user_id INTEGER PRIMARY KEY,
    company VARCHAR(50),
    bio VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES Users(uid) 
    ON DELETE CASCADE
    );
    
CREATE TABLE Viewers (
	user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    subscription ENUM('free', 'monthly', 'yearly') DEFAULT 'free',
    FOREIGN KEY (user_id) REFERENCES Users(uid)
    ON DELETE CASCADE);
 
CREATE TABLE Releases (
	rid INTEGER PRIMARY KEY auto_increment,
	producer INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	genre VARCHAR(50),
	release_date DATE,
	FOREIGN KEY (producer) 
    REFERENCES Producers(user_id)
    );

CREATE TABLE Movies (
	rid INTEGER PRIMARY KEY,
    website_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (rid) REFERENCES Releases(rid)
    ON DELETE CASCADE
    );

CREATE TABLE Series (
	rid INTEGER PRIMARY KEY,
    introduction TEXT NOT NULL,
    FOREIGN KEY (rid) REFERENCES Releases(rid)
    ON DELETE CASCADE
    );

CREATE TABLE Videos (
	rid INTEGER,
    ep_num INTEGER,
    title VARCHAR(200) NOT NULL,
    length INTEGER NOT NULL,	
    PRIMARY KEY (rid, ep_num),
    FOREIGN KEY (rid) REFERENCES Releases(rid)
    ON DELETE CASCADE
    );
    
CREATE TABLE Sessions (
	sid INTEGER PRIMARY KEY AUTO_INCREMENT,
    quality ENUM('480p', '720p', '1080p'),
    device ENUM('mobile','desktop'),
    initiate_at DATETIME NOT NULL,
    leave_at DATETIME DEFAULT NULL,
    user_id INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    ep_num INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Viewers(user_id)
    ON DELETE CASCADE,
    FOREIGN KEY (rid, ep_num) REFERENCES Videos(rid,ep_num)
    ON DELETE CASCADE
    );
    
CREATE TABLE Reviews (
	rvid INTEGER PRIMARY KEY auto_increment,
    rating DECIMAL(2,1) NOT NULL,
    body TEXT,
    rid INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    posted_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Viewers(user_id)
    ON DELETE CASCADE,
    FOREIGN KEY (rid) REFERENCES Releases(rid) 
    ON DELETE CASCADE
    );