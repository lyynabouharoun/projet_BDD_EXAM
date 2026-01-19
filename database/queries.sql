-- ===============================
-- 1. All exams of a formation
-- ===============================
SELECT f.nom AS formation, m.nom AS module, e.date_exam, e.heure_debut, s.nom AS salle, p.nom AS professeur
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN professeurs p ON e.prof_id = p.id
JOIN salles s ON e.salle_id = s.id
ORDER BY f.nom, e.date_exam, e.heure_debut;

-- ===============================
-- 2. Exams of a student
-- ===============================
SELECT st.nom || ' ' || st.prenom AS student, m.nom AS module, e.date_exam, e.heure_debut, s.nom AS salle
FROM inscriptions i
JOIN etudiants st ON i.etudiant_id = st.id
JOIN examens e ON i.module_id = e.module_id
JOIN modules m ON e.module_id = m.id
JOIN salles s ON e.salle_id = s.id
WHERE st.id = 123;  -- Replace 123 by student_id
ORDER BY e.date_exam, e.heure_debut;

-- ===============================
-- 3. Exams of a professor
-- ===============================
SELECT p.nom || ' ' || p.prenom AS professeur, m.nom AS module, e.date_exam, e.heure_debut, s.nom AS salle
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN professeurs p ON e.prof_id = p.id
JOIN salles s ON e.salle_id = s.id
WHERE p.id = 12   -- Replace 12 by professor_id
ORDER BY e.date_exam, e.heure_debut;

-- ===============================
-- 4. Room occupation (total exams per room)
-- ===============================
SELECT s.nom AS salle, COUNT(e.id) AS nb_examens, SUM(s.capacite) AS total_capacity
FROM salles s
LEFT JOIN examens e ON s.id = e.salle_id
GROUP BY s.nom
ORDER BY nb_examens DESC;

-- ===============================
-- 5. Professor workload (exams per professor)
-- ===============================
SELECT p.nom || ' ' || p.prenom AS professeur, COUNT(e.id) AS nb_examens
FROM professeurs p
LEFT JOIN examens e ON p.id = e.prof_id
GROUP BY p.id
ORDER BY nb_examens DESC;

-- ===============================
-- 6. Student exam conflicts
-- Detect students with two exams at the same date/time
-- ===============================
SELECT st.nom || ' ' || st.prenom AS student, e1.date_exam, e1.heure_debut, COUNT(*) AS nb_conflicts
FROM inscriptions i1
JOIN examens e1 ON i1.module_id = e1.module_id
JOIN inscriptions i2 ON i1.etudiant_id = i2.etudiant_id
JOIN examens e2 ON i2.module_id = e2.module_id
JOIN etudiants st ON i1.etudiant_id = st.id
WHERE e1.id <> e2.id
AND e1.date_exam = e2.date_exam
AND e1.heure_debut = e2.heure_debut
GROUP BY st.id, e1.date_exam, e1.heure_debut
HAVING COUNT(*) > 1
ORDER BY nb_conflicts DESC;

-- ===============================
-- 7. Professor exam conflicts
-- Detect professors assigned multiple exams at the same time
-- ===============================
SELECT p.nom || ' ' || p.prenom AS professeur, e1.date_exam, e1.heure_debut, COUNT(*) AS nb_conflicts
FROM examens e1
JOIN examens e2 ON e1.prof_id = e2.prof_id
JOIN professeurs p ON e1.prof_id = p.id
WHERE e1.id <> e2.id
AND e1.date_exam = e2.date_exam
AND e1.heure_debut = e2.heure_debut
GROUP BY p.id, e1.date_exam, e1.heure_debut
HAVING COUNT(*) > 1
ORDER BY nb_conflicts DESC;

-- ===============================
-- 8. Room capacity violations
-- Detect exams where registered students exceed room capacity
-- ===============================
SELECT e.id AS examen_id, m.nom AS module, s.nom AS salle, s.capacite, COUNT(i.etudiant_id) AS registered_students
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN salles s ON e.salle_id = s.id
JOIN inscriptions i ON i.module_id = m.id
GROUP BY e.id, m.nom, s.nom, s.capacite
HAVING COUNT(i.etudiant_id) > s.capacite
ORDER BY registered_students DESC;

-- ===============================
-- 9. Department exam statistics
-- Total exams and students per department
-- ===============================
SELECT d.nom AS departement,
       COUNT(DISTINCT e.id) AS total_exams,
       COUNT(DISTINCT i.etudiant_id) AS total_students
FROM departements d
JOIN formations f ON f.departement_id = d.id
JOIN modules m ON m.formation_id = f.id
LEFT JOIN examens e ON e.module_id = m.id
LEFT JOIN inscriptions i ON i.module_id = m.id
GROUP BY d.nom
ORDER BY total_exams DESC;

-- ===============================
-- 10. Staff login validation
-- Check if staff email exists and hash matches
-- ===============================
SELECT *
FROM staff
WHERE email='doyen@univ.com' 
AND password_hash='put_hash_here';

-- ===============================
-- 11. Student login validation
-- Check if student matricule + birthday combination exists
-- ===============================
SELECT st.id, st.nom, st.prenom
FROM etudiants st
JOIN etudiant_logins sl ON st.id = sl.etudiant_id
WHERE st.matricule='MAT000123' 
AND sl.password_hash='put_hash_here';

-- ===============================
-- 12. Exams per cycle / level
-- ===============================
SELECT f.cycle, f.niveau, COUNT(e.id) AS nb_examens
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
GROUP BY f.cycle, f.niveau
ORDER BY f.cycle, f.niveau;

-- ===============================
-- 13. Modules per formation
-- ===============================
SELECT f.nom AS formation, COUNT(m.id) AS nb_modules
FROM formations f
JOIN modules m ON m.formation_id = f.id
GROUP BY f.nom
ORDER BY nb_modules DESC;

-- ===============================
-- 14. Students per formation
-- ===============================
SELECT f.nom AS formation, COUNT(st.id) AS nb_students
FROM formations f
JOIN etudiants st ON st.formation_id = f.id
GROUP BY f.nom
ORDER BY nb_students DESC;

-- ===============================
-- 15. Exams scheduled per day
-- ===============================
SELECT e.date_exam, COUNT(e.id) AS nb_examens
FROM examens e
GROUP BY e.date_exam
ORDER BY e.date_exam;

-- ===============================
-- 16. Check professor exam distribution fairness
-- ===============================
SELECT p.nom || ' ' || p.prenom AS professeur, COUNT(e.id) AS nb_examens
FROM professeurs p
LEFT JOIN examens e ON p.id = e.prof_id
GROUP BY p.id
ORDER BY nb_examens;

-- ===============================
-- 17. Check student maximum 1 exam per day
-- ===============================
SELECT st.nom || ' ' || st.prenom AS student, e.date_exam, COUNT(e.id) AS nb_examens
FROM etudiants st
JOIN inscriptions i ON st.id = i.etudiant_id
JOIN examens e ON i.module_id = e.module_id
GROUP BY st.id, e.date_exam
HAVING COUNT(e.id) > 1
ORDER BY nb_examens DESC;

-- ===============================
-- 18. Check professor maximum 3 exams per day
-- ===============================
SELECT p.nom || ' ' || p.prenom AS professeur, e.date_exam, COUNT(e.id) AS nb_examens
FROM professeurs p
JOIN examens e ON p.id = e.prof_id
GROUP BY p.id, e.date_exam
HAVING COUNT(e.id) > 3
ORDER BY nb_examens DESC;
