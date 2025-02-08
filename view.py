# view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import date
from tkinter import Listbox, messagebox
import tkinter as tk

# ============================================================================
# Fonction utilitaire pour obtenir une date par défaut sous forme de chaîne
# ============================================================================
def get_default_date():
    return date.today().strftime("%d/%m/%Y")

# ============================================================================
# Page : Ajouter une séance
# ============================================================================
class AddLessonPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()

    def create_widgets(self):
        # Ligne 0 : Date de la séance (simple Entry)
        tb.Label(self, text="Date de la séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_frame = tk.Frame(self)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.date_entry = tb.Entry(date_frame, font=("Segoe UI", 12))
        self.date_entry.pack(fill="x")
        self.date_entry.insert(0, get_default_date())

        # Ligne 1 : Formation de la séance
        tb.Label(self, text="Formation de la séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.formation_combo = tb.Combobox(self, state="readonly", font=("Segoe UI", 12))
        self.formation_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Ligne 2 : Professeur de la séance
        tb.Label(self, text="Professeur de la séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.teacher_combo = tb.Combobox(self, state="readonly", font=("Segoe UI", 12))
        self.teacher_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Ligne 3 : Sélection des participants
        tb.Label(self, text="Sélectionnez les participants:", font=("Segoe UI", 12, "bold"))\
            .grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.participants_listbox = Listbox(self, selectmode="multiple", height=6, font=("Segoe UI", 12))
        self.participants_listbox.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Ligne 4 : Message de confirmation
        self.status_label = tb.Label(self, text="", bootstyle="success", font=("Segoe UI", 12))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Ligne 5 : Bouton soumettre
        btn = tb.Button(self, text="Ajouter la séance", command=self.submit_lesson, bootstyle="primary")
        btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        self.columnconfigure(1, weight=1)
        self.refresh_combos()

    def refresh_combos(self):
        courses = self.controller_obj.get_courses()
        self.courses = courses
        self.formation_combo['values'] = [course[4] for course in courses]

        teachers = self.controller_obj.get_students()
        self.teachers = teachers
        self.teacher_combo['values'] = [f"{t[2]} (ID: {t[1]})" for t in teachers]

        self.participants_listbox.delete(0, "end")
        for t in teachers:
            self.participants_listbox.insert("end", f"{t[2]} (ID: {t[1]})")

    def submit_lesson(self):
        try:
            # On récupère la date saisie dans le champ Entry
            lesson_date = self.date_entry.get().strip()
            formation_index = self.formation_combo.current()
            teacher_index = self.teacher_combo.current()
            selected_indices = self.participants_listbox.curselection()

            if formation_index == -1 or teacher_index == -1 or not selected_indices:
                raise ValueError("Veuillez sélectionner tous les éléments requis.")

            result = self.controller_obj.add_lesson(
                lesson_date, formation_index, teacher_index, selected_indices,
                self.courses, self.teachers
            )
            if result:
                self.status_label.config(text="Séance ajoutée avec succès !")
                messagebox.showinfo("Succès", "La séance a été ajoutée avec succès !")
                self.formation_combo.set('')
                self.teacher_combo.set('')
                self.participants_listbox.selection_clear(0, "end")
                self.refresh_combos()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout de la séance.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# ============================================================================
# Page : Voir les séances par date
# ============================================================================
class GetLessonsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="Date des séances:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_frame = tk.Frame(self)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.lessons_date_entry = tb.Entry(date_frame, font=("Segoe UI", 12))
        self.lessons_date_entry.pack(fill="x")
        self.lessons_date_entry.insert(0, get_default_date())
        self.lessons_date_entry.bind("<FocusOut>", lambda e: self.refresh())

        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details)

        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        btn_refresh = tb.Button(self, text="Refresh", command=self.refresh, bootstyle="info")
        btn_refresh.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        btn_delete = tb.Button(self, text="Supprimer la séance", command=self.delete_selected_lesson, bootstyle="danger")
        btn_delete.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        # Récupérer la date saisie
        lesson_date_str = self.lessons_date_entry.get().strip()
        lessons = self.controller_obj.get_lessons_date(lesson_date_str)
        self.lessons = lessons
        courses = self.controller_obj.get_courses()
        self.courses = courses
        for lesson in lessons:
            course_name = next((course[4] for course in courses if course[0] == lesson[2]), "Inconnu")
            self.listbox.insert("end", f"ID {lesson[0]} - {course_name}")

    def delete_selected_lesson(self):
        try:
            index = self.listbox.curselection()[0]
            lesson = self.lessons[index]
            if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer cette séance et tous ses liens ?"):
                self.controller_obj.remove_lesson_and_links(lesson[0])
                messagebox.showinfo("Succès", "La séance et ses liens ont été supprimés.")
                self.refresh()
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une séance à supprimer.")

    def show_lesson_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            lesson = self.lessons[index]
            course = next((c for c in self.courses if c[0] == lesson[2]), None)
            course_info = (f"Formation : {course[4]}\nCode : {course[1]}\nDescription : {course[2]}"
                           if course else "Formation inconnue")
            teachers = self.controller_obj.get_students()
            teacher = next((t for t in teachers if t[0] == lesson[3]), None)
            teacher_info = (f"Professeur : {teacher[2]} (ID: {teacher[1]})"
                            if teacher else "Professeur inconnu")
            participants = self.controller_obj.get_lesson_participants(lesson[0])
            participants_info = ("\n".join([f"{p[1]} (ID: {p[2]})" for p in participants])
                                 if participants else "Aucun participant")
            details = (f"ID Séance: {lesson[0]}\nDate: {lesson[1]}\n{course_info}\n"
                       f"{teacher_info}\nParticipants:\n{participants_info}")
            self.detail_label.config(text=details)
        except IndexError:
            self.detail_label.config(text="")

# ============================================================================
# Page : Voir les séances par personnel
# ============================================================================
class GetLessonsByPersonnelPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()
    def create_widgets(self):
        tb.Label(self, text="Sélectionnez le personnel:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.personnel_list = Listbox(self, height=4, font=("Segoe UI", 12))
        self.personnels = self.controller_obj.get_students()
        for pers in self.personnels:
            self.personnel_list.insert("end", f"{pers[2]} (ID: {pers[1]})")
        self.personnel_list.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.personnel_list.bind("<<ListboxSelect>>", self.refresh_lessons)
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details_personnel)
        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        btn_delete = tb.Button(self, text="Supprimer la séance sélectionnée", command=self.remove_link, bootstyle="danger")
        btn_delete.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
    def refresh_lessons(self, event=None):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        try:
            index = self.personnel_list.curselection()[0]
            personnel_id = self.personnels[index][0]
            lessons = self.controller_obj.get_student_lessons(personnel_id)
            self.lessons = lessons
            for les in lessons:
                self.listbox.insert("end", f"ID {les[1]} - Date: {les[2]}")
        except IndexError:
            self.listbox.delete(0, "end")
    def show_lesson_details_personnel(self, event):
        try:
            index = self.personnel_list.curselection()[0]
            personnel_id = self.personnels[index][0]
            lessons = self.controller_obj.get_student_lessons(personnel_id)
            listbox_index = self.listbox.curselection()[0]
            les = lessons[listbox_index]
            course = next((c for c in self.controller_obj.get_courses() if c[0] == les[3]), None)
            course_info = f"Formation : {course[4]}" if course else "Formation inconnue"
            detail = f"ID Séance: {les[1]}\nDate: {les[2]}\n{course_info}"
            self.detail_label.config(text=detail)
        except IndexError:
            self.detail_label.config(text="")
    def remove_link(self):
        try:
            index = self.personnel_list.curselection()[0]
            personnel_id = self.personnels[index][0]
            lessons = self.controller_obj.get_student_lessons(personnel_id)
            listbox_index = self.listbox.curselection()[0]
            link_id = lessons[listbox_index][0]
            self.controller_obj.remove_student_lesson(link_id)
            self.refresh_lessons()
            messagebox.showinfo("Succès", "La relation a été supprimée.")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une séance à supprimer.")

# ============================================================================
# Page : Ajouter un personnel
# ============================================================================
class AddStudentPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()
    def create_widgets(self):
        tb.Label(self, text="Nom du personnel:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.student_name_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.student_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tb.Label(self, text="Identification:", font=("Segoe UI", 12, "bold"))\
            .grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.student_identification_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.student_identification_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.status_label = tb.Label(self, text="", bootstyle="success", font=("Segoe UI", 12))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=5)
        btn = tb.Button(self, text="Ajouter le personnel", command=self.submit_student, bootstyle="primary")
        btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        self.columnconfigure(1, weight=1)
    def submit_student(self):
        name = self.student_name_entry.get()
        ident = self.student_identification_entry.get()
        if name and ident:
            if self.controller_obj.add_student(name, ident):
                self.student_name_entry.delete(0, "end")
                self.student_identification_entry.delete(0, "end")
                self.status_label.config(text="Personnel ajouté avec succès !")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout du personnel.")
        else:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")

# ============================================================================
# Page : Ajouter une formation
# ============================================================================
class AddCoursePage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()
    def create_widgets(self):
        tb.Label(self, text="Nom de la formation:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.course_name_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.course_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tb.Label(self, text="Code de la formation:", font=("Segoe UI", 12, "bold"))\
            .grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.course_code_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.course_code_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        tb.Label(self, text="Description:", font=("Segoe UI", 12, "bold"))\
            .grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.course_description_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.course_description_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        tb.Label(self, text="Durée:", font=("Segoe UI", 12, "bold"))\
            .grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.course_duration_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.course_duration_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.status_label = tb.Label(self, text="", bootstyle="success", font=("Segoe UI", 12))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        btn = tb.Button(self, text="Ajouter la formation", command=self.submit_course, bootstyle="primary")
        btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        self.columnconfigure(1, weight=1)
    def submit_course(self):
        name = self.course_name_entry.get()
        code = self.course_code_entry.get()
        desc = self.course_description_entry.get()
        duration = self.course_duration_entry.get()
        if name and code and desc and duration:
            if self.controller_obj.add_course(name, code, desc, duration):
                self.course_name_entry.delete(0, "end")
                self.course_code_entry.delete(0, "end")
                self.course_description_entry.delete(0, "end")
                self.course_duration_entry.delete(0, "end")
                self.status_label.config(text="Formation ajoutée avec succès !")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout de la formation.")
        else:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")

# ============================================================================
# Page : Voir les formations
# ============================================================================
class GetCoursesPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()
    def create_widgets(self):
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_course_details)
        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        btn_refresh = tb.Button(self, text="Refresh", command=self.refresh, bootstyle="info")
        btn_refresh.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        btn_delete = tb.Button(self, text="Supprimer la formation", command=self.remove_selected, bootstyle="danger")
        btn_delete.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()
    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.courses = self.controller_obj.get_courses()
        for course in self.courses:
            self.listbox.insert("end", course[4])
    def remove_selected(self):
        try:
            index = self.listbox.curselection()[0]
            course_id = self.courses[index][0]
            self.controller_obj.remove_course(course_id)
            self.refresh()
            messagebox.showinfo("Succès", "Formation supprimée avec succès !")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une formation à supprimer.")
    def show_course_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            course = self.courses[index]
            details = f"Code: {course[1]}\nDescription: {course[2]}\nDurée: {course[3]}"
            self.detail_label.config(text=details)
        except IndexError:
            self.detail_label.config(text="")

# ============================================================================
# Page : Voir le personnel
# ============================================================================
class GetStudentsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()
    def create_widgets(self):
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_student_details)
        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        btn_refresh = tb.Button(self, text="Refresh", command=self.refresh, bootstyle="info")
        btn_refresh.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()
    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.students = self.controller_obj.get_students()
        for stud in self.students:
            self.listbox.insert("end", f"{stud[2]} (ID: {stud[1]})")
    def show_student_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            details = f"Nom : {student[2]}\nIdentification : {student[1]}"
            self.detail_label.config(text=details)
        except IndexError:
            self.detail_label.config(text="")

# ============================================================================
# Fenêtre principale
# ============================================================================
class MainView(tb.Window):
    def __init__(self, controller):
        super().__init__(themename="flatly")
        self.controller_obj = controller
        self.title("Gestion des séances de formation")
        self.geometry("1200x600")
        main_frame = tb.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        self.notebook = tb.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        self.pages = {}
        self.pages['add_lesson'] = AddLessonPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['add_lesson'], text="Ajouter une séance")
        self.pages['get_lessons'] = GetLessonsPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_lessons'], text="Voir les séances par date")
        self.pages['get_lessons_by_personnel'] = GetLessonsByPersonnelPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_lessons_by_personnel'], text="Voir les séances par personnel")
        self.pages['add_student'] = AddStudentPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['add_student'], text="Ajouter un personnel")
        self.pages['add_course'] = AddCoursePage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['add_course'], text="Ajouter une formation")
        self.pages['get_courses'] = GetCoursesPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_courses'], text="Voir les formations")
        self.pages['get_students'] = GetStudentsPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_students'], text="Voir le personnel")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        frame = event.widget.nametowidget(selected_tab)
        if hasattr(frame, "refresh"):
            frame.refresh()
