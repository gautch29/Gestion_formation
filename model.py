# model.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self, db_file='bdd_formations.db'):
        self.conn = sqlite3.connect(db_file)
        self.c = self.conn.cursor()
        self.create_database()

    def create_database(self):
        try:
            # Création de la table des formations
            self.c.execute('''CREATE TABLE IF NOT EXISTS courses
                              (course_id INTEGER PRIMARY KEY,
                               course_code TEXT,
                               course_description TEXT,
                               course_duration INTEGER,
                               course_name TEXT)''')
            # Création de la table du personnel
            self.c.execute('''CREATE TABLE IF NOT EXISTS students
                              (student_id INTEGER PRIMARY KEY,
                               student_identification TEXT,
                               student_name TEXT)''')
            # Création de la table des séances
            self.c.execute('''CREATE TABLE IF NOT EXISTS lessons
                              (lesson_id INTEGER PRIMARY KEY,
                               lesson_date TEXT,
                               lesson_course_id INTEGER,
                               teacher_id INTEGER)''')
            # Vérification (et ajout) de la colonne teacher_id si nécessaire
            self.c.execute("PRAGMA table_info(lessons)")
            columns = [col[1] for col in self.c.fetchall()]
            if "teacher_id" not in columns:
                self.c.execute("ALTER TABLE lessons ADD COLUMN teacher_id INTEGER")
                self.conn.commit()
            # Création de la table de liaison entre étudiants et séances
            self.c.execute('''CREATE TABLE IF NOT EXISTS students_lessons
                              (student_lesson_id INTEGER PRIMARY KEY,
                               student_id INTEGER,
                               lesson_id INTEGER)''')
            self.conn.commit()
            logging.info("Base de données initialisée avec succès.")
        except Exception as e:
            logging.error("Erreur lors de la création de la base de données : %s", e)

    # Méthodes d'insertion
    def add_course(self, course_name, course_code, course_description, course_duration):
        try:
            self.c.execute('''INSERT INTO courses (course_name, course_code, course_description, course_duration)
                              VALUES (?, ?, ?, ?)''',
                           (course_name, course_code, course_description, course_duration))
            self.conn.commit()
            logging.info("Formation ajoutée : %s", course_name)
            return self.c.lastrowid
        except Exception as e:
            logging.error("Erreur lors de l'ajout de la formation : %s", e)
            raise e

    def add_student(self, student_name, student_identification):
        try:
            self.c.execute('''INSERT INTO students (student_name, student_identification)
                              VALUES (?, ?)''', (student_name, student_identification))
            self.conn.commit()
            logging.info("Personnel ajouté : %s", student_name)
            return self.c.lastrowid
        except Exception as e:
            logging.error("Erreur lors de l'ajout du personnel : %s", e)
            raise e

    def add_lesson(self, lesson_date, lesson_course_id, teacher_id):
        try:
            self.c.execute('''INSERT INTO lessons (lesson_date, lesson_course_id, teacher_id)
                              VALUES (?, ?, ?)''', (lesson_date, lesson_course_id, teacher_id))
            self.conn.commit()
            logging.info("Séance ajoutée le %s", lesson_date)
            return self.c.lastrowid
        except Exception as e:
            logging.error("Erreur lors de l'ajout de la séance : %s", e)
            raise e

    def add_student_lesson(self, student_id, lesson_id):
        try:
            self.c.execute('''INSERT INTO students_lessons (student_id, lesson_id)
                              VALUES (?, ?)''', (student_id, lesson_id))
            self.conn.commit()
            logging.info("Lien ajouté entre étudiant %s et séance %s", student_id, lesson_id)
            return self.c.lastrowid
        except Exception as e:
            logging.error("Erreur lors de l'ajout du lien étudiant-séance : %s", e)
            raise e

    # Méthodes de sélection
    def get_courses(self):
        self.c.execute('''SELECT * FROM courses''')
        return self.c.fetchall()

    def get_students(self):
        self.c.execute('''SELECT * FROM students''')
        return self.c.fetchall()

    def get_lessons(self):
        self.c.execute('''SELECT * FROM lessons''')
        return self.c.fetchall()

    def get_lessons_date(self, lesson_date):
        self.c.execute('''SELECT * FROM lessons WHERE lesson_date = ?''', (lesson_date,))
        return self.c.fetchall()

    def get_student_lessons(self, student_id):
        self.c.execute('''SELECT sl.student_lesson_id, l.lesson_id, l.lesson_date, l.lesson_course_id, l.teacher_id 
                          FROM students_lessons sl 
                          JOIN lessons l ON sl.lesson_id = l.lesson_id 
                          WHERE sl.student_id = ?''', (student_id,))
        return self.c.fetchall()

    def get_lesson_participants(self, lesson_id):
        self.c.execute('''SELECT sl.student_lesson_id, s.student_name, s.student_identification 
                          FROM students_lessons sl 
                          JOIN students s ON sl.student_id = s.student_id 
                          WHERE sl.lesson_id = ?''', (lesson_id,))
        return self.c.fetchall()

    def get_lessons_by_module(self, course_id):
        self.c.execute('''SELECT * FROM lessons WHERE lesson_course_id = ?''', (course_id,))
        return self.c.fetchall()

    # Méthodes de suppression
    def remove_course(self, course_id):
        try:
            self.c.execute('''DELETE FROM courses WHERE course_id = ?''', (course_id,))
            self.conn.commit()
            logging.info("Formation supprimée : %s", course_id)
        except Exception as e:
            logging.error("Erreur lors de la suppression de la formation : %s", e)
            raise e

    def remove_student(self, student_id):
        try:
            self.c.execute('''DELETE FROM students WHERE student_id = ?''', (student_id,))
            self.conn.commit()
            logging.info("Personnel supprimé : %s", student_id)
        except Exception as e:
            logging.error("Erreur lors de la suppression du personnel : %s", e)
            raise e

    def remove_lesson(self, lesson_id):
        try:
            self.c.execute('''DELETE FROM lessons WHERE lesson_id = ?''', (lesson_id,))
            self.conn.commit()
            logging.info("Séance supprimée : %s", lesson_id)
        except Exception as e:
            logging.error("Erreur lors de la suppression de la séance : %s", e)
            raise e

    def remove_student_lesson(self, student_lesson_id):
        try:
            self.c.execute('''DELETE FROM students_lessons WHERE student_lesson_id = ?''', (student_lesson_id,))
            self.conn.commit()
            logging.info("Lien étudiant-séance supprimé : %s", student_lesson_id)
        except Exception as e:
            logging.error("Erreur lors de la suppression du lien étudiant-séance : %s", e)
            raise e

    def remove_lesson_and_links(self, lesson_id):
        try:
            # Supprime d'abord les liens, puis la séance
            self.c.execute('DELETE FROM students_lessons WHERE lesson_id = ?', (lesson_id,))
            self.c.execute('DELETE FROM lessons WHERE lesson_id = ?', (lesson_id,))
            self.conn.commit()
            logging.info("Séance et ses liens supprimés : %s", lesson_id)
        except Exception as e:
            logging.error("Erreur lors de la suppression de la séance et de ses liens : %s", e)
            raise e

    # Méthodes de mise à jour
    def update_course(self, course_id, course_name, course_code, course_description, course_duration):
        try:
            self.c.execute('''UPDATE courses
                              SET course_name = ?, course_code = ?, course_description = ?, course_duration = ?
                              WHERE course_id = ?''',
                           (course_name, course_code, course_description, course_duration, course_id))
            self.conn.commit()
            logging.info("Formation %s mise à jour", course_id)
            return True
        except Exception as e:
            logging.error("Erreur lors de la mise à jour de la formation : %s", e)
            raise e

    def update_student(self, student_id, student_name, student_identification):
        try:
            self.c.execute('''UPDATE students
                              SET student_name = ?, student_identification = ?
                              WHERE student_id = ?''',
                           (student_name, student_identification, student_id))
            self.conn.commit()
            logging.info("Personnel %s mis à jour", student_id)
            return True
        except Exception as e:
            logging.error("Erreur lors de la mise à jour du personnel : %s", e)
            raise e

    def update_lesson(self, lesson_id, lesson_date, lesson_course_id, teacher_id):
        try:
            self.c.execute('''UPDATE lessons
                              SET lesson_date = ?, lesson_course_id = ?, teacher_id = ?
                              WHERE lesson_id = ?''',
                           (lesson_date, lesson_course_id, teacher_id, lesson_id))
            self.conn.commit()
            logging.info("Séance %s mise à jour", lesson_id)
            return True
        except Exception as e:
            logging.error("Erreur lors de la mise à jour de la séance : %s", e)
            raise e

    def close(self):
        self.conn.close()
