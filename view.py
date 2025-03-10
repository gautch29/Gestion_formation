# view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, date
from tkinter import Listbox, messagebox
import tkinter as tk
from PIL import Image, ImageTk 
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# ------------------------------------------------------------------------------
# Fonction utilitaire pour obtenir une date par défaut sous forme de chaîne
# ------------------------------------------------------------------------------
def get_default_date():
    return date.today().strftime("%d/%m/%Y")

# ==============================================================================
# Page : Nouvelle séance (identique à AddLessonPage d'origine)
# ==============================================================================
class AddLessonPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        # Ligne 0 : Date de la séance
        tb.Label(self, text="Date de la séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_frame = tk.Frame(self)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.date_entry = tb.Entry(date_frame, font=("Segoe UI", 12))
        self.date_entry.pack(fill="x")
        self.date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        
        # Ligne 1 : Formation de la séance
        tb.Label(self, text="Module:", font=("Segoe UI", 12, "bold"))\
            .grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.formation_combo = tb.Combobox(self, state="readonly", font=("Segoe UI", 12))
        self.formation_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Ligne 2 : Professeur de la séance
        tb.Label(self, text="Moniteur de séance:", font=("Segoe UI", 12, "bold"))\
            .grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.teacher_combo = tb.Combobox(self, state="readonly", font=("Segoe UI", 12))
        self.teacher_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Ligne 3 : Sélection des participants
        tb.Label(self, text="Sélection des participants:", font=("Segoe UI", 12, "bold"))\
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
        self.formation_combo['values'] = [f"{course[1]} - {course[4]}" for course in courses]

        teachers = self.controller_obj.get_students()
        self.teachers = teachers
        # Afficher : Prénom + Nom de famille (ID: xxxx)
        self.teacher_combo['values'] = [f"{t[2]} {t[4]} (ID: {t[1]})" for t in teachers]

        sorted_participants = sorted(teachers, key=lambda t: t[2].lower())
        self.participants_listbox.delete(0, "end")
        for t in sorted_participants:
            # Afficher : Prénom + Nom de famille (ID: xxxx, Peloton: xxxx)
            self.participants_listbox.insert(
                "end",
                f"{t[2]} {t[4]} (ID: {t[1]}, Peloton: {t[5]})"
            )

    def submit_lesson(self):
        try:
            lesson_date = self.date_entry.get().strip()
            formation_index = self.formation_combo.current()
            teacher_index = self.teacher_combo.current()
            selected_indices = self.participants_listbox.curselection()

            if formation_index == -1 or teacher_index == -1 or not selected_indices:
                self.status_label.config(text="Veuillez remplir tous les champs.", bootstyle="danger")
                return

            result = self.controller_obj.add_lesson(
                lesson_date, formation_index, teacher_index, selected_indices,
                self.courses, self.teachers
            )
            if result:
                self.status_label.config(text="Séance ajoutée avec succès.", bootstyle="success")
            else:
                self.status_label.config(text="Erreur lors de l'ajout de la séance.", bootstyle="danger")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# ==============================================================================
# Page : Recherche par date (GetLessonsPage)
# ==============================================================================
class GetLessonsPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="Date des séances:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        date_frame = tk.Frame(self)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.lessons_date_entry = tb.Entry(date_frame, font=("Segoe UI", 12))
        self.lessons_date_entry.pack(fill="x")
        self.lessons_date_entry.insert(0, get_default_date())
        
        # Bouton de recherche ajouté à côté du champs date
        search_btn = tb.Button(self, text="Rechercher", command=self.refresh, bootstyle="primary")
        search_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.lessons_date_entry.bind("<FocusOut>", lambda e: self.refresh())
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details)

        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        self.btn_delete = tb.Button(self, text="Supprimer la séance", command=self.delete_selected_lesson, bootstyle="danger")
        self.btn_delete.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
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
        self.btn_delete.grid_remove()

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
            self.btn_delete.grid()  # Affiche le bouton lorsque la séance est sélectionnée
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

# ==============================================================================
# Page : Recherche par personnel (GetLessonsByPersonnelPage)
# ==============================================================================
class GetLessonsByPersonnelPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=10)
        self.controller_obj = controller
        self.navigator = navigator
        # Utilisation d'un Listbox de tkinter pour le personnel
        self.personnel_list = tk.Listbox(self, height=4, exportselection=False)
        self.personnel_list.pack(pady=5, fill="x")
        self.personnel_list.bind("<<ListboxSelect>>", self.refresh_lessons)
        self.listbox = tk.Listbox(self, width=50, height=8)
        self.listbox.pack(pady=5, fill="x")
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details_personnel)
        self.detail_label = tb.Label(self, text="", justify="left", wraplength=400)
        self.detail_label.pack(pady=5)
        self.refresh_personnel()

    def refresh_personnel(self):
        self.personnel_list.delete(0, "end")
        self.personnels = self.controller_obj.get_students()
        for pers in self.personnels:
            self.personnel_list.insert("end", f"{pers[2]} {pers[4]} (ID: {pers[1]}, Peloton: {pers[5]})")

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
                course_info = f"{course[4]} ({course[1]})" if course else "Formation inconnue"
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
            course_info = f"Formation : {course[4]} ({course[1]})" if course else "Formation inconnue"
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

# ==============================================================================
# Page : Ajouter un personnel (AddStudentPage)
# ==============================================================================
class AddStudentPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()
        
    def create_widgets(self):
        # Identification
        tb.Label(self, text="Identification:", font=("Segoe UI", 12, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ident_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.ident_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Prénom
        tb.Label(self, text="Prénom:", font=("Segoe UI", 12, "bold"))\
            .grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.prenom_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.prenom_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Nom de famille
        tb.Label(self, text="Nom de famille:", font=("Segoe UI", 12, "bold"))\
            .grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.nomfam_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.nomfam_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Peloton
        tb.Label(self, text="Peloton:", font=("Segoe UI", 12, "bold"))\
            .grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.peloton_entry = tb.Entry(self, font=("Segoe UI", 12))
        self.peloton_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Message de confirmation
        self.status_label = tb.Label(self, text="", bootstyle="success", font=("Segoe UI", 12))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Bouton d'ajout
        btn = tb.Button(self, text="Ajouter le personnel", command=self.submit_student, bootstyle="primary")
        btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        self.columnconfigure(1, weight=1)

    def submit_student(self):
        student_identification = self.ident_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        nom_de_famille = self.nomfam_entry.get().strip()
        peloton = self.peloton_entry.get().strip()

        if not (student_identification and prenom and nom_de_famille and peloton):
            self.status_label.config(text="Veuillez remplir tous les champs.", bootstyle="danger")
            return

        # On enregistre le prénom dans "student_name" et le nom de famille dans "nom_de_famille"
        result = self.controller_obj.add_student(prenom, student_identification, "", nom_de_famille, peloton)
        if result:
            self.status_label.config(text="Personnel ajouté avec succès.", bootstyle="success")
        else:
            self.status_label.config(text="Erreur lors de l'ajout du personnel.", bootstyle="danger")

# ==============================================================================
# Page : Ajouter une formation (AddCoursePage)
# ==============================================================================
class AddCoursePage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
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

# ==============================================================================
# Page : Voir les formations (GetCoursesPage)
# ==============================================================================
class GetCoursesPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_course_details)

        self.detail_label = tb.Label(
            self, text="", font=("Segoe UI", 12), 
            wraplength=400, anchor="w", justify="left"
        )
        self.detail_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.btn_delete = tb.Button(
            self, text="Supprimer la formation", 
            command=self.remove_selected, bootstyle="danger"
        )
        self.btn_delete.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()

        self.btn_edit = tb.Button(
            self, text="Modifier la formation", 
            command=self.edit_selected_course, bootstyle="warning"
        )
        self.btn_edit.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_edit.grid_remove()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.courses = self.controller_obj.get_courses()
        for course in self.courses:
            self.listbox.insert("end", course[4])
        self.btn_delete.grid_remove()
        self.btn_edit.grid_remove()

    def show_course_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            course = self.courses[index]
            details = f"Code: {course[1]}\nDescription: {course[2]}\nDurée: {course[3]}"
            self.detail_label.config(text=details)
            self.btn_delete.grid()  # affiche le bouton de suppression
            self.btn_edit.grid()    # affiche le bouton de modification
        except IndexError:
            self.detail_label.config(text="")
            self.btn_delete.grid_remove()
            self.btn_edit.grid_remove()

    def remove_selected(self):
        try:
            index = self.listbox.curselection()[0]
            course_id = self.courses[index][0]
            if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer cette formation ?"):
                if self.controller_obj.remove_course(course_id):
                    messagebox.showinfo("Succès", "Formation supprimée avec succès !")
                    self.refresh()
                else:
                    messagebox.showerror("Erreur", "La suppression a échoué.")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une formation à supprimer.")

    def edit_selected_course(self):
        try:
            index = self.listbox.curselection()[0]
            course = self.courses[index]
            edit_win = tk.Toplevel(self)
            edit_win.title("Modifier la formation")
            tk.Label(edit_win, text="Nom :").grid(row=0, column=0, padx=5, pady=5)
            name_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            name_entry.insert(0, course[4])
            tk.Label(edit_win, text="Code :").grid(row=1, column=0, padx=5, pady=5)
            code_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            code_entry.grid(row=1, column=1, padx=5, pady=5)
            code_entry.insert(0, course[1])
            tk.Label(edit_win, text="Description :").grid(row=2, column=0, padx=5, pady=5)
            desc_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            desc_entry.grid(row=2, column=1, padx=5, pady=5)
            desc_entry.insert(0, course[2])
            tk.Label(edit_win, text="Durée :").grid(row=3, column=0, padx=5, pady=5)
            duration_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
            duration_entry.insert(0, str(course[3]))

            def save_changes():
                new_name = name_entry.get().strip()
                new_code = code_entry.get().strip()
                new_desc = desc_entry.get().strip()
                try:
                    new_duration = int(duration_entry.get().strip())
                except ValueError:
                    messagebox.showwarning("Champ invalide", "La durée doit être un nombre.")
                    return
                if new_name and new_code and new_desc:
                    if self.controller_obj.update_course(course[0], new_name, new_code, new_desc, new_duration):
                        messagebox.showinfo("Succès", "Formation mise à jour avec succès.")
                        self.refresh()
                        edit_win.destroy()  # Ferme le popup
                    else:
                        messagebox.showerror("Erreur", "La modification a échoué.")
                else:
                    messagebox.showwarning("Champ manquant", "Veuillez remplir tous les champs.")
            btn_save = tb.Button(edit_win, text="Enregistrer", command=save_changes, bootstyle="primary")
            btn_save.grid(row=4, column=0, columnspan=2, pady=10)
        except IndexError:
            messagebox.showerror("Erreur", "Aucune formation sélectionnée.")

# ==============================================================================
# Page : Voir le personnel (GetStudentsPage)
# ==============================================================================
class GetStudentsPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_student_details)

        self.detail_label = tb.Label(
            self, text="", font=("Segoe UI", 12),
            wraplength=400, anchor="w", justify="left"
        )
        self.detail_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.btn_delete = tb.Button(
            self, text="Supprimer le personnel", 
            command=self.delete_selected_student, bootstyle="danger"
        )
        self.btn_delete.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_delete.grid_remove()

        self.btn_edit = tb.Button(
            self, text="Modifier le personnel", 
            command=self.edit_selected_student, bootstyle="warning"
        )
        self.btn_edit.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.btn_edit.grid_remove()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.refresh()

    def tkraise(self, aboveThis=None):
        self.refresh()  # Mise à jour de la liste dès que la page devient visible
        super().tkraise(aboveThis)
        
    def refresh(self):
        self.listbox.delete(0, "end")
        self.detail_label.config(text="")
        self.students = self.controller_obj.get_students()
        for stud in self.students:
            # Affichage : Prénom + Nom de famille (ID, Peloton)
            self.listbox.insert("end", f"{stud[2]} {stud[4]} (ID: {stud[1]}, Peloton: {stud[5]})")
        self.btn_delete.grid_remove()
        self.btn_edit.grid_remove()

    def show_student_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            details = (f"Prénom : {student[2]}\n"
                    f"Nom de famille : {student[4]}\n"
                    f"Identification : {student[1]}\n"
                    f"Peloton : {student[5]}")
            self.detail_label.config(text=details)
            self.btn_delete.grid()  # Affiche le bouton de suppression
            self.btn_edit.grid()    # Affiche le bouton de modification
        except IndexError:
            self.detail_label.config(text="")
            self.btn_delete.grid_remove()
            self.btn_edit.grid_remove()

    def delete_selected_student(self):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce personnel ?")
            if confirm:
                if self.controller_obj.remove_student(student[0]):
                    messagebox.showinfo("Succès", "Personnel supprimé avec succès.")
                    self.refresh()  # Rafraîchit la liste
                else:
                    messagebox.showerror("Erreur", "La suppression a échoué.")
        except IndexError:
            messagebox.showerror("Erreur", "Aucun personnel sélectionné.")

    def edit_selected_student(self):
        try:
            index = self.listbox.curselection()[0]
            student = self.students[index]
            edit_win = tk.Toplevel(self)
            edit_win.title("Modifier le personnel")
            
            tk.Label(edit_win, text="Identification:", font=("Segoe UI", 12)).grid(row=0, column=0, padx=5, pady=5)
            ident_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            ident_entry.grid(row=0, column=1, padx=5, pady=5)
            ident_entry.insert(0, student[1])
            
            tk.Label(edit_win, text="Prénom:", font=("Segoe UI", 12)).grid(row=1, column=0, padx=5, pady=5)
            prenom_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            prenom_entry.grid(row=1, column=1, padx=5, pady=5)
            prenom_entry.insert(0, student[2])
            
            tk.Label(edit_win, text="Nom de famille:", font=("Segoe UI", 12)).grid(row=2, column=0, padx=5, pady=5)
            nomfam_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            nomfam_entry.grid(row=2, column=1, padx=5, pady=5)
            nomfam_entry.insert(0, student[4])
            
            tk.Label(edit_win, text="Peloton:", font=("Segoe UI", 12)).grid(row=3, column=0, padx=5, pady=5)
            peloton_entry = tk.Entry(edit_win, font=("Segoe UI", 12))
            peloton_entry.grid(row=3, column=1, padx=5, pady=5)
            peloton_entry.insert(0, student[5])
            
            def save_changes():
                new_ident = ident_entry.get().strip()
                new_prenom = prenom_entry.get().strip()
                new_nomfam = nomfam_entry.get().strip()
                new_peloton = peloton_entry.get().strip()
                if new_ident and new_prenom and new_nomfam and new_peloton:
                    # Mise à jour : on passe le prénom dans student_name et le nom de famille dans nom_de_famille
                    if self.controller_obj.update_student(student[0], new_prenom, new_ident, "", new_nomfam, new_peloton):
                        messagebox.showinfo("Succès", "Personnel mis à jour avec succès.")
                        self.refresh()
                        edit_win.destroy()
                    else:
                        messagebox.showerror("Erreur", "La modification a échoué.")
                else:
                    messagebox.showwarning("Champ manquant", "Veuillez remplir tous les champs.")
            
            # Bouton d'enregistrement
            btn_save = tb.Button(edit_win, text="Enregistrer", command=save_changes, bootstyle="primary")
            btn_save.grid(row=4, column=0, columnspan=2, pady=10)
        except IndexError:
            messagebox.showerror("Erreur", "Aucun personnel sélectionné.")

# ==============================================================================
# Page : Recherche par module (GetLessonsByModulePage)
# ==============================================================================
class GetLessonsByModulePage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        # Ligne 0 : Sélection du module
        tb.Label(self, text="Module :", font=("Segoe UI", 12, "bold")) \
            .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.module_combo = tb.Combobox(self, state="readonly", font=("Segoe UI", 12))
        self.module_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        # Bouton de recherche
        search_btn = tb.Button(self, text="Rechercher", command=self.search_by_module, bootstyle="primary")
        search_btn.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        # Zone d'affichage des séances
        self.listbox = Listbox(self, font=("Segoe UI", 12))
        self.listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.show_lesson_details)
        # Zone de détails
        self.detail_label = tb.Label(self, text="", font=("Segoe UI", 12),
                                     wraplength=400, anchor="w", justify="left")
        self.detail_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.columnconfigure(1, weight=1)
        self.refresh_modules()

    def refresh_modules(self):
        courses = self.controller_obj.get_courses()
        self.courses = courses
        # Affiche "Le code de la formation - nom de la formation"
        self.module_combo['values'] = [f"{course[1]} - {course[4]}" for course in courses]

    def search_by_module(self):
        module_index = self.module_combo.current()
        if module_index == -1:
            self.detail_label.config(text="Veuillez sélectionner un module.")
            return
        course_id = self.courses[module_index][0]
        # Méthode supposée présente dans le contrôleur pour filtrer par module
        lessons = self.controller_obj.get_lessons_by_module(course_id)
        self.lessons = lessons
        teachers = self.controller_obj.get_students()
        self.teachers = teachers
        self.listbox.delete(0, "end")
        for lesson in lessons:
            course = next((c for c in self.courses if c[0] == lesson[2]), None)
            teacher = next((t for t in teachers if t[0] == lesson[3]), None)
            course_info = f"{course[4]} ({course[1]})" if course else "Formation inconnue"
            teacher_info = teacher[2] if teacher else "Formateur inconnu"
            self.listbox.insert("end", f"{course_info} - Date: {lesson[1]} - Formateur: {teacher_info}")
        if not lessons:
            self.detail_label.config(text="Aucune séance trouvée pour ce module.")
        else:
            self.detail_label.config(text="")

    def show_lesson_details(self, event):
        try:
            index = self.listbox.curselection()[0]
            lesson = self.lessons[index]
            course = next((c for c in self.courses if c[0] == lesson[2]), None)
            teacher = next((t for t in self.teachers if t[0] == lesson[3]), None)
            course_info = f"Formation : {course[4]} ({course[1]})\nDescription : {course[2]}" if course else "Formation inconnue"
            teacher_info = f"Formateur : {teacher[2]} (ID: {teacher[1]})" if teacher else "Formateur inconnu"
            participants = self.controller_obj.get_lesson_participants(lesson[0])
            participants_info = ("\n".join([f"{p[1]} (ID: {p[2]})" for p in participants])
                                 if participants else "Aucun participant")
            details = (f"ID Séance: {lesson[0]}\nDate: {lesson[1]}\n{course_info}\n"
                       f"{teacher_info}\nParticipants:\n{participants_info}")
            self.detail_label.config(text=details)
        except IndexError:
            self.detail_label.config(text="")

# ==============================================================================
# Page : Menu Principal
# ==============================================================================
class MainMenuPage(tb.Frame):
    def __init__(self, parent, controller, navigator):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()

    def create_widgets(self):
        # Utilisation d'un tk.Label classique pour le titre avec un fond sombre
        title_label = tk.Label(
            self,
            text="Menu Principal",
            font=("Segoe UI", 20, "bold"),
            bg="#000000",      # Fond noir (à adapter selon votre logo)
            fg="white"         # Texte blanc
        )
        title_label.pack(pady=10)

        btn1 = tb.Button(self, text="Nouvelle séance",
                         command=lambda: self.navigator.show_frame("AddLessonPage"),
                         bootstyle="primary")
        btn1.pack(fill="x", pady=5)
        btn2 = tb.Button(self, text="Recherche",
                         command=lambda: self.navigator.show_frame("SearchMenuPage"),
                         bootstyle="primary")
        btn2.pack(fill="x", pady=5)
        btn3 = tb.Button(self, text="Admin",
                         command=lambda: self.navigator.show_frame("AdminMenuPage"),
                         bootstyle="primary")
        btn3.pack(fill="x", pady=5)

# ==============================================================================
# Page : Menu Recherche (accueille deux boutons)
# ==============================================================================
class SearchMenuPage(tb.Frame):
    def __init__(self, parent, controller, navigator):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()
        self.back_target = "MainMenuPage"  # Retour vers le menu principal

    def create_widgets(self):
        tb.Label(self, text="Menu Recherche", font=("Segoe UI", 16, "bold")).pack(pady=10)
        btn1 = tb.Button(self, text="Recherche par date",
                         command=lambda: self.navigator.show_frame("GetLessonsPage"),
                         bootstyle="primary")
        btn1.pack(fill="x", pady=5)
        btn2 = tb.Button(self, text="Recherche par personnel",
                         command=lambda: self.navigator.show_frame("GetLessonsByPersonnelPage"),
                         bootstyle="primary")
        btn2.pack(fill="x", pady=5)
        btn3 = tb.Button(self, text="Recherche par module",
                         command=lambda: self.navigator.show_frame("GetLessonsByModulePage"),
                         bootstyle="primary")
        btn3.pack(fill="x", pady=5)
        # Nouveau bouton pour afficher le tableau croisé
        btn4 = tb.Button(self, text="Tableau croisé formations/personal",
                         command=lambda: self.navigator.show_frame("CrossTabPage"),
                         bootstyle="primary")
        btn4.pack(fill="x", pady=5)

# ==============================================================================
# Page : Menu Administration (accueille quatre boutons)
# ==============================================================================
class AdminMenuPage(tb.Frame):
    def __init__(self, parent, controller, navigator):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()
        self.back_target = "MainMenuPage"  # Retour vers le menu principal

    def create_widgets(self):
        tb.Label(self, text="Menu Admin", font=("Segoe UI", 16, "bold")).pack(pady=10)
        btn1 = tb.Button(self, text="Ajouter un personnel",
                         command=lambda: self.navigator.show_frame("AddStudentPage"),
                         bootstyle="primary")
        btn1.pack(fill="x", pady=5)
        btn2 = tb.Button(self, text="Voir le personnel",
                         command=lambda: self.navigator.show_frame("GetStudentsPage"),
                         bootstyle="primary")
        btn2.pack(fill="x", pady=5)
        btn3 = tb.Button(self, text="Voir les formations",
                         command=lambda: self.navigator.show_frame("GetCoursesPage"),
                         bootstyle="primary")
        btn3.pack(fill="x", pady=5)
        btn4 = tb.Button(self, text="Ajouter une formation",
                         command=lambda: self.navigator.show_frame("AddCoursePage"),
                         bootstyle="primary")
        btn4.pack(fill="x", pady=5)

# ==============================================================================
# Page : Tableau croisé formations / personnel (CrossTabPage)
# ==============================================================================
class CrossTabPage(tb.Frame):
    def __init__(self, parent, controller, navigator=None):
        super().__init__(parent, padding=20)
        self.controller_obj = controller
        self.navigator = navigator
        self.create_widgets()
        self.back_target = "SearchMenuPage"  # retour vers le menu recherche

    def create_widgets(self):
        tb.Label(self, text="Tableau de suivi de formation",
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        # Zone de sélection multiple pour le personnel
        selection_frame = tb.Frame(self)
        selection_frame.pack(fill="x", pady=5)
        tb.Label(selection_frame, text="Sélectionnez les personnels :", font=("Segoe UI", 12)).pack(anchor="w")
        self.personnel_listbox = tk.Listbox(selection_frame, selectmode="extended", font=("Segoe UI", 12))
        self.personnel_listbox.pack(fill="x", padx=5, pady=5)
        self.refresh_personnel_list()
        # Bouton pour générer le PDF
        btn_generate = tb.Button(self, text="Générer le PDF",
                                 command=self.generate_table, bootstyle="primary")
        btn_generate.pack(pady=10)

    def refresh_personnel_list(self):
        self.all_personnels = self.controller_obj.get_students()
        self.personnel_listbox.delete(0, tk.END)
        for pers in self.all_personnels:
            self.personnel_listbox.insert(tk.END, f"{pers[2]} {pers[4]} (ID: {pers[1]})")

    def generate_table(self):
        # Récupérer les personnels sélectionnés
        selected_indices = self.personnel_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Avertissement", "Sélectionnez au moins un personnel.")
            return
        selected_personnels = [self.all_personnels[i] for i in selected_indices]
        # Récupérer toutes les formations et tous les personnels (pour les lessons)
        courses = self.controller_obj.get_courses()
        all_students = self.controller_obj.get_students()

        # Construction des données du tableau (ligne d'en-tête + lignes de données)
        table_data = []
        header = [""]
        for course in courses:
            header.append(course[4])
        table_data.append(header)
        
        for pers in selected_personnels:
            row = [pers[2]]  # première colonne : nom du personnel
            personnel_id = pers[0]
            lessons = self.controller_obj.get_student_lessons(personnel_id)
            course_dict = {}
            for les in lessons:
                c_id = les[3]
                teacher = next((t for t in all_students if t[0] == les[4]), None)
                teacher_str = teacher[2] if teacher else "Inconnu"
                infos = f"{les[2]}\n({teacher_str})"
                course_dict.setdefault(c_id, []).append(infos)
            for course in courses:
                if course[0] in course_dict:
                    content = "\n---\n".join(course_dict[course[0]])
                else:
                    content = "Non effectué"
                row.append(content)
            table_data.append(row)

        # Configuration du PDF en portrait avec nom de fichier incluant date et heure
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"tableau_suivi_formation_{now}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                                leftMargin=20, rightMargin=20,
                                topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        elements = []

        # En-tête du document
        title = Paragraph("Tableau de suivi de formation", styles["Title"])
        generation_date = Paragraph("Date de génération : " + date.today().strftime("%d/%m/%Y"), styles["Normal"])
        elements.append(title)
        elements.append(Spacer(1, 12))
        elements.append(generation_date)
        elements.append(Spacer(1, 24))
        
        # Création de la table ReportLab
        table = Table(table_data, repeatRows=1, hAlign="CENTER")
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6)
        ])
        # Appliquer des couleurs spécifiques aux cellules en fonction du contenu
        for row_idx in range(1, len(table_data)):
            for col_idx in range(1, len(table_data[row_idx])):
                cell_text = table_data[row_idx][col_idx]
                if "Non effectué" in cell_text:
                    style.add("BACKGROUND", (col_idx, row_idx), (col_idx, row_idx), colors.salmon)
                else:
                    style.add("BACKGROUND", (col_idx, row_idx), (col_idx, row_idx), colors.lightgreen)
        table.setStyle(style)
        elements.append(table)

        try:
            doc.build(elements)
            messagebox.showinfo("Succès", f"Le PDF a été généré : {pdf_filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la génération du PDF : {e}")

# ==============================================================================
# Fenêtre principale
# ==============================================================================
class MainView(tb.Window):
    def __init__(self, controller):
        super().__init__(themename="flatly")
        self.controller_obj = controller
        self.title("Gestion des séances de formation")
        self.geometry("500x600")
        self.resizable(False, False) 

        # Suppression de l'en-tête avec le logo (ceci ne sera plus affiché en haut)
        # À la place, le logo sera affiché en arrière-plan sur chaque page.
        
        # Bouton global "Retour" (affiché lorsque la page courante définit un back_target)
        self.back_button = tb.Button(self, text="Retour", command=self.go_back, bootstyle="secondary")
        self.back_button.pack_forget()  # Masqué initialement

        container = tb.Frame(self, padding=10)
        container.pack(fill="both", expand=True)
        
        self.frames = {}
        # Création de toutes les pages en passant "self" comme navigateur
        self.frames["MainMenuPage"] = MainMenuPage(container, self.controller_obj, self)
        self.frames["AddLessonPage"] = AddLessonPage(container, self.controller_obj, self)
        self.frames["SearchMenuPage"] = SearchMenuPage(container, self.controller_obj, self)
        self.frames["GetLessonsPage"] = GetLessonsPage(container, self.controller_obj, self)
        self.frames["GetLessonsByPersonnelPage"] = GetLessonsByPersonnelPage(container, self.controller_obj, self)
        self.frames["GetLessonsByModulePage"] = GetLessonsByModulePage(container, self.controller_obj, self)
        self.frames["AdminMenuPage"] = AdminMenuPage(container, self.controller_obj, self)
        self.frames["AddStudentPage"] = AddStudentPage(container, self.controller_obj, self)
        self.frames["GetStudentsPage"] = GetStudentsPage(container, self.controller_obj, self)
        self.frames["GetCoursesPage"] = GetCoursesPage(container, self.controller_obj, self)
        self.frames["AddCoursePage"] = AddCoursePage(container, self.controller_obj, self)
        self.frames["CrossTabPage"] = CrossTabPage(container, self.controller_obj, self)

        # Définition des cibles de retour (back_target) pour les pages détaillées
        self.frames["AddLessonPage"].back_target = "MainMenuPage"
        self.frames["GetLessonsPage"].back_target = "SearchMenuPage"
        self.frames["GetLessonsByPersonnelPage"].back_target = "SearchMenuPage"
        self.frames["GetLessonsByModulePage"].back_target = "SearchMenuPage"
        self.frames["AddStudentPage"].back_target = "AdminMenuPage"
        self.frames["GetStudentsPage"].back_target = "AdminMenuPage"
        self.frames["GetCoursesPage"].back_target = "AdminMenuPage"
        self.frames["AddCoursePage"].back_target = "AdminMenuPage"
        self.frames["SearchMenuPage"].back_target = "MainMenuPage"
        self.frames["AdminMenuPage"].back_target = "MainMenuPage"
        self.frames["CrossTabPage"].back_target = "SearchMenuPage"

        # Positionnement de toutes les pages dans le même container
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            # Ajout du logo en arrière-plan sur chaque page.
            try:
                # Le logo est centré dans la page
                bg_label = tk.Label(frame, image=None)
                # Si le logo n'a pas encore été chargé, nous le chargerons ci-dessous.
                bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                bg_label.lower()
                frame.bg_label = bg_label  # Sauvegarde du label dans l'instance pour éviter la collecte de garbage
            except Exception as e:
                print("Erreur lors de l'ajout du background :", e)

        # Chargement du logo (filigrane) à utiliser en arrière-plan sur chaque page
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "LOGO_PIGR.jpeg")
            logo = Image.open(logo_path)
            # Redimensionnement du logo (ici, 500x500 comme dans l'ancienne version)
            logo = logo.resize((300, 300), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(logo)
        except Exception as e:
            print("Erreur lors du chargement du logo :", e)
            self.logo_image = None

        # Application du logo en arrière-plan sur chaque page (le label a été créé plus haut)
        if self.logo_image is not None:
            for frame in self.frames.values():
                if hasattr(frame, 'bg_label'):
                    frame.bg_label.config(image=self.logo_image)

        self.current_frame = None
        self.show_frame("MainMenuPage")
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_frame = page_name
        # Mise à jour du bouton "Retour" en fonction de l'attribut back_target
        if hasattr(frame, "back_target"):
            self.back_button.config(command=lambda: self.show_frame(frame.back_target))
            self.back_button.pack(side="top", anchor="w", padx=10, pady=5)
        else:
            self.back_button.pack_forget()

    def go_back(self):
        if self.current_frame and hasattr(self.frames[self.current_frame], "back_target"):
            self.show_frame(self.frames[self.current_frame].back_target)
