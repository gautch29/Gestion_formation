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
# Dans la classe AddLessonPage (dans view.py)

class AddLessonPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.create_widgets()

    def create_widgets(self):
        # Ligne 0 : Date de la séance (ici on utilise un Entry pour simplifier)
        tb.Label(self, text="Date de la séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_frame = tk.Frame(self)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.date_entry = tb.Entry(date_frame, font=("Segoe UI", 12))
        self.date_entry.pack(fill="x")
        self.date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        
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
        # Mise à jour des listes depuis la BDD via le contrôleur
        courses = self.controller_obj.get_courses()
        self.courses = courses
        self.formation_combo['values'] = [course[4] for course in courses]

        teachers = self.controller_obj.get_students()
        self.teachers = teachers
        self.teacher_combo['values'] = [f"{t[2]} (ID: {t[1]})" for t in teachers]

        # Tri des participants par ordre alphabétique (en comparant l'élément à l'indice 2, le nom)
        sorted_participants = sorted(teachers, key=lambda t: t[2].lower())
        self.participants_listbox.delete(0, "end")
        for t in sorted_participants:
            self.participants_listbox.insert("end", f"{t[2]} (ID: {t[1]})")

    # Méthode refresh appelée lors d'un changement d'onglet
    def refresh(self):
        self.refresh_combos()

    def submit_lesson(self):
        try:
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

        # Bouton pour supprimer la séance, créé puis masqué par défaut
        self.btn_delete = tb.Button(self, text="Supprimer la séance", command=self.delete_selected_lesson, bootstyle="danger")
        self.btn_delete.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()

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
        teachers = self.controller_obj.get_students()
        self.teachers = teachers
        for lesson in lessons:
            course = next((c for c in courses if c[0] == lesson[2]), None)
            teacher = next((t for t in teachers if t[0] == lesson[3]), None)
            course_info = f"{course[4]} ({course[1]})" if course else "Formation inconnue"
            teacher_info = teacher[2] if teacher else "Formateur inconnu"
            self.listbox.insert("end", f"{course_info} - Date: {lesson[1]} - Formateur: {teacher_info}")
        self.btn_delete.grid_remove()  # Cacher le bouton lors du rafraîchissement

    def show_lesson_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            lesson = self.lessons[index]
            course = next((c for c in self.courses if c[0] == lesson[2]), None)
            teacher = next((t for t in self.teachers if t[0] == lesson[3]), None)
            course_info = (f"Formation : {course[4]} ({course[1]})\nDescription : {course[2]}"
                           if course else "Formation inconnue")
            teacher_info = (f"Formateur : {teacher[2]} (ID: {teacher[1]})"
                            if teacher else "Formateur inconnu")
            participants = self.controller_obj.get_lesson_participants(lesson[0])
            participants_info = ("\n".join([f"{p[1]} (ID: {p[2]})" for p in participants])
                                 if participants else "Aucun participant")
            details = (f"ID Séance: {lesson[0]}\nDate: {lesson[1]}\n{course_info}\n"
                       f"{teacher_info}\nParticipants:\n{participants_info}")
            self.detail_label.config(text=details)
            self.btn_delete.grid()  # Afficher le bouton lorsque la séance est sélectionnée
        except IndexError:
            self.detail_label.config(text="")
            self.btn_delete.grid_remove()

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

# ============================================================================
# Page : Voir les séances par personnel
# ============================================================================
class GetLessonsByPersonnelPage(tb.Frame):
    def __init__(self, master, controller_obj):
        super().__init__(master, padding=10)
        self.controller_obj = controller_obj
        # Utilisation du Listbox de tkinter à la place de tb.Listbox
        self.personnel_list = tk.Listbox(self, height=4, exportselection=False)
        self.personnel_list.pack(pady=5, fill="x")
        self.personnel_list.bind("<<ListboxSelect>>", self.refresh_lessons)
        self.listbox = tk.Listbox(self, width=50, height=8)
        self.listbox.pack(pady=5, fill="x")
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details_personnel)
        self.detail_label = tb.Label(self, text="", justify="left", wraplength=400)
        self.detail_label.pack(pady=5)
        self.refresh_personnel()

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

    def refresh_personnel(self):
        self.personnel_list.delete(0, "end")
        self.personnels = self.controller_obj.get_students()
        for pers in self.personnels:
            self.personnel_list.insert("end", f"{pers[2]} (ID: {pers[1]})")

    def refresh_lessons(self, event=None):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        try:
            index = self.personnel_list.curselection()[0]
            personnel_id = self.personnels[index][0]
            lessons = self.controller_obj.get_student_lessons(personnel_id)
            self.lessons = lessons
            courses = self.controller_obj.get_courses()
            teachers = self.controller_obj.get_students()
            for les in lessons:
                course = next((c for c in courses if c[0] == les[3]), None)
                teacher = next((t for t in teachers if t[0] == les[4]), None)
                if course:
                    course_info = f"{course[4]} ({course[1]})"
                else:
                    course_info = "Formation inconnue"
                teacher_info = teacher[2] if teacher else "Formateur inconnu"
                display_text = f"{course_info} - Date: {les[2]} - Formateur: {teacher_info}"
                self.listbox.insert("end", display_text)
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
            teacher = next((t for t in self.controller_obj.get_students() if t[0] == les[4]), None)
            if course:
                course_info = f"Formation : {course[4]} ({course[1]})"
            else:
                course_info = "Formation inconnue"
            teacher_info = f"Formateur : {teacher[2]}" if teacher else "Formateur inconnu"
            detail = f"Date : {les[2]}\n{course_info}\n{teacher_info}"
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

        # Bouton pour supprimer la formation, créé puis masqué par défaut
        self.btn_delete = tb.Button(self, text="Supprimer la formation", command=self.remove_selected, bootstyle="danger")
        self.btn_delete.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.courses = self.controller_obj.get_courses()
        for course in self.courses:
            self.listbox.insert("end", course[4])
        self.btn_delete.grid_remove()  # Masquer le bouton lors du rafraîchissement

    def show_course_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            course = self.courses[index]
            details = f"Code: {course[1]}\nDescription: {course[2]}\nDurée: {course[3]}"
            self.detail_label.config(text=details)
            self.btn_delete.grid()  # Afficher le bouton lorsque la formation est sélectionnée
        except IndexError:
            self.detail_label.config(text="")
            self.btn_delete.grid_remove()

    def remove_selected(self):
        try:
            index = self.listbox.curselection()[0]
            course_id = self.courses[index][0]
            self.controller_obj.remove_course(course_id)
            messagebox.showinfo("Succès", "Formation supprimée avec succès !")
            self.refresh()
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une formation à supprimer.")

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

        # Bouton pour supprimer le personnel (créé puis masqué)
        self.btn_delete = tb.Button(self, text="Supprimer le personnel", command=self.delete_selected_student, bootstyle="danger")
        self.btn_delete.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()  # Masquer le bouton par défaut

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.students = self.controller_obj.get_students()
        for stud in self.students:
            self.listbox.insert("end", f"{stud[2]} (ID: {stud[1]})")
        self.btn_delete.grid_remove()  # On cache le bouton lors du rafraîchissement

    def show_student_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            details = f"Nom : {student[2]}\nIdentification : {student[1]}"
            self.detail_label.config(text=details)
            self.btn_delete.grid()  # Afficher le bouton lorsque le personnel est sélectionné
        except IndexError:
            self.detail_label.config(text="")
            self.btn_delete.grid_remove()

    def delete_selected_student(self):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer ce personnel et tous ses liens ?"):
                self.controller_obj.remove_student_and_links(student[0])
                messagebox.showinfo("Succès", "Le personnel et ses liens ont été supprimés.")
                self.refresh()
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez un personnel à supprimer.")

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
        self.pages['add_course'] = AddCoursePage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['add_course'], text="Ajouter une formation")
        self.pages['get_courses'] = GetCoursesPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_courses'], text="Voir les formations")
        self.pages['add_student'] = AddStudentPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['add_student'], text="Ajouter un personnel")
        self.pages['get_students'] = GetStudentsPage(self.notebook, self.controller_obj)
        self.notebook.add(self.pages['get_students'], text="Voir le personnel")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        frame = event.widget.nametowidget(selected_tab)
        if hasattr(frame, "refresh"):
            frame.refresh()
