-- Création table users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    bio VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'trusted', 'admin')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Création table libraries
CREATE TABLE IF NOT EXISTS libraries (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    visibility VARCHAR(20) NOT NULL DEFAULT 'private' CHECK (visibility IN ('public', 'private')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Création table franchises
CREATE TABLE IF NOT EXISTS franchises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Création table media
CREATE TABLE IF NOT EXISTS media (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('film', 'serie')),
    release_year SMALLINT,
    duration SMALLINT,
    synopsis TEXT,
    cover_image_url VARCHAR,
    trailer_url VARCHAR,
    library_id INT NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
    franchise_id INT REFERENCES franchises(id) ON DELETE SET NULL,
    franchise_order INT,
    visibility VARCHAR(20) NOT NULL CHECK (visibility IN ('public', 'private')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Création table persons (Acteurs, Réalisateurs, etc.)
CREATE TABLE IF NOT EXISTS persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birthdate DATE
);

-- Création table media_persons (Table de liaison Média à Personnes)
CREATE TABLE IF NOT EXISTS media_persons (
    media_id INT NOT NULL REFERENCES media(id) ON DELETE CASCADE,
    person_id INT NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    role VARCHAR(50),
    character_name VARCHAR(255),
    PRIMARY KEY (media_id, person_id, role)
);

-- Création table genres
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Création table media_genres (Table de liaison Média à Genres)
CREATE TABLE IF NOT EXISTS media_genres (
    media_id INT NOT NULL REFERENCES media(id) ON DELETE CASCADE,
    genre_id INT NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (media_id, genre_id)
);

-- ======
-- INSERTION DES DONNÉES DE TEST
-- ======
INSERT INTO users (username, email, password, bio, role) VALUES
('admin', 'admin@admin.admin', '$argon2id$v=19$m=65536,t=3,p=4$nPKF8ls1F9R0rKd1Hu47FQ$3JS3nmpp9MrT1UtrEgqi3NcYQ7c7BvyOhTTytAmWVbg', 'Administrateur de la vidéothèque', 'admin'),
('user', 'user@user.user', '$argon2id$v=19$m=65536,t=3,p=4$sxwfCqtWjiCNC9uBju592Q$4P3mKSfQLH/hwwtC1JMe27CuweaOY9vmj8e7FEfrlpg', 'Utilisateur standard', 'user'),
('trusted', 'trusted@trusted.trusted', '$argon2id$v=19$m=65536,t=3,p=4$XQDonOMz9sf8a3zNh/+2xg$ePNS6gOC0xUfXxsLrkjDBb+2zfZzLVoAhLWuV5L88C4', 'Utilisateur de confiance', 'trusted'),
('alice', 'alice@example.com', '$argon2id$v=19$m=65536,t=3,p=4$qMaLnJNjSFnRJ15Vlg1lrQ$Qr+MgbDptWAskQYCzGjPOmaDiaxWVExLzssxbccfsRA', 'Juste un fan de Film', 'user'),
('bob', 'bob@example.com', '$argon2id$v=19$m=65536,t=3,p=4$qMaLnJNjSFnRJ15Vlg1lrQ$Qr+MgbDptWAskQYCzGjPOmaDiaxWVExLzssxbccfsRA', 'Fan de séries, bof les films...', 'user');

INSERT INTO genres (name) VALUES
('Action'), ('Aventure'), ('Animation'), ('Comédie'), ('Crime'), ('Documentaire'),
('Drame'), ('Fantastique'), ('Horreur'), ('Mystère'), ('Romance'), ('Science-Fiction'),
('Thriller'), ('Western'), ('Guerre'), ('Biographie'), ('Histoire'), ('Musical');

INSERT INTO franchises (name, description) VALUES
('Star Wars', 'La saga épique de la galaxie lointaine'),
('Marvel Cinematic Universe', 'L''univers cinématographique Marvel'),
('Le Seigneur des Anneaux', 'L''adaptation cinématographique de Tolkien'),
('Harry Potter', 'Les aventures du sorcier à lunettes'),
('James Bond', 'Les missions de l''agent 007');

INSERT INTO persons (name, birthdate) VALUES
('Harrison Ford', '1942-07-13'),
('Mark Hamill', '1951-09-25'),
('Carrie Fisher', '1956-10-21'),
('Robert Downey Jr.', '1965-04-04'),
('Chris Evans', '1981-06-13'),
('Scarlett Johansson', '1984-11-22'),
('Elijah Wood', '1981-01-28'),
('Ian McKellen', '1939-05-25'),
('Daniel Radcliffe', '1989-07-23'),
('Emma Watson', '1990-04-15'),
('Sean Connery', '1930-08-25'),
('Pierce Brosnan', '1953-05-16'),
('Christopher Nolan', '1970-07-30'),
('Quentin Tarantino', '1963-03-27'),
('Steven Spielberg', '1946-12-18');

INSERT INTO libraries (owner_id, name, description, visibility) VALUES
(1, 'Ma Collection Personnelle', NULL, 'private'),
(1, 'Films Classiques', 'Ma sélection de films classiques', 'public'),
(4, 'Vidéothèque d''Alice', 'Mes films favoris', 'private'),
(5, 'Séries que je dois regarder', 'Ma liste de séries', 'public'),
(3, 'Collection Trusted pour test', 'Vidéothèque de l''utilisateur de confiance de test', 'public');

INSERT INTO media (title, type, release_year, duration, synopsis, library_id, franchise_id, franchise_order, visibility) VALUES
('Star Wars: Episode IV - Un Nouvel Espoir', 'film', 1977, 121, 'Luke Skywalker rejoint la rébellion pour sauver la princesse Leia.', 1, 1, 1, 'public'),
('Iron Man', 'film', 2008, 126, 'Tony Stark devient Iron Man après avoir été kidnappé.', 1, 2, 1, 'public'),
('Le Seigneur des Anneaux: La Communauté de l''Anneau', 'film', 2001, 178, 'Frodon entreprend un voyage pour détruire l''Anneau Unique.', 2, 3, 1, 'public'),
('Harry Potter à l''école des sorciers', 'film', 2001, 152, 'Harry découvre qu''il est un sorcier et entre à Poudlard.', 3, 4, 1, 'public'),
('Game of Thrones', 'serie', 2011, NULL, 'Les familles nobles se battent pour le Trône de Fer.', 4, NULL, NULL, 'public'),
('Breaking Bad', 'serie', 2008, NULL, 'Un professeur de chimie devient fabricant de méthamphétamine.', 4, NULL, NULL, 'public'),
('Inception', 'film', 2010, 148, 'Un voleur spécialisé dans l''extraction de secrets via les rêves.', 2, NULL, NULL, 'public'),
('Pulp Fiction', 'film', 1994, 154, 'Plusieurs histoires de crime entrelacées à Los Angeles.', 2, NULL, NULL, 'public');

INSERT INTO media_genres (media_id, genre_id) VALUES
(1, 12), (1, 2), (1, 1),
(2, 1), (2, 12), (2, 2),
(3, 8), (3, 2), (3, 7),
(4, 8), (4, 2),
(5, 7), (5, 8), (5, 2),
(6, 7), (6, 5), (6, 13),
(7, 12), (7, 1), (7, 13),
(8, 5), (8, 7), (8, 13);

INSERT INTO media_persons (media_id, person_id, role, character_name) VALUES
(1, 2, 'acteur', 'Luke Skywalker'),
(1, 1, 'acteur', 'Han Solo'),
(1, 3, 'acteur', 'Princesse Leia'),
(2, 4, 'acteur', 'Tony Stark / Iron Man'),
(3, 7, 'acteur', 'Frodon Sacquet'),
(3, 8, 'acteur', 'Gandalf'),
(4, 9, 'acteur', 'Harry Potter'),
(4, 10, 'acteur', 'Hermione Granger'),
(7, 13, 'réalisateur', NULL), 
(8, 14, 'réalisateur', NULL);