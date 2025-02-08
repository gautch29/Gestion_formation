import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date

def create_database():
    # Crée la table des formations
    c.execute('''CREATE TABLE IF NOT EXISTS courses
                    (course_id INTEGER PRIMARY KEY,
                     course_code TEXT,
                     course_description TEXT,
                     course_duration INTEGER,
                     course_name TEXT)''')
    # Crée la table du personnel
    c.execute('''CREATE TABLE IF NOT EXISTS students
                    (student_id INTEGER PRIMARY KEY,
                     student_identification TEXT,
                     student_name TEXT)''')
    # Crée la table des séances (si la table existe déjà, elle ne sera pas recréée)
    c.execute('''CREATE TABLE IF NOT EXISTS lessons
                    (lesson_id INTEGER PRIMARY KEY,
                     lesson_date TEXT,
                     lesson_course_id INTEGER)''')
    # Rajoute la colonne teacher_id si elle n'existe pas encore dans lessons
    c.execute("PRAGMA table_info(lessons)")
    columns = [col[1] for col in c.fetchall()]
    if "teacher_id" not in columns:
         c.execute("ALTER TABLE lessons ADD COLUMN teacher_id INTEGER")
         conn.commit()
    # Crée la table de liaison entre personnel et séances
    c.execute('''CREATE TABLE IF NOT EXISTS students_lessons
                    (student_lesson_id INTEGER PRIMARY KEY,
                     student_id INTEGER,
                     lesson_id INTEGER)''')

def add_course(course_name, course_code, course_description, course_duration):
    c.execute('''INSERT INTO courses (course_name, course_code, course_description, course_duration) 
                 VALUES (?, ?, ?, ?)''', (course_name, course_code, course_description, course_duration))
    conn.commit()

def add_student(student_name, student_identification):
    c.execute('''INSERT INTO students (student_name, student_identification) 
                 VALUES (?, ?)''', (student_name, student_identification))
    conn.commit()

def add_lesson(lesson_date, lesson_course_id, teacher_id):
    c.execute('''INSERT INTO lessons (lesson_date, lesson_course_id, teacher_id) 
                 VALUES (?, ?, ?)''', (lesson_date, lesson_course_id, teacher_id))
    conn.commit()
    return c.lastrowid

def add_student_lesson(student_id, lesson_id):
    c.execute('''INSERT INTO students_lessons (student_id, lesson_id) 
                 VALUES (?, ?)''', (student_id, lesson_id))
    conn.commit()

def get_courses():
    c.execute('''SELECT * FROM courses''')
    return c.fetchall()

def get_students():
    c.execute('''SELECT * FROM students''')
    return c.fetchall()

def get_lessons():
    c.execute('''SELECT * FROM lessons''')
    return c.fetchall()

def get_lessons_date(lesson_date):
    c.execute('''SELECT * FROM lessons WHERE lesson_date = ?''', (lesson_date,))
    return c.fetchall()

def get_lessons_by_personnel(personnel_id):
    c.execute('''SELECT * FROM lessons WHERE lesson_student_id = ?''', (personnel_id,))
    return c.fetchall()

def remove_course(course_id):
    c.execute('''DELETE FROM courses WHERE course_id = ?''', (course_id,))
    conn.commit()

def remove_student(student_id):
    c.execute('''DELETE FROM students WHERE student_id = ?''', (student_id,))
    conn.commit()

def remove_lesson(lesson_id):
    c.execute('''DELETE FROM lessons WHERE lesson_id = ?''', (lesson_id,))
    conn.commit()

def remove_student_lesson(student_lesson_id):
    c.execute('''DELETE FROM students_lessons WHERE student_lesson_id = ?''', (student_lesson_id,))
    conn.commit()


def remove_lesson_and_links(lesson_id):
    # Supprime tous les liens entre personnels et la séance
    c.execute('DELETE FROM students_lessons WHERE lesson_id = ?', (lesson_id,))
    # Supprime la séance
    c.execute('DELETE FROM lessons WHERE lesson_id = ?', (lesson_id,))
    conn.commit()

# Connexion à la base de données
conn = sqlite3.connect('projet_kevin.db')
c = conn.cursor()
create_database()

# Création de la fenêtre principale
main_page = tk.Tk()
main_page.title('Main Page')
main_page.geometry('1200x600')

# Création d'un widget Notebook pour les onglets
notebook = ttk.Notebook(main_page)
notebook.pack(fill="both", expand=True)

# Dictionnaire pour stocker les références aux pages (frames)
frames = {}

#####################################
# PAGE : Ajout d'une séance
#####################################
def create_add_lesson_page():
    frame = tk.Frame(notebook)
    frames['add_lesson'] = frame

    # Sélection de la date via un calendrier
    date_label = tk.Label(frame, text='Date de la séance:')
    date_label.pack(pady=5)
    date_entry = DateEntry(frame, date_pattern='dd/mm/yyyy')
    date_entry.set_date(date.today())
    date_entry.pack(pady=5)
    # Redonne le focus à la fenêtre principale une fois la date sélectionnée
    date_entry.bind("<<DateEntrySelected>>", lambda event: main_page.focus())

    # Choix de la formation via une Combobox
    formation_label = tk.Label(frame, text='Formation de la séance:')
    formation_label.pack(pady=5)
    formations = get_courses()
    formation_names = [course[4] for course in formations]
    formation_combo = ttk.Combobox(frame, values=formation_names, state="readonly")
    formation_combo.pack(pady=5)

    # Choix du professeur via une Combobox
    teacher_label = tk.Label(frame, text='Professeur de la séance:')
    teacher_label.pack(pady=5)
    personnels = get_students()
    teacher_list = [f"{pers[2]} (ID: {pers[1]})" for pers in personnels]
    teacher_combo = ttk.Combobox(frame, values=teacher_list, state="readonly")
    teacher_combo.pack(pady=5)

    # Sélection de la liste des participants via un Listbox multi-sélection
    participants_label = tk.Label(frame, text='Sélectionnez les participants:')
    participants_label.pack(pady=5)
    participants_listbox = tk.Listbox(frame, selectmode="multiple", height=6, exportselection=False)
    for pers in personnels:
        participants_listbox.insert(tk.END, f"{pers[2]} (ID: {pers[1]})")
    participants_listbox.pack(pady=5)

    status_label = tk.Label(frame, text="", fg="green")
    status_label.pack(pady=5)

    def submit_lesson():
        try:
            lesson_date = date_entry.get_date().strftime('%d/%m/%Y')
            formation_index = formation_combo.current()
            if formation_index == -1:
                raise IndexError("Formation non sélectionnée")
            lesson_course_id = formations[formation_index][0]

            teacher_index = teacher_combo.current()
            if teacher_index == -1:
                raise IndexError("Professeur non sélectionné")
            teacher_id = personnels[teacher_index][0]

            lesson_id = add_lesson(lesson_date, lesson_course_id, teacher_id)

            selected_indices = participants_listbox.curselection()
            if not selected_indices:
                raise IndexError("Aucun participant sélectionné")
            for index in selected_indices:
                participant_id = personnels[index][0]
                add_student_lesson(participant_id, lesson_id)

            status_label.config(text="Séance ajoutée avec succès !")
            messagebox.showinfo("Succès", "La séance a été ajoutée avec succès !")
            formation_combo.set('')
            teacher_combo.set('')
            participants_listbox.selection_clear(0, tk.END)
        except IndexError as e:
            messagebox.showerror("Erreur", f"Veuillez sélectionner tous les éléments requis.\n{str(e)}")

    submit_button = tk.Button(frame, text='Ajouter la séance', command=submit_lesson)
    submit_button.pack(pady=10)

    notebook.add(frame, text="Ajouter une séance")

#####################################
# PAGE : Affichage des séances par date
#####################################
def create_get_lessons_page():
    frame = tk.Frame(notebook)
    frames['get_lessons'] = frame

    lessons_date_label = tk.Label(frame, text='Date des séances:')
    lessons_date_label.pack(pady=5)
    lessons_date_entry = DateEntry(frame, date_pattern='dd/mm/yyyy')
    lessons_date_entry.set_date(date.today())
    lessons_date_entry.pack(pady=5)
    # Mise à jour automatique dès que la date est sélectionnée
    lessons_date_entry.bind("<<DateEntrySelected>>", lambda event: refresh())

    listbox = tk.Listbox(frame, width=50, height=8)
    listbox.pack(pady=5)

    detail_label = tk.Label(frame, text="", justify="left", wraplength=400)
    detail_label.pack(pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        lesson_date_str = lessons_date_entry.get_date().strftime('%d/%m/%Y')
        lessons = get_lessons_date(lesson_date_str)
        for lesson in lessons:
            courses = get_courses()
            # Récupère le nom de la formation en fonction de lesson_course_id
            course_name = next((course[4] for course in courses if course[0] == lesson[2]), "Inconnu")
            listbox.insert(tk.END, f"ID {lesson[0]} - {course_name}")
        detail_label.config(text="")

    refresh_button = tk.Button(frame, text="Refresh", command=refresh)
    refresh_button.pack(pady=5)

    # Bouton pour supprimer la séance sélectionnée
    def delete_selected_lesson():
        lessons = get_lessons_date(lessons_date_entry.get_date().strftime('%d/%m/%Y'))
        try:
            index = listbox.curselection()[0]
            lesson = lessons[index]
            # Confirmer la suppression
            if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer cette séance et tous ses liens ?"):
                remove_lesson_and_links(lesson[0])
                messagebox.showinfo("Succès", "La séance et ses liens ont été supprimés.")
                refresh()
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une séance à supprimer.")

    delete_button = tk.Button(frame, text="Supprimer la séance", command=delete_selected_lesson)
    delete_button.pack(pady=5)

    def show_lesson_details(event):
        lessons = get_lessons_date(lessons_date_entry.get_date().strftime('%d/%m/%Y'))
        try:
            index = listbox.curselection()[0]
            lesson = lessons[index]
            courses = get_courses()
            course = next((c for c in courses if c[0] == lesson[2]), None)
            course_info = f"Formation : {course[4]}\nCode : {course[1]}\nDescription : {course[2]}" if course else "Formation inconnue"
            teachers = get_students()
            teacher = next((t for t in teachers if t[0] == lesson[3]), None)
            teacher_info = f"Professeur : {teacher[2]} (ID: {teacher[1]})" if teacher else "Professeur inconnu"
            c.execute('''SELECT sl.student_lesson_id, s.student_name, s.student_identification 
                         FROM students_lessons sl 
                         JOIN students s ON sl.student_id = s.student_id 
                         WHERE sl.lesson_id = ?''', (lesson[0],))
            participants = c.fetchall()
            participants_info = "\n".join([f"{p[1]} (ID: {p[2]})" for p in participants]) if participants else "Aucun participant"
            details = f"ID Séance: {lesson[0]}\nDate: {lesson[1]}\n{course_info}\n{teacher_info}\nParticipants:\n{participants_info}"
            detail_label.config(text=details)
        except IndexError:
            detail_label.config(text="")

    listbox.bind("<<ListboxSelect>>", show_lesson_details)
    notebook.add(frame, text="Voir les séances par date")

#####################################
# Nouvelle fonction : obtenir les séances d'un participant via la table de liaison
#####################################
def get_student_lessons(personnel_id):
    c.execute('''SELECT sl.student_lesson_id, l.lesson_id, l.lesson_date, l.lesson_course_id, l.teacher_id 
                 FROM students_lessons sl 
                 JOIN lessons l ON sl.lesson_id = l.lesson_id 
                 WHERE sl.student_id = ?''', (personnel_id,))
    return c.fetchall()

#####################################
# PAGE : Affichage des séances par personnel avec suppression de lien
#####################################
def create_get_lessons_by_personnel_page():
    frame = tk.Frame(notebook)
    frames['get_lessons_by_personnel'] = frame

    personnel_label = tk.Label(frame, text='Sélectionnez le personnel:')
    personnel_label.pack(pady=5)

    personnel_list = tk.Listbox(frame, height=4)
    personnels = get_students()
    for pers in personnels:
        personnel_list.insert(tk.END, f"{pers[2]} (ID: {pers[1]})")
    personnel_list.pack(pady=5)

    listbox = tk.Listbox(frame, width=50, height=8)
    listbox.pack(pady=5)

    detail_label = tk.Label(frame, text="", justify="left", wraplength=400)
    detail_label.pack(pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        detail_label.config(text="")
        try:
            index = personnel_list.curselection()[0]
            personnel_id = personnels[index][0]
            lessons = get_student_lessons(personnel_id)
            for les in lessons:
                listbox.insert(tk.END, f"ID {les[1]} - Date: {les[2]}")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez un personnel.")

    refresh_button = tk.Button(frame, text="Refresh", command=refresh)
    refresh_button.pack(pady=5)

    def show_lesson_details_personnel(event):
        try:
            lessons = get_student_lessons(personnels[personnel_list.curselection()[0]][0])
            index = listbox.curselection()[0]
            les = lessons[index]
            courses = get_courses()
            course = next((c for c in courses if c[0] == les[3]), None)
            course_info = f"Formation : {course[4]}" if course else "Formation inconnue"
            detail = f"ID Séance: {les[1]}\nDate: {les[2]}\n{course_info}"
            detail_label.config(text=detail)
        except IndexError:
            detail_label.config(text="")

    listbox.bind("<<ListboxSelect>>", show_lesson_details_personnel)

    # Bouton pour supprimer le lien (supprimer la participation)
    def remove_link():
        try:
            personnel_id = personnels[personnel_list.curselection()[0]][0]
            lessons = get_student_lessons(personnel_id)
            index = listbox.curselection()[0]
            link_id = lessons[index][0]
            remove_student_lesson(link_id)
            refresh()
            messagebox.showinfo("Succès", "La relation a été supprimée.")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une séance à supprimer.")

    remove_button = tk.Button(frame, text="Supprimer la séance sélectionnée", command=remove_link)
    remove_button.pack(pady=5)

    personnel_submit = tk.Button(frame, text='Afficher les séances', command=refresh)
    personnel_submit.pack(pady=10)

    notebook.add(frame, text="Voir les séances par personnel")

#####################################
# PAGE : Ajout d'un personnel
#####################################
def create_add_student_page():
    frame = tk.Frame(notebook)
    frames['add_student'] = frame

    student_name_label = tk.Label(frame, text='Nom du personnel:')
    student_name_label.pack(pady=5)

    student_name_entry = tk.Entry(frame)
    student_name_entry.pack(pady=5)

    student_identification_label = tk.Label(frame, text='Identification:')
    student_identification_label.pack(pady=5)

    student_identification_entry = tk.Entry(frame)
    student_identification_entry.pack(pady=5)

    status_label = tk.Label(frame, text="", fg="green")
    status_label.pack(pady=5)

    def submit_student():
        add_student(student_name_entry.get(), student_identification_entry.get())
        student_name_entry.delete(0, tk.END)
        student_identification_entry.delete(0, tk.END)
        status_label.config(text="Personnel ajouté avec succès !")
        refresh_get_courses_page()  # Pour actualiser les listes dépendantes
        
    student_submit = tk.Button(frame, text='Ajouter le personnel', command=submit_student)
    student_submit.pack(pady=10)

    notebook.add(frame, text="Ajouter un personnel")

#####################################
# PAGE : Ajout d'une formation
#####################################
def create_add_course_page():
    frame = tk.Frame(notebook)
    frames['add_course'] = frame

    course_name_label = tk.Label(frame, text='Nom de la formation:')
    course_name_label.pack(pady=5)

    course_name_entry = tk.Entry(frame)
    course_name_entry.pack(pady=5)

    course_code_label = tk.Label(frame, text='Code de la formation:')
    course_code_label.pack(pady=5)

    course_code_entry = tk.Entry(frame)
    course_code_entry.pack(pady=5)

    course_description_label = tk.Label(frame, text='Description:')
    course_description_label.pack(pady=5)

    course_description_entry = tk.Entry(frame)
    course_description_entry.pack(pady=5)

    course_duration_label = tk.Label(frame, text='Durée:')
    course_duration_label.pack(pady=5)

    course_duration_entry = tk.Entry(frame)
    course_duration_entry.pack(pady=5)

    status_label = tk.Label(frame, text="", fg="green")
    status_label.pack(pady=5)

    def submit_course():
        add_course(course_name_entry.get(), course_code_entry.get(), course_description_entry.get(), course_duration_entry.get())
        course_name_entry.delete(0, tk.END)
        course_code_entry.delete(0, tk.END)
        course_description_entry.delete(0, tk.END)
        course_duration_entry.delete(0, tk.END)
        status_label.config(text="Formation ajoutée avec succès !")
        refresh_get_courses_page()
        
    course_submit = tk.Button(frame, text='Ajouter la formation', command=submit_course)
    course_submit.pack(pady=10)

    # Lorsqu'on sélectionne cet onglet, on peut le rafraîchir
    notebook.add(frame, text="Ajouter une formation")

#####################################
# PAGE : Affichage des formations et possibilité de suppression
# + affichage des détails lors de la sélection
#####################################
def create_get_courses_page():
    frame = tk.Frame(notebook)
    frames['get_courses'] = frame

    listbox = tk.Listbox(frame, width=50, height=8)
    listbox.pack(pady=5)

    detail_label = tk.Label(frame, text="", justify="left", wraplength=400)
    detail_label.pack(pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        courses = get_courses()
        for course in courses:
            listbox.insert(tk.END, course[4])  # nom de la formation
        detail_label.config(text="")  # on efface les détails
    refresh_button = tk.Button(frame, text="Refresh", command=refresh)
    refresh_button.pack(pady=5)

    def remove_selected():
        courses = get_courses()
        try:
            index = listbox.curselection()[0]
            remove_course(courses[index][0])
            refresh()
            messagebox.showinfo("Succès", "Formation supprimée avec succès !")
        except IndexError:
            messagebox.showerror("Erreur", "Sélectionnez une formation à supprimer.")
    
    course_remove_button = tk.Button(frame, text='Supprimer la formation', command=remove_selected)
    course_remove_button.pack(pady=10)

    def show_course_details(event):
        courses = get_courses()
        try:
            index = listbox.curselection()[0]
            course = courses[index]
            details = f"Code: {course[1]}\nDescription: {course[2]}\nDurée: {course[3]}"
            detail_label.config(text=details)
        except IndexError:
            detail_label.config(text="")

    listbox.bind("<<ListboxSelect>>", show_course_details)

    notebook.add(frame, text="Voir les formations")

def refresh_get_courses_page():
    page = frames.get('get_courses')
    if page:
        for child in page.winfo_children():
            if isinstance(child, tk.Button) and child.cget("text")=="Refresh":
                child.invoke()

#####################################
# PAGE : Affichage des personnels avec détails
#####################################
def create_get_students_page():
    frame = tk.Frame(notebook)
    frames['get_students'] = frame

    listbox = tk.Listbox(frame, width=50, height=8)
    listbox.pack(pady=5)
    
    detail_label = tk.Label(frame, text="", justify="left", wraplength=400)
    detail_label.pack(pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        detail_label.config(text="")
        students = get_students()
        for stud in students:
            listbox.insert(tk.END, f"{stud[2]} (ID: {stud[1]})")
    refresh_button = tk.Button(frame, text="Refresh", command=refresh)
    refresh_button.pack(pady=5)

    def show_student_details(event):
        students = get_students()
        try:
            index = listbox.curselection()[0]
            student = students[index]
            details = f"Nom : {student[2]}\nIdentification : {student[1]}"
            detail_label.config(text=details)
        except IndexError:
            detail_label.config(text="")

    listbox.bind("<<ListboxSelect>>", show_student_details)

    notebook.add(frame, text="Voir le personnel")

# Lors du changement d'onglet, on rafraîchit automatiquement la page si besoin
def on_tab_changed(event):
    selected_tab = event.widget.select()
    frame = event.widget.nametowidget(selected_tab)
    # Si la page possède un bouton "Refresh", on l'invoque
    for child in frame.winfo_children():
        if isinstance(child, tk.Button) and child.cget("text") == "Refresh":
            child.invoke()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# Création de toutes les pages (chaque page est ajoutée en tant qu'onglet)
create_add_lesson_page()
create_add_student_page()
create_add_course_page()
create_get_lessons_page()
create_get_courses_page()
create_get_students_page()
create_get_lessons_by_personnel_page()

main_page.mainloop()
conn.close()