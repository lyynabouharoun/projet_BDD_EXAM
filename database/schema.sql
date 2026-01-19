-- ================================
-- DATABASE SCHEMA
-- Exam Planning System
-- Faculty of Science
-- ================================

-- ENUMS
CREATE TYPE cycle_type AS ENUM ('LICENCE','MASTER','INGENIEUR','MEDECINE');
CREATE TYPE room_type AS ENUM ('AMPHI','SALLE');
CREATE TYPE staff_role AS ENUM ('ADMIN','DOYEN','VICE_DOYEN','CHEF_DEPARTEMENT');

-- ================================
-- DEPARTMENTS
-- ================================
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

-- ================================
-- FORMATIONS
-- ================================
CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    cycle cycle_type NOT NULL,
    niveau INTEGER NOT NULL,
    departement_id INTEGER REFERENCES departements(id)
);

-- ================================
-- MODULES
-- ================================
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    formation_id INTEGER REFERENCES formations(id),
    semestre INTEGER CHECK (semestre IN (1,2)),
    credits INTEGER DEFAULT 3,
    pre_req_id INTEGER REFERENCES modules(id)
);

-- ================================
-- STAFF USERS
-- ================================
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL, -- store hashed password
    role staff_role NOT NULL,
    departement_id INTEGER REFERENCES departements(id)
);

-- ================================
-- PROFESSORS
-- ================================
CREATE TABLE professeurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    specialite VARCHAR(100),
    departement_id INTEGER REFERENCES departements(id)
);

-- ================================
-- STUDENTS
-- ================================
CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    date_naissance DATE NOT NULL,
    formation_id INTEGER REFERENCES formations(id)
);

-- ================================
-- STUDENT LOGIN
-- ================================
CREATE TABLE etudiant_logins (
    etudiant_id INTEGER PRIMARY KEY REFERENCES etudiants(id),
    password_hash VARCHAR(256) NOT NULL -- could be derived from matricule + birthday
);

-- ================================
-- ENROLLMENTS
-- ================================
CREATE TABLE inscriptions (
    etudiant_id INTEGER REFERENCES etudiants(id),
    module_id INTEGER REFERENCES modules(id),
    PRIMARY KEY (etudiant_id, module_id)
);

-- ================================
-- BUILDINGS
-- ================================
CREATE TABLE batiments (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50)
);

-- ================================
-- ROOMS
-- ================================
CREATE TABLE salles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50),
    capacite INTEGER,
    type room_type,
    batiment_id INTEGER REFERENCES batiments(id)
);

-- ================================
-- EXAMS
-- ================================
CREATE TABLE examens (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id),
    prof_id INTEGER REFERENCES professeurs(id),
    salle_id INTEGER REFERENCES salles(id),
    date_exam DATE NOT NULL,
    heure_debut TIME NOT NULL,
    duree_minutes INTEGER NOT NULL
);

-- ================================
-- CONSTRAINTS (NO CONFLICTS)
-- ================================
-- Unique room + date + time
CREATE UNIQUE INDEX unique_salle_time
ON examens (salle_id, date_exam, heure_debut);

-- Unique professor + date + time
CREATE UNIQUE INDEX unique_prof_time
ON examens (prof_id, date_exam, heure_debut);

-- Optional: Unique student exam per day (constraint)
-- This is an advanced check, can be enforced in code or triggers:
-- CREATE UNIQUE INDEX unique_student_exam_day
-- ON examens (etudiant_id, date_exam);  -- requires join with inscriptions

