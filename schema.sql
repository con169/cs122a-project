DROP DATABASE IF EXISTS cs122a;
CREATE DATABASE cs122a;
USE cs122a;

CREATE TABLE Users (
	uid INTEGER AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(30) UNIQUE NOT NULL,
    joined_date DATE,
    nickname VARCHAR(20) NOT NULL,
    street VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    genres TEXT  -- Ensure CSV header uses 'genre_list' NOT 'genres'
    
);

CREATE TABLE Producers (
	uid INTEGER PRIMARY KEY,
    bio VARCHAR(200),
    company VARCHAR(50),
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE
);

CREATE TABLE Viewers (
	uid INTEGER PRIMARY KEY,
    subscription ENUM('free', 'monthly', 'yearly') DEFAULT 'free',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE
);
 
CREATE TABLE Releases (
	rid INTEGER PRIMARY KEY AUTO_INCREMENT,
	producer_uid INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	genre VARCHAR(50),
	release_date DATE,
	FOREIGN KEY (producer_uid) REFERENCES Producers(uid)
);

CREATE TABLE Movies (
	rid INTEGER PRIMARY KEY,
    website_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (rid) REFERENCES Releases(rid) ON DELETE CASCADE
);

CREATE TABLE Series (
	rid INTEGER PRIMARY KEY,
    introduction TEXT NOT NULL,
    FOREIGN KEY (rid) REFERENCES Releases(rid) ON DELETE CASCADE
);

CREATE TABLE Videos (
	rid INTEGER,
    ep_num INTEGER,
    title VARCHAR(200) NOT NULL,
    length INTEGER NOT NULL,	
    PRIMARY KEY (rid, ep_num),
    FOREIGN KEY (rid) REFERENCES Releases(rid) ON DELETE CASCADE
);

CREATE TABLE Sessions (
	sid INTEGER PRIMARY KEY AUTO_INCREMENT,
    uid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    ep_num INTEGER NOT NULL,
    initiate_at DATETIME NOT NULL,
    leave_at DATETIME DEFAULT NULL,
    quality ENUM('480p', '720p', '1080p'),
    device ENUM('mobile','desktop'),
    FOREIGN KEY (uid) REFERENCES Viewers(uid) ON DELETE CASCADE,
    FOREIGN KEY (rid, ep_num) REFERENCES Videos(rid, ep_num) ON DELETE CASCADE
);

CREATE TABLE Reviews (
	rvid INTEGER PRIMARY KEY AUTO_INCREMENT,
    uid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    body TEXT,
    posted_at DATETIME NOT NULL,
    FOREIGN KEY (uid) REFERENCES Viewers(uid) ON DELETE CASCADE,
    FOREIGN KEY (rid) REFERENCES Releases(rid) ON DELETE CASCADE
);
