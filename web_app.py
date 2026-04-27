import os
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)

from controller import Controller
from model import Database


BASE_DIR = Path(__file__).resolve().parent


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "gestion-formation-dev")
    app.config["DATABASE_PATH"] = database_path or os.environ.get("DATABASE_PATH", "bdd_formations.db")

    @app.teardown_appcontext
    def close_database(error=None):
        database = g.pop("database", None)
        if database is not None:
            database.close()

    @app.get("/")
    def index():
        controller = get_controller()
        return render_app(controller, active_page="dashboard", page_title="Vue globale", page_eyebrow="Formation")

    @app.get("/search")
    def search_page():
        controller = get_controller()
        return render_app(controller, active_page="search", page_title="Recherche", page_eyebrow="Retrouver")

    @app.get("/admin")
    def admin_page():
        controller = get_controller()
        active_tab = request.args.get("tab", "personnel")
        if active_tab not in {"personnel", "formations"}:
            active_tab = "personnel"
        return render_app(
            controller,
            active_page="admin",
            active_tab=active_tab,
            page_title="Admin",
            page_eyebrow="Gerer",
        )

    @app.get("/reports")
    def reports_page():
        controller = get_controller()
        return render_app(controller, active_page="reports", page_title="Export PDF", page_eyebrow="Suivi")

    @app.post("/courses")
    def create_course():
        controller = get_controller()
        name = request.form.get("course_name", "").strip()
        code = request.form.get("course_code", "").strip()
        description = request.form.get("course_description", "").strip()
        duration = request.form.get("course_duration", "").strip()

        if not all([name, code, description, duration]):
            flash("Tous les champs de formation sont requis.", "error")
            return redirect(url_for("admin_page", tab="formations"))

        try:
            duration_value = int(duration)
        except ValueError:
            flash("La duree doit etre un nombre.", "error")
            return redirect(url_for("admin_page", tab="formations"))

        if controller.add_course(name, code, description, duration_value):
            flash("Formation ajoutee.", "success")
        else:
            flash("Impossible d'ajouter la formation.", "error")
        return redirect(url_for("admin_page", tab="formations"))

    @app.post("/courses/<int:course_id>/update")
    def update_course(course_id):
        controller = get_controller()
        name = request.form.get("course_name", "").strip()
        code = request.form.get("course_code", "").strip()
        description = request.form.get("course_description", "").strip()
        duration = request.form.get("course_duration", "").strip()

        if not all([name, code, description, duration]):
            flash("Tous les champs de formation sont requis.", "error")
            return redirect(url_for("admin_page", tab="formations"))

        try:
            duration_value = int(duration)
        except ValueError:
            flash("La duree doit etre un nombre.", "error")
            return redirect(url_for("admin_page", tab="formations"))

        if controller.update_course(course_id, name, code, description, duration_value):
            flash("Formation mise a jour.", "success")
        else:
            flash("La formation n'a pas pu etre modifiee.", "error")
        return redirect(url_for("admin_page", tab="formations"))

    @app.post("/courses/<int:course_id>/delete")
    def delete_course(course_id):
        controller = get_controller()
        if controller.remove_course(course_id):
            flash("Formation supprimee.", "success")
        else:
            flash("La formation n'a pas pu etre supprimee.", "error")
        return redirect(url_for("admin_page", tab="formations"))

    @app.post("/students")
    def create_student():
        controller = get_controller()
        identification = request.form.get("student_identification", "").strip()
        first_name = request.form.get("student_name", "").strip()
        last_name = request.form.get("nom_de_famille", "").strip()
        peloton = request.form.get("peloton", "").strip()

        if not all([identification, first_name, last_name, peloton]):
            flash("Tous les champs de personnel sont requis.", "error")
            return redirect(url_for("admin_page", tab="personnel"))

        if controller.add_student(first_name, identification, "", last_name, peloton):
            flash("Personnel ajoute.", "success")
        else:
            flash("Impossible d'ajouter le personnel.", "error")
        return redirect(url_for("admin_page", tab="personnel"))

    @app.post("/students/<int:student_id>/update")
    def update_student(student_id):
        controller = get_controller()
        identification = request.form.get("student_identification", "").strip()
        first_name = request.form.get("student_name", "").strip()
        last_name = request.form.get("nom_de_famille", "").strip()
        peloton = request.form.get("peloton", "").strip()

        if not all([identification, first_name, last_name, peloton]):
            flash("Tous les champs de personnel sont requis.", "error")
            return redirect(url_for("admin_page", tab="personnel"))

        if controller.update_student(student_id, first_name, identification, "", last_name, peloton):
            flash("Personnel mis a jour.", "success")
        else:
            flash("Le personnel n'a pas pu etre modifie.", "error")
        return redirect(url_for("admin_page", tab="personnel"))

    @app.post("/students/<int:student_id>/delete")
    def delete_student(student_id):
        controller = get_controller()
        if controller.remove_student(student_id):
            flash("Personnel supprime.", "success")
        else:
            flash("Le personnel n'a pas pu etre supprime.", "error")
        return redirect(url_for("admin_page", tab="personnel"))

    @app.post("/lessons")
    def create_lesson():
        controller = get_controller()
        lesson_date = request.form.get("lesson_date", "").strip()
        course_id = parse_int(request.form.get("course_id"))
        teacher_id = parse_int(request.form.get("teacher_id"))
        participant_ids = [parse_int(value) for value in request.form.getlist("participant_ids")]
        participant_ids = [value for value in participant_ids if value is not None]

        if not lesson_date or course_id is None or teacher_id is None or not participant_ids:
            flash("Date, module, moniteur et participants sont requis.", "error")
            return redirect(url_for("index"))

        if controller.add_lesson_by_ids(lesson_date, course_id, teacher_id, participant_ids):
            flash("Seance ajoutee.", "success")
        else:
            flash("Impossible d'ajouter la seance.", "error")
        return redirect(url_for("index"))

    @app.post("/lessons/<int:lesson_id>/delete")
    def delete_lesson(lesson_id):
        controller = get_controller()
        if controller.remove_lesson_and_links(lesson_id):
            flash("Seance supprimee.", "success")
        else:
            flash("La seance n'a pas pu etre supprimee.", "error")
        return redirect_to_search_filters()

    @app.post("/student-lessons/<int:student_lesson_id>/delete")
    def delete_student_lesson(student_lesson_id):
        controller = get_controller()
        if controller.remove_student_lesson(student_lesson_id):
            flash("Lien de seance supprime.", "success")
        else:
            flash("Le lien de seance n'a pas pu etre supprime.", "error")
        return redirect_to_search_filters()

    @app.post("/reports/cross-tab")
    def report_cross_tab():
        controller = get_controller()
        student_ids = [parse_int(value) for value in request.form.getlist("student_ids")]
        student_ids = [value for value in student_ids if value is not None]
        if not student_ids:
            flash("Selectionnez au moins un personnel pour le PDF.", "error")
            return redirect(url_for("reports_page"))

        pdf_buffer = build_training_pdf(controller, student_ids)
        filename = f"tableau_suivi_formation_{date.today().strftime('%Y%m%d')}.pdf"
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    @app.get("/logo")
    def logo():
        if not (BASE_DIR / "LOGO_PIGR.jpeg").exists():
            abort(404)
        return send_from_directory(BASE_DIR, "LOGO_PIGR.jpeg")

    return app


def get_controller():
    if "database" not in g:
        g.database = Database(current_database_path())
        g.controller = Controller(g.database)
    return g.controller


def current_database_path():
    from flask import current_app

    return current_app.config["DATABASE_PATH"]


def render_app(controller, active_page, page_title, page_eyebrow, active_tab=None):
    return render_template(
        "index.html",
        **build_context(controller),
        active_page=active_page,
        active_tab=active_tab,
        page_title=page_title,
        page_eyebrow=page_eyebrow,
    )


def redirect_to_search_filters():
    args = {}
    for key in ("date", "student_id", "course_id"):
        value = request.form.get(key, "").strip()
        if value:
            args[key] = value
    return redirect(url_for("search_page", **args))


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def today_text():
    return date.today().strftime("%d/%m/%Y")


def build_context(controller):
    courses = [course_to_dict(row) for row in controller.get_courses()]
    students = [student_to_dict(row) for row in controller.get_students()]
    courses_by_id = {course["id"]: course for course in courses}
    students_by_id = {student["id"]: student for student in students}

    date_filter = request.args.get("date", "").strip()
    student_filter = parse_int(request.args.get("student_id"))
    course_filter = parse_int(request.args.get("course_id"))

    lessons = [
        lesson_to_dict(row, controller, courses_by_id, students_by_id)
        for row in controller.get_lessons()
    ]
    recent_lessons = list(reversed(lessons[-6:]))

    search_results = build_search_results(controller, lessons, date_filter, student_filter, course_filter)

    return {
        "courses": courses,
        "students": students,
        "lessons": lessons,
        "recent_lessons": recent_lessons,
        "search_results": search_results,
        "cross_tab": build_cross_tab(controller, students, courses, students_by_id),
        "filters": {
            "date": date_filter,
            "student_id": student_filter,
            "course_id": course_filter,
        },
        "stats": {
            "courses": len(courses),
            "students": len(students),
            "lessons": len(lessons),
        },
        "today": today_text(),
    }


def course_to_dict(row):
    return {
        "id": row[0],
        "code": row[1] or "",
        "description": row[2] or "",
        "duration": row[3] if row[3] is not None else "",
        "name": row[4] or "Formation sans nom",
    }


def student_to_dict(row):
    student = {
        "id": row[0],
        "identification": row[1] or "",
        "first_name": row[2] or "",
        "legacy_name": row[3] or "",
        "last_name": row[4] or "",
        "peloton": row[5] or "",
    }
    student["label"] = format_student(student)
    return student


def format_student(student):
    name = f"{student['first_name']} {student['last_name']}".strip()
    if name:
        return name
    if student["identification"]:
        return f"Personnel {student['identification']}"
    return f"Personnel #{student['id']}"


def lesson_to_dict(row, controller, courses_by_id, students_by_id):
    participants = [
        {
            "link_id": participant[0],
            "name": participant[1] or "Personnel",
            "identification": participant[2] or "",
        }
        for participant in controller.get_lesson_participants(row[0])
    ]
    course = courses_by_id.get(row[2], missing_course(row[2]))
    teacher = students_by_id.get(row[3], missing_student(row[3]))
    return {
        "id": row[0],
        "date": row[1] or "",
        "course_id": row[2],
        "teacher_id": row[3],
        "course": course,
        "teacher": teacher,
        "participants": participants,
    }


def linked_lesson_to_dict(row, courses_by_id, students_by_id):
    course = courses_by_id.get(row[3], missing_course(row[3]))
    teacher = students_by_id.get(row[4], missing_student(row[4]))
    return {
        "student_lesson_id": row[0],
        "id": row[1],
        "date": row[2] or "",
        "course_id": row[3],
        "teacher_id": row[4],
        "course": course,
        "teacher": teacher,
    }


def build_search_results(controller, lessons, date_filter, student_filter, course_filter):
    selected_student_links = {}
    if student_filter:
        selected_student_links = {
            row[1]: row[0]
            for row in controller.get_student_lessons(student_filter)
        }

    results = []
    for lesson in lessons:
        if date_filter and lesson["date"] != date_filter:
            continue
        if course_filter and lesson["course_id"] != course_filter:
            continue
        if student_filter and lesson["id"] not in selected_student_links:
            continue

        result = dict(lesson)
        result["selected_student_lesson_id"] = selected_student_links.get(lesson["id"])
        results.append(result)

    return list(reversed(results))


def missing_course(course_id):
    return {
        "id": course_id,
        "code": "NC",
        "description": "",
        "duration": "",
        "name": "Formation inconnue",
    }


def missing_student(student_id):
    return {
        "id": student_id,
        "identification": "",
        "first_name": "",
        "legacy_name": "",
        "last_name": "",
        "peloton": "",
        "label": "Personnel inconnu",
    }


def build_cross_tab(controller, students, courses, students_by_id):
    rows = []
    for student in students:
        lessons = controller.get_student_lessons(student["id"])
        grouped = {}
        for lesson in lessons:
            teacher = students_by_id.get(lesson[4], missing_student(lesson[4]))
            grouped.setdefault(lesson[3], []).append(
                {
                    "date": lesson[2],
                    "teacher": teacher["label"],
                }
            )
        rows.append(
            {
                "student": student,
                "cells": [
                    {
                        "course": course,
                        "items": grouped.get(course["id"], []),
                    }
                    for course in courses
                ],
            }
        )
    return rows


def build_training_pdf(controller, selected_student_ids):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    courses = [course_to_dict(row) for row in controller.get_courses()]
    students = [student_to_dict(row) for row in controller.get_students()]
    students_by_id = {student["id"]: student for student in students}
    selected_students = [student for student in students if student["id"] in selected_student_ids]

    styles = getSampleStyleSheet()
    table_data = [["Personnel"] + [course["name"] for course in courses]]
    completion_matrix = []
    for student in selected_students:
        row = [student["label"]]
        completion_row = []
        lessons = controller.get_student_lessons(student["id"])
        grouped = {}
        for lesson in lessons:
            teacher = students_by_id.get(lesson[4], missing_student(lesson[4]))
            grouped.setdefault(lesson[3], []).append(f"{lesson[2]} ({teacher['label']})")
        for course in courses:
            items = grouped.get(course["id"], [])
            completion_row.append(bool(items))
            content = "<br/>".join(items) or "Non effectue"
            row.append(Paragraph(content, styles["BodyText"]))
        table_data.append(row)
        completion_matrix.append(completion_row)

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=18,
        rightMargin=18,
        topMargin=18,
        bottomMargin=18,
    )
    elements = [
        Paragraph("Tableau de suivi de formation", styles["Title"]),
        Spacer(1, 10),
        Paragraph("Date de generation : " + today_text(), styles["Normal"]),
        Spacer(1, 18),
    ]

    table = Table(table_data, repeatRows=1, hAlign="CENTER")
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eadf")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17201b")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#8d968d")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
            ("TOPPADDING", (0, 0), (-1, 0), 7),
        ]
    )
    for row_index, completion_row in enumerate(completion_matrix, start=1):
        for column_index, is_done in enumerate(completion_row, start=1):
            color = "#d9f0df" if is_done else "#ffd8cc"
            style.add("BACKGROUND", (column_index, row_index), (column_index, row_index), colors.HexColor(color))
    table.setStyle(style)
    elements.append(table)
    document.build(elements)
    buffer.seek(0)
    return buffer
