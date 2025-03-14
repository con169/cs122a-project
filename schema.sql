DROP DATABASE IF EXISTS cs122a;
CREATE DATABASE cs122a;
USE cs122a;

CREATE TABLE users (
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

CREATE TABLE producers (
	uid INTEGER PRIMARY KEY,
    bio VARCHAR(200),
    company VARCHAR(50),
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);

CREATE TABLE viewers (
	uid INTEGER PRIMARY KEY,
    subscription ENUM('free', 'monthly', 'yearly') DEFAULT 'free',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);
 
CREATE TABLE releases (
	rid INTEGER PRIMARY KEY AUTO_INCREMENT,
	producer_uid INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	genre VARCHAR(50),
	release_date DATE,
	FOREIGN KEY (producer_uid) REFERENCES producers(uid)
);

CREATE TABLE movies (
	rid INTEGER PRIMARY KEY,
    website_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (rid) REFERENCES releases(rid) ON DELETE CASCADE
);

CREATE TABLE series (
	rid INTEGER PRIMARY KEY,
    introduction TEXT NOT NULL,
    FOREIGN KEY (rid) REFERENCES releases(rid) ON DELETE CASCADE
);

CREATE TABLE videos (
	rid INTEGER,
    ep_num INTEGER,
    title VARCHAR(200) NOT NULL,
    length INTEGER NOT NULL,	
    PRIMARY KEY (rid, ep_num),
    FOREIGN KEY (rid) REFERENCES releases(rid) ON DELETE CASCADE
);

CREATE TABLE sessions (
	sid INTEGER PRIMARY KEY AUTO_INCREMENT,
    uid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    ep_num INTEGER NOT NULL,
    initiate_at DATETIME NOT NULL,
    leave_at DATETIME DEFAULT NULL,
    quality ENUM('480p', '720p', '1080p'),
    device ENUM('mobile','desktop'),
    FOREIGN KEY (uid) REFERENCES viewers(uid) ON DELETE CASCADE,
    FOREIGN KEY (rid, ep_num) REFERENCES videos(rid, ep_num) ON DELETE CASCADE
);

CREATE TABLE reviews (
	rvid INTEGER PRIMARY KEY AUTO_INCREMENT,
    uid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    body TEXT,
    posted_at DATETIME NOT NULL,
    FOREIGN KEY (uid) REFERENCES viewers(uid) ON DELETE CASCADE,
    FOREIGN KEY (rid) REFERENCES releases(rid) ON DELETE CASCADE
);
