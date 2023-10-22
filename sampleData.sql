
-- Insert into user (username, pwd, fname, lname, lastlogin, nickname) Values;
-- Insert into friend(user1, user2, acceptStatus, requestSentBy, createdAt, updatedAt) Values;
-- Insert into follows(follower, follows, createdAt) Values ;

Insert into artist (artistID, fname, lname, artistBio, artistURL) Values
('A0001', 'Frank', 'Sinatra', 'American singer and actor', 'http://www.sinatra.com'),
('A0002', 'Bruno', 'Mars', 'American singer, songwriter, and record producer', 'https://www.brunomars.com'),
('A0003', 'Ed', 'Sheeran', ' English singer-songwriter', 'https://www.edsheeran.com/'),
('A0004', 'Shakira', 'Mebarak Ripoll', 'Colombian singer and songwriter', "https://www.shakira.com/"),
('A0005','Jessie', 'J', 'English singer', "https://www.jessiejofficial.com/"),
('A0006', 'Norah', 'Jones', 'American singer, songwriter, and pianist', 'https://www.norahjones.com/');

Insert into song (songID, title, releaseDate, songURL) Values
('S0001', 'The Best Is Yet To Come', '1964-08-01', 'https://www.youtube.com/embed/mQIZ-Esbg_c'),
('S0002', 'New York, New York', '1980-04-01', 'https://www.youtube.com/embed/le1QF3uoQNg'),
('S0003', 'Just The Way You Are', '2010-07-10', 'https://www.youtube.com/embed/LjhCEhWiKXk'),
('S0004', 'Perfect', '2017-09-26', 'https://www.youtube.com/embed/ORrFJ63nlcA'),
('S0005', 'Try Everything', '2016-02-23', "https://www.youtube.com/embed/c6rP-YP4c5I"),
('S0006', 'Price Tag', '2011-01-31', "https://www.youtube.com/embed/qMxX-QOV9tI"),
('S0007', 'Dont Know Why', '2002-01-28','https://www.youtube.com/embed/tO4dxvguQDk'),
('S0008', 'Curtains', '2023-05-05','https://www.youtube.com/embed/YxSj3TP90SA');

Insert into songGenre(songID, genre) Values
('S0001', 'Jazz'),
('S0001', 'Swing'),
('S0002', 'Jazz'),
('S0003', 'R&B'),
('S0003', 'Pop'),
('S0004', 'Pop'),
('S0005', 'Pop'),
('S0006', 'R&B'),
('S0007', 'Pop'),
('S0007', 'Jazz'),
('S0008', 'Pop');

Insert into artistPerformsSong (artistID, songID) Values
('A0001','S0001'),
('A0001','S0002'),
('A0002','S0003'),
('A0003','S0004'),
('A0004','S0005'),
('A0005','S0006'),
('A0006','S0007'),
('A0003','S0008');

Insert into album (albumID, albumTitle) Values 
('Al001', 'It Might as Well Be Swing'), 
('Al002', 'Trilogy: Past Present Future'), 
('Al003', 'Doo-Wops & Hooligans'), 
('Al004', 'divide'), 
('Al005', 'Zootopia: Original Motion Picture Soundtrack'), 
('Al006', 'Who you are'), 
('Al007', 'Come Away with Me'),
('Al008', 'Subtract');

Insert into songInAlbum (albumID, songID) Values
('Al001', 'S0001'),
('Al002', 'S0002'), 
('Al003', 'S0003'), 
('Al004', 'S0004'),
('Al005', 'S0005'), 
('Al006', 'S0006'),
('Al007', 'S0007'),
('Al008', 'S0008');

-- Insert into rateSong (username, songID, stars, ratingDate) Values;
-- Insert into reviewSong (username, songID, reviewText, reviewDate) Values;
-- Insert into rateAlbum (username, albumID, stars) Values;
-- Insert into reviewAlbum (username, albumID, reviewText, reviewDate) Values;
-- Insert into userFanOfArtist (username, artistID) Values;


