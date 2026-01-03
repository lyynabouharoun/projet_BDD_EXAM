-- ===============================
-- USEFUL QUERIES
-- ===============================

-- 1. All exams of a formation
SELECT f.nom, m.nom AS module, e.date_exam, e.heure_debut
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
ORDER BY e.date_exam;

-- 2. Room occupation
SELECT s.nom, COUNT(e.id) AS nb_examens
FROM salles s
LEFT JOIN examens e ON s.id = e.salle_id
GROUP BY s.nom;

-- 3. Professor workload
SELECT p.nom, COUNT(e.id) AS nb_examens
FROM professeurs p
LEFT JOIN examens e ON p.id = e.prof_id
GROUP BY p.nom;

-- 4. Conflict detection (students)
SELECT i.etudiant_id, e1.date_exam, e1.heure_debut
FROM inscriptions i
JOIN examens e1 ON i.module_id = e1.module_id
JOIN inscriptions i2 ON i.etudiant_id = i2.etudiant_id
JOIN examens e2 ON i2.module_id = e2.module_id
WHERE e1.id <> e2.id
AND e1.date_exam = e2.date_exam
AND e1.heure_debut = e2.heure_debut;
