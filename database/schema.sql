-- ================================
-- DATABASE SCHEMA
-- Exam Planning System
-- Faculty of Science
-- ================================

-- ENUMS
CREATE TYPE cycle_type AS ENUM ('LICENCE','MASTER','INGENIEUR','MEDECINE');
CREATE TYPE room_type AS ENUM ('AMPHI','SALLE');

-- DEPARTEMENTS
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

-- FORMATIONS
CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    cycle cycle_type NOT NULL,
    niveau INTEGER NOT NULL,
    departement_id INTEGER REFERENCES departements(id)
);

-- MODULES
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    formation_id INTEGER REFERENCES formations(id),
    semestre INTEGER CHECK (semestre IN (1,2)),
    credits INTEGER DEFAULT 3
);

-- PROFESSORS
CREATE TABLE professeurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    specialite VARCHAR(100),
    departement_id INTEGER REFERENCES departements(id)
);

-- STUDENTS
CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE,
    nom VARCHAR(100),
    formation_id INTEGER REFERENCES formations(id)
);

-- ENROLLMENTS
CREATE TABLE inscriptions (
    etudiant_id INTEGER REFERENCES etudiants(id),
    module_id INTEGER REFERENCES modules(id),
    PRIMARY KEY (etudiant_id, module_id)
);

-- BUILDINGS
CREATE TABLE batiments (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50)
);

-- ROOMS
CREATE TABLE salles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50),
    capacite INTEGER,
    type room_type,
    batiment_id INTEGER REFERENCES batiments(id)
);

-- EXAMS
CREATE TABLE examens (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id),
    prof_id INTEGER REFERENCES professeurs(id),
    salle_id INTEGER REFERENCES salles(id),
    date_exam DATE,
    heure_debut TIME,
    duree_minutes INTEGER
);

-- CONSTRAINTS (NO CONFLICTS)
CREATE UNIQUE INDEX unique_salle_time
ON examens (salle_id, date_exam, heure_debut);

CREATE UNIQUE INDEX unique_prof_time
ON examens (prof_id, date_exam, heure_debut);
