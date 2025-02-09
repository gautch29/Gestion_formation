# controller.py
class Controller:
    def __init__(self, model):
        self.model = model

    # Méthodes d'ajout
    def add_course(self, course_name, course_code, course_description, course_duration):
        try:
            self.model.add_course(course_name, course_code, course_description, course_duration)
            return True
        except Exception:
            return False

    def add_student(self, student_name, student_identification):
        try:
            self.model.add_student(student_name, student_identification)
            return True
        except Exception:
            return False

    def add_lesson(self, lesson_date, formation_index, teacher_index, selected_participants_indices, courses, teachers):
        try:
            if formation_index == -1 or teacher_index == -1 or not selected_participants_indices:
                raise ValueError("Veuillez sélectionner tous les éléments requis.")
            lesson_course_id = courses[formation_index][0]
            teacher_id = teachers[teacher_index][0]
            lesson_id = self.model.add_lesson(lesson_date, lesson_course_id, teacher_id)
            for index in selected_participants_indices:
                participant_id = teachers[index][0]
                self.model.add_student_lesson(participant_id, lesson_id)
            return True
        except Exception:
            return False

    # Méthodes de suppression
    def remove_lesson_and_links(self, lesson_id):
        try:
            self.model.remove_lesson_and_links(lesson_id)
            return True
        except Exception:
            return False

    def remove_course(self, course_id):
        try:
            self.model.remove_course(course_id)
            return True
        except Exception:
            return False

    def remove_student_lesson(self, student_lesson_id):
        try:
            self.model.remove_student_lesson(student_lesson_id)
            return True
        except Exception:
            return False

    # Méthodes de récupération
    def get_courses(self):
        return self.model.get_courses()

    def get_students(self):
        return self.model.get_students()

    def get_lessons_date(self, lesson_date):
        return self.model.get_lessons_date(lesson_date)

    def get_student_lessons(self, student_id):
        return self.model.get_student_lessons(student_id)

    def get_lesson_participants(self, lesson_id):
        return self.model.get_lesson_participants(lesson_id)

    def get_lessons_by_module(self, course_id):
        return self.model.get_lessons_by_module(course_id)