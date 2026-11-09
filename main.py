# main.py
from nicegui import ui
from typing import List
import models
import csv
import io
import tkinter as tk
from tkinter import filedialog
import assignment_engine
import json
import os

AUTOSAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autosave.json')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

#----------------------------------- 
# SAVE/LOAD FUNCTIONS
#----------------------------------- 

def save_project_to_file(filepath):
    data = {
        'students': [vars(s) for s in students],
        'buildings': [vars(b) for b in buildings],
        'classrooms': [vars(c) for c in classrooms],
        'proctors': [vars(p) for p in proctors],
        'building_supervisors': [vars(s) for s in building_supervisors],
        'exams': [vars(e) for e in exams],
        'assignments': [vars(a) for a in assignments],
        'next_student_id': next_student_id,
        'next_building_id': next_building_id,
        'next_classroom_id': next_classroom_id,
        'next_proctor_id': next_proctor_id,
        'next_building_supervisor_id': next_building_supervisor_id,
        'next_exam_id': next_exam_id,
        'next_assignment_id': next_assignment_id,
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_project_from_file(filepath):
    global students, buildings, classrooms, proctors, building_supervisors, exams, assignments
    global next_student_id, next_building_id, next_classroom_id, next_proctor_id
    global next_building_supervisor_id, next_exam_id, next_assignment_id

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Rebuild objects using dataclass constructors
    students = [models.Student(**s) for s in data['students']]
    buildings = [models.Building(**b) for b in data['buildings']]
    classrooms = [models.Classroom(**c) for c in data['classrooms']]
    proctors = [models.Proctor(**p) for p in data['proctors']]
    building_supervisors = [models.BuildingSupervisor(**s) for s in data['building_supervisors']]
    exams = [models.Exam(**e) for e in data['exams']]
    assignments = [models.Assignment(**a) for a in data['assignments']]

    next_student_id = data['next_student_id']
    next_building_id = data['next_building_id']
    next_classroom_id = data['next_classroom_id']
    next_proctor_id = data['next_proctor_id']
    next_building_supervisor_id = data['next_building_supervisor_id']
    next_exam_id = data['next_exam_id']
    next_assignment_id = data['next_assignment_id']

def autosave():
    """Save current state to the autosave file (silent)."""
    try:
        save_project_to_file(AUTOSAVE_PATH)
    except Exception as e:
        print(f"Autosave failed: {e}")

def auto_load():
    """Load state from autosave file if it exists."""
    if os.path.exists(AUTOSAVE_PATH):
        try:
            load_project_from_file(AUTOSAVE_PATH)
            print(f"Autoloaded project from {AUTOSAVE_PATH}")
        except Exception as e:
            print(f"Autoload failed: {e}")

def save_project_dialog():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialfile="exam_project.json",
        title="Save Project As"
    )
    if file_path:
        try:
            save_project_to_file(file_path)
            ui.notify(f'Project saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving project: {e}', type='error')
    root.destroy()

def load_project_dialog():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Open Project"
    )
    if file_path:
        try:
            load_project_from_file(file_path)
            # After loading, refresh all UI tables and dropdowns
            if exam_table_refresh:
                exam_table_refresh()
            if student_table_refresh:
                student_table_refresh()
            if building_table_refresh:
                building_table_refresh()
            if classroom_table_refresh:
                classroom_table_refresh()
            if proctor_table_refresh:
                proctor_table_refresh()
            if supervisor_table_refresh:
                supervisor_table_refresh()
            if exam_select_refresh:
                exam_select_refresh()
            if report_exam_select_refresh:
                report_exam_select_refresh()
            if assignment_table_refresh:
                assignment_table_refresh()
            ui.notify('Project loaded successfully', type='positive')
        except Exception as e:
            ui.notify(f'Error loading project: {e}', type='error')
    root.destroy()

#---------------------------
# Backup function
#---------------------------
def backup_now():
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'backup_{timestamp}.json'
    filepath = os.path.join(BACKUP_DIR, filename)
    try:
        save_project_to_file(filepath)
        ui.notify(f'Backup saved to {filename}', type='positive')
    except Exception as e:
        ui.notify(f'Backup failed: {e}', type='error')

#---------------------------------
# Reset all data function
#--------------------------------   
def reset_all_data():
    global students, buildings, classrooms, proctors, building_supervisors, exams, assignments
    global next_student_id, next_building_id, next_classroom_id, next_proctor_id
    global next_building_supervisor_id, next_exam_id, next_assignment_id

    students = []
    buildings = []
    classrooms = []
    proctors = []
    building_supervisors = []
    exams = []
    assignments = []
    next_student_id = 1
    next_building_id = 1
    next_classroom_id = 1
    next_proctor_id = 1
    next_building_supervisor_id = 1
    next_exam_id = 1
    next_assignment_id = 1

    # Refresh all UI
    if student_table_refresh: student_table_refresh()
    if building_table_refresh: building_table_refresh()
    if classroom_table_refresh: classroom_table_refresh()
    if proctor_table_refresh: proctor_table_refresh()
    if supervisor_table_refresh: supervisor_table_refresh()
    if exam_table_refresh: exam_table_refresh()
    if exam_select_refresh: exam_select_refresh()
    if report_exam_select_refresh: report_exam_select_refresh()
    if assignment_table_refresh: assignment_table_refresh()

    autosave()
    ui.notify('All data reset', type='positive')

#-----------------------------------
# CSV Content Decoding
#----------------------------------
def decode_csv_content(content: bytes) -> str:
    """Try to decode CSV bytes using common encodings."""
    for enc in ['utf-8-sig', 'utf-8', 'cp1254', 'latin-1']:
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    # Final fallback
    return content.decode('latin-1', errors='ignore')

#----------------------------------------
# Read & Upload Rows (csv & xlsx)
#----------------------------------------
def read_upload_rows(content: bytes, filename: str):
    """
    Read a CSV or XLSX file's bytes and return a list of rows (list of lists of strings).
    Detects format by extension first, then content.
    """
    print(f"DEBUG read_upload_rows: filename='{filename}'")
    name = (filename or '').lower()
    if name.endswith('.xlsx') or name.endswith('.xlsm'):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append(['' if v is None else str(v) for v in row])
        return rows

    # Fallback: treat as text (CSV/TSV)
    text = decode_csv_content(content)
    first_line = text.splitlines()[0] if text.splitlines() else ''
    delimiter = '\t' if '\t' in first_line else ','
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    return [list(row) for row in reader]

#-------------------------------------
# Extract ID's from lists
#-------------------------------------
def extract_selected_ids(selected):
    """Extract IDs from a table's selection, handling dict or scalar formats."""
    ids = []
    for item in selected:
        if isinstance(item, dict):
            ids.append(item.get('id'))
        else:
            try:
                ids.append(int(item))
            except (ValueError, TypeError):
                pass
    return ids

#------------------------------------
# Confirm Action Dialogue for Risky Buttons
#------------------------------------
def confirm_action(message, callback):
    with ui.dialog() as confirm_dialog, ui.card():
        ui.label(message).classes('text-lg')
        with ui.row():
            ui.button('Yes', on_click=lambda: (confirm_dialog.close(), callback())).props('color=negative')
            ui.button('No', on_click=confirm_dialog.close).props('color=primary')
    confirm_dialog.open()

#-----------------------------------------------
# Language Normalizer Function
#-----------------------------------------------
def normalize_language(lang):
    """Map language names (Turkish/English, case-insensitive) to canonical English names."""
    if not lang:
        return None
    mapping = {
        'ingilizce': 'English',
        'english': 'English',
        'almanca': 'German',
        'german': 'German',
        'türkçe': 'Turkish',
        'turkce': 'Turkish',
        'turkish': 'Turkish',
        'fransızca': 'French',
        'fransizca': 'French',
        'french': 'French',
        'ispanyolca': 'Spanish',
        'i̇spanyolca': 'Spanish',
        'spanish': 'Spanish',
    }
    key = lang.strip().lower().replace('\u0307', '')
    return mapping.get(key, lang.strip())

# ------------------------------------------------------------
# In-memory data storage
# ------------------------------------------------------------
# Settings defaults
default_proctors_per_classroom = 2
backup_folder = None   # set below

students: List[models.Student] = []
next_student_id = 1

student_table = None
student_table_refresh = None

buildings: List[models.Building] = []
next_building_id = 1

building_table = None

classrooms: List[models.Classroom] = []
next_classroom_id = 1

classroom_table_refresh = None

proctors: List[models.Proctor] = []
next_proctor_id = 1

proctor_table_refresh = None

building_supervisors: List[models.BuildingSupervisor] = []
next_building_supervisor_id = 1

supervisor_table_refresh = None

exams: List[models.Exam] = []
next_exam_id = 1

exam_select_refresh = None
exam_table_refresh = None

report_exam_select_refresh = None

assignments: List[models.Assignment] = []
next_assignment_id = 1

assignment_table_refresh = None
run_assignment_global = None
report_preview_clear = None

# ------------------------------------------------------------
# Helper functions for students
# ------------------------------------------------------------
def add_student_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Student').classes('text-lg font-bold')
        full_name = ui.input('Full Name').classes('w-full')
        faculty = ui.input('Faculty').classes('w-full')
        department = ui.input('Department').classes('w-full')
        exam_id = ui.number('Exam ID', value=1, min=1, step=1).classes('w-full')
        language_options = ['English', 'German', 'Turkish', 'French', 'Spanish']
        language = ui.select(
            label='Language (optional)',
            options=language_options,
            with_input=True,
            clearable=True
        ).classes('w-full')

        def save():
            global next_student_id
            new_student = models.Student(
                id=next_student_id,
                full_name=full_name.value,
                faculty=faculty.value,
                department=department.value,
                exam_id=int(exam_id.value),
                language=language.value.strip() if language.value else None
            )
            students.append(new_student)
            next_student_id += 1
            # Update table
            student_table.rows = [
                {'id': s.id, 'full_name': s.full_name, 'faculty': s.faculty,
                 'department': s.department, 'exam_id': s.exam_id, 'language': s.language or '-'}
                for s in students
            ]
            student_table.update()
            dialog.close()
            ui.notify('Student added', type='positive')

        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

# ------------------------------------------------------------
# Helper functions for buildings and classrooms
# ------------------------------------------------------------
def add_building_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Building').classes('text-lg font-bold')
        name = ui.input('Building Name').classes('w-full')
        def save():
            global next_building_id
            new_building = models.Building(id=next_building_id, name=name.value)
            buildings.append(new_building)
            next_building_id += 1
            # Update the building table rows
            building_table.rows = [{'id': b.id, 'name': b.name} for b in buildings]
            building_table.update()
            dialog.close()
            ui.notify('Building added', type='positive')
        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

def add_classroom_dialog():
    if not buildings:
        ui.notify('Please add at least one building first', type='warning')
        return
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Classroom').classes('text-lg font-bold')
        building_select = ui.select(
            label='Building',
            options={b.id: b.name for b in buildings},
            with_input=True
        ).classes('w-full')
        name = ui.input('Classroom Name (e.g., A101)').classes('w-full')
        capacity = ui.number('Capacity', value=30, min=1, step=1).classes('w-full')
        is_reserve = ui.checkbox('Reserve classroom')
        def save():
            global next_classroom_id
            new_classroom = models.Classroom(
                id=next_classroom_id,
                building_id=building_select.value,
                name=name.value,
                capacity=int(capacity.value),
                is_reserve=is_reserve.value
            )
            classrooms.append(new_classroom)
            next_classroom_id += 1
            # Use the global refresh function if available
            if classroom_table_refresh:
                classroom_table_refresh()
            dialog.close()
            ui.notify('Classroom added', type='positive')
        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

# ------------------------------------------------------------
# Helper function for proctors
# ------------------------------------------------------------
def add_proctor_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Proctor').classes('text-lg font-bold')
        full_name = ui.input('Full Name').classes('w-full')
        department = ui.input('Department').classes('w-full')
        languages = ui.input('Languages (comma-separated, e.g., English,German)').classes('w-full')
        building_options = {b.id: b.name for b in buildings}
        building_options[0] = 'None'
        preferred_building = ui.select(
            label='Preferred Building (optional)',
            options=building_options,
            value=0,
            with_input=False
        ).classes('w-full')
        can_be_supervisor = ui.checkbox('Can be building supervisor', value=True)
        is_reserve = ui.checkbox('Reserve proctor', value=False)

        def save():
            global next_proctor_id
            lang_list = [l.strip() for l in languages.value.split(',') if l.strip()]
            bld_id = preferred_building.value if preferred_building.value != 0 else None
            new_proctor = models.Proctor(
                id=next_proctor_id,
                full_name=full_name.value,
                department=department.value,
                languages=lang_list,
                preferred_building_id=bld_id,
                can_be_supervisor=can_be_supervisor.value,
                is_reserve=is_reserve.value
            )
            proctors.append(new_proctor)
            next_proctor_id += 1
            if proctor_table_refresh:
                proctor_table_refresh()
            dialog.close()
            ui.notify('Proctor added', type='positive')

        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

# ------------------------------------------------------------
# Helper function for building supervisors
# ------------------------------------------------------------
def add_building_supervisor_dialog():
    if not buildings:
        ui.notify('Please add at least one building first', type='warning')
        return
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Building Supervisor').classes('text-lg font-bold')
        use_proctor = ui.checkbox('Select from existing proctor', value=False)
        proctor_select = ui.select(
            label='Proctor',
            options={p.id: p.full_name for p in proctors},
            with_input=False
        ).classes('w-full')
        full_name_input = ui.input('Full Name').classes('w-full')
        building_select = ui.select(
            label='Building',
            options={b.id: b.name for b in buildings},
            with_input=True
        ).classes('w-full')

        proctor_select.visible = False
        full_name_input.visible = True

        def toggle_proctor_select(e):
            proctor_select.visible = e.value
            full_name_input.visible = not e.value
            if e.value and proctors:
                proctor_id = proctor_select.value
                if proctor_id is not None:
                    proctor = next((p for p in proctors if p.id == proctor_id), None)
                    if proctor:
                        full_name_input.value = proctor.full_name

        use_proctor.on_value_change(toggle_proctor_select)

        def on_proctor_change(e):
            if use_proctor.value:
                proctor = next((p for p in proctors if p.id == e.value), None)
                if proctor:
                    full_name_input.value = proctor.full_name
        proctor_select.on_value_change(on_proctor_change)

        def save():
            global next_building_supervisor_id
            name = full_name_input.value.strip()
            if not name:
                ui.notify('Name cannot be empty', type='error')
                return
            proctor_id = None
            if use_proctor.value:
                proctor_id = proctor_select.value
            new_supervisor = models.BuildingSupervisor(
                id=next_building_supervisor_id,
                full_name=name,
                building_id=building_select.value,
                proctor_id=proctor_id
            )
            building_supervisors.append(new_supervisor)
            next_building_supervisor_id += 1
            if supervisor_table_refresh:
                supervisor_table_refresh()
            dialog.close()
            ui.notify('Building supervisor added', type='positive')

        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

# ------------------------------------------------------------
# Helper function for exams
# ------------------------------------------------------------
def add_exam_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Exam').classes('text-lg font-bold')
        name_input = ui.input('Exam Name').classes('w-full')
        date_input = ui.input('Date (e.g., 2025-06-15)').classes('w-full')
        time_input = ui.input('Time (e.g., 09:00)').classes('w-full')
        language_options = ['English', 'German', 'Turkish', 'French', 'Spanish']
        language_input = ui.select(
            label='Language (optional)',
            options=language_options,
            with_input=True,
            clearable=True
        ).classes('w-full')
        proctors_default_input = ui.number(
            'Proctors per Classroom (default)',
            value=default_proctors_per_classroom,
            min=1, max=5, step=1
        ).classes('w-full')
        # Distribution strategy dropdown
        strategy_options = {
            'random': 'Random',
            'same_department': 'Same Department',
            'same_faculty': 'Same Faculty'
        }
        strategy_input = ui.select(
            label='Distribution Strategy',
            options=strategy_options,
            value='random',
            with_input=False
        ).classes('w-full')

        session_group_input = ui.input(
            'Session Group (exams with the same label run in parallel)',
            placeholder='e.g., Spring 2025 Morning'
        ).classes('w-full')

        split_by_language_input = ui.checkbox(
            'Split students by language (each language gets its own classrooms)',
            value=False
        )

        def save():
            global next_exam_id
            lang = language_input.value.strip() if language_input.value else None
            new_exam = models.Exam(
                id=next_exam_id,
                name=name_input.value,
                date=date_input.value,
                time=time_input.value,
                language=lang,
                proctors_per_classroom_default=int(proctors_default_input.value),
                distribution_strategy=strategy_input.value,
                session_group=session_group_input.value.strip(),
                split_by_language=split_by_language_input.value
            )
            exams.append(new_exam)
            next_exam_id += 1
            if exam_table_refresh:
                print("DEBUG: exam_table_refresh is not None, calling refresh")
                print(f"DEBUG: after calling refresh, exam_table.rows count = {len(exam_table.rows)}")
                exam_table_refresh()
            else:
                print("DEBUG: exam_table_refresh is None")
            if exam_select_refresh:
                exam_select_refresh()
            if report_exam_select_refresh:
                report_exam_select_refresh()
            dialog.close()
            ui.notify('Exam added', type='positive')

        with ui.row():
            ui.button('Save', on_click=save).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

#-------------------------------
# Save xlsx template
#------------------------------
def save_xlsx_template(filepath, headers, sample_rows, sheet_name='Template'):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in sample_rows:
        ws.append(row)
    wb.save(filepath)

#-------------------------------
# Download Student List Template CSV
#-------------------------------

def download_student_template():
    template_content = "Student ID,Full Name,Faculty,Department,Language\n1001,John Doe,Engineering,Computer Science,English\n1002,Jane Smith,Arts,History,German\n"

    # Create a hidden tkinter root window for the dialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="student_template.csv",
        title="Save Student Template As"
    )

    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(template_content)
            ui.notify(f'Template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')

    root.destroy()

#--------------------------------
# Download student list template XLSX
#--------------------------------
def download_student_template_xlsx():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="student_template.xlsx",
        title="Save Student Template (XLSX) As"
    )
    if file_path:
        try:
            save_xlsx_template(
                file_path,
                ['Student ID', 'Full Name', 'Faculty', 'Department', 'Language'],
                [
                    [1001, 'John Doe', 'Engineering', 'Computer Science', 'English'],
                    [1002, 'Jane Smith', 'Arts', 'History', 'German'],
                ],
                sheet_name='Students'
            )
            ui.notify(f'XLSX template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#--------------------------------
# Download Proctor list template XLSX
#--------------------------------
def download_proctor_template_xlsx():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="proctor_template.xlsx",
        title="Save Proctor Template (XLSX) As"
    )
    if file_path:
        try:
            save_xlsx_template(
                file_path,
                ['ID', 'Full Name', 'Department', 'Languages', 'Preferred Building', 'Can be supervisor', 'Reserve'],
                [
                    [1, 'John Doe', 'Engineering', 'English,German', 'Building A', 'Yes', 'No'],
                    [2, 'Jane Smith', 'Arts', 'English', '', 'No', 'Yes'],
                ],
                sheet_name='Proctors'
            )
            ui.notify(f'XLSX template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#--------------------------------
# Download building list template XLSX
#--------------------------------
def download_building_template_xlsx():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="building_template.xlsx",
        title="Save Building Template (XLSX) As"
    )
    if file_path:
        try:
            save_xlsx_template(
                file_path,
                ['ID', 'Name'],
                [[1, 'Building A'], [2, 'Building B']],
                sheet_name='Buildings'
            )
            ui.notify(f'XLSX template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#--------------------------------
# Download classroom list template XLSX
#--------------------------------
def download_classroom_template_xlsx():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="classroom_template.xlsx",
        title="Save Classroom Template (XLSX) As"
    )
    if file_path:
        try:
            save_xlsx_template(
                file_path,
                ['ID', 'Building', 'Classroom Name', 'Capacity', 'Is Reserve'],
                [
                    [1, 'Building A', 'A101', 30, 'No'],
                    [2, 'Building A', 'A102', 25, 'No'],
                    [3, 'Building B', 'B201', 40, 'Yes'],
                ],
                sheet_name='Classrooms'
            )
            ui.notify(f'XLSX template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#--------------------------------
# Download building supervisor list template XLSX
#--------------------------------
def download_supervisor_template_xlsx():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="building_supervisor_template.xlsx",
        title="Save Building Supervisor Template (XLSX) As"
    )
    if file_path:
        try:
            save_xlsx_template(
                file_path,
                ['ID', 'Full Name', 'Building', 'Proctor ID'],
                [
                    [1, 'John Supervisor', 'Building A', ''],
                    [2, 'Jane Supervisor', 'Building B', 5],
                ],
                sheet_name='Supervisors'
            )
            ui.notify(f'XLSX template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#-------------------------------
# Download proctor list template
#-------------------------------

def download_proctor_template():
    template_content = "ID,Full Name,Department,Languages,Preferred Building,Can be supervisor,Reserve\n1,John Doe,Engineering,\"English,German\",Building A,Yes,No\n2,Jane Smith,Arts,English,,No,Yes\n"
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="proctor_template.csv",
        title="Save Proctor Template As"
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(template_content)
            ui.notify(f'Template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#-------------------------------
# Download building list template
#-------------------------------
def download_building_template():
    template_content = "ID,Name\n1,Building A\n2,Building B\n"
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="building_template.csv",
        title="Save Building Template As"
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(template_content)
            ui.notify(f'Template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#----------------------------------
#Download Classroom List Template
#---------------------------------

def download_classroom_template():
    template_content = "ID,Building,Classroom Name,Capacity,Is Reserve\n1,Building A,A101,30,No\n2,Building A,A102,25,No\n3,Building B,B201,40,Yes\n"
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="classroom_template.csv",
        title="Save Classroom Template As"
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(template_content)
            ui.notify(f'Template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#-------------------------------
# Download Building Supervisor List Template
#-------------------------------
def download_supervisor_template():
    template_content = "ID,Full Name,Building,Proctor ID\n1,John Supervisor,Building A,\n2,Jane Supervisor,Building B,5\n"
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="building_supervisor_template.csv",
        title="Save Building Supervisor Template As"
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(template_content)
            ui.notify(f'Template saved to {file_path}', type='positive')
        except Exception as e:
            ui.notify(f'Error saving template: {e}', type='error')
    root.destroy()

#-------------------------------
# Import students
#-------------------------------

def import_students_dialog():
    if not exams:
        with ui.dialog() as prompt_dialog, ui.card():
            ui.label('No exams found').classes('text-lg font-bold')
            ui.label('You need to create at least one exam before importing students.')
            with ui.row():
                ui.button('Create Exam', on_click=lambda: (prompt_dialog.close(), add_exam_dialog()))
                ui.button('Cancel', on_click=prompt_dialog.close)
        prompt_dialog.open()
        return

    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Import Students').classes('text-lg font-bold')
        exam_select = ui.select(
            label='Assign to Exam',
            options={e.id: f"{e.name} ({e.language or 'No lang'})" for e in exams},
            with_input=False
        ).classes('w-full')

        data_holder = {'rows': []}

        preview_columns = [
            {'name': 'id', 'label': 'Student ID', 'field': 'id'},
            {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
            {'name': 'faculty', 'label': 'Faculty', 'field': 'faculty'},
            {'name': 'department', 'label': 'Department', 'field': 'department'},
            {'name': 'language', 'label': 'Language', 'field': 'language'},
        ]
        preview_table = ui.table(columns=preview_columns, rows=[], row_key='id').classes('w-full')
        preview_table.visible = False

        async def handle_upload(e):
            ui.notify('File uploaded, processing...', type='info')
            try:
                content = await e.file.read()
                rows_raw = read_upload_rows(content, getattr(e.file, 'name', ''))
                if not rows_raw:
                    ui.notify('File is empty', type='error')
                    return

                first_row = rows_raw[0]
                first_cell = first_row[0].strip().lower() if first_row and first_row[0] else ''
                has_header = not first_cell.isdigit()

                if has_header:
                    header = [h.strip().lower() for h in first_row]
                    id_cols = ['student id', 'öğrenci no', 'öğrenci numarası', 'id']
                    name_cols = ['full name', 'ad soyad', 'adı soyadı', 'ad', 'name']
                    faculty_cols = ['faculty', 'fakülte', 'fac']
                    dept_cols = ['department', 'bölüm', 'dept']
                    lang_cols = ['language', 'dil tercihi', 'dil', 'lang']

                    id_idx = next((i for i, h in enumerate(header) if h in id_cols), None)
                    name_idx = next((i for i, h in enumerate(header) if h in name_cols), None)
                    faculty_idx = next((i for i, h in enumerate(header) if h in faculty_cols), None)
                    dept_idx = next((i for i, h in enumerate(header) if h in dept_cols), None)
                    lang_idx = next((i for i, h in enumerate(header) if h in lang_cols), None)
                    exam_id_idx = next((i for i, h in enumerate(header) if h in ['exam id', 'examid']), None)
                    data_rows = rows_raw[1:]
                else:
                    id_idx = 1
                    name_idx = 2
                    faculty_idx = 3
                    dept_idx = 4
                    lang_idx = 5 if len(first_row) > 5 else None
                    exam_id_idx = None
                    data_rows = rows_raw

                if id_idx is None or name_idx is None or faculty_idx is None or dept_idx is None:
                    ui.notify('Could not identify required columns: Student ID, Full Name, Faculty, Department', type='error')
                    return

                rows = []
                for row in data_rows:
                    if not row or all(not cell.strip() for cell in row):
                        continue
                    try:
                        sid = int(row[id_idx].strip())
                    except (ValueError, IndexError):
                        ui.notify(f'Skipping row with invalid Student ID: {row}', type='warning')
                        continue
                    full_name = row[name_idx].strip() if name_idx < len(row) else ''
                    faculty = row[faculty_idx].strip() if faculty_idx < len(row) else ''
                    department = row[dept_idx].strip() if dept_idx < len(row) else ''
                    language = normalize_language(row[lang_idx].strip()) if lang_idx is not None and lang_idx < len(row) else None
                    eid = int(row[exam_id_idx].strip()) if exam_id_idx is not None and exam_id_idx < len(row) and row[exam_id_idx].strip() else exam_select.value

                    rows.append({
                        'id': sid,
                        'full_name': full_name,
                        'faculty': faculty,
                        'department': department,
                        'exam_id': eid,
                        'language': language,
                    })
                data_holder['rows'] = rows
                preview_table.rows = rows
                preview_table.visible = True
                preview_table.update()
                ui.notify(f'Loaded {len(rows)} rows. Click Import to add.', type='positive')
            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', type='error')

        ui.upload(
            label='Choose CSV or XLSX file',
            auto_upload=True,
            max_file_size=10_000_000,
            on_upload=handle_upload
        ).classes('w-full')

        with ui.row().classes('items-center gap-2'):
            ui.button('Download CSV Template', on_click=download_student_template).props('color=secondary')
            ui.button('Download XLSX Template', on_click=download_student_template_xlsx).props('color=secondary')

        def do_import():
            rows = data_holder['rows']
            if not rows:
                ui.notify('No data to import. Please upload a file first.', type='warning')
                return
            exam_id_now = exam_select.value
            if exam_id_now is None:
                ui.notify('Please select an exam first', type='warning')
                return
            global next_student_id
            existing_ids = {s.id for s in students}
            imported_count = 0
            for row in rows:
                if row['id'] in existing_ids:
                    ui.notify(f"Student ID {row['id']} already exists, skipping", type='warning')
                    continue
                new_student = models.Student(
                    id=row['id'],
                    full_name=row['full_name'],
                    faculty=row['faculty'],
                    department=row['department'],
                    exam_id=exam_id_now,
                    language=row.get('language')
                )
                students.append(new_student)
                imported_count += 1
            if students:
                next_student_id = max(s.id for s in students) + 1
            # Use the standard refresh to also update the count label
            if student_table_refresh:
                student_table_refresh()
            autosave()
            dialog.close()
            ui.notify(f'Imported {imported_count} student(s).', type='positive')

        with ui.row():
            ui.button('Import', on_click=do_import).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

#------------------------------
# import proctors dialogue
#------------------------------
def import_proctors_dialog():
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Import Proctors from CSV').classes('text-lg font-bold')

        # Data holder
        data_holder = {'rows': []}

        preview_columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
            {'name': 'department', 'label': 'Department', 'field': 'department'},
            {'name': 'languages', 'label': 'Languages', 'field': 'languages'},
            {'name': 'preferred_building', 'label': 'Preferred Building', 'field': 'preferred_building'},
            {'name': 'can_be_supervisor', 'label': 'Supervisor?', 'field': 'can_be_supervisor'},
            {'name': 'is_reserve', 'label': 'Reserve?', 'field': 'is_reserve'},
        ]
        preview_table = ui.table(columns=preview_columns, rows=[], row_key='id').classes('w-full')
        preview_table.visible = False

        async def handle_upload(e):
            ui.notify('File uploaded, processing...', type='info')
            try:
                content = await e.file.read()
                rows_raw = read_upload_rows(content, getattr(e.file, 'name', ''))
                if not rows_raw:
                    ui.notify('CSV file is empty', type='error')
                    return
                header = [h.strip().lower() for h in rows_raw[0]]
                id_idx = next((i for i, h in enumerate(header) if h in ['id', 'proctor id', 'proctorid']), None)
                name_idx = next((i for i, h in enumerate(header) if h in ['full name', 'fullname', 'name']), None)
                dept_idx = next((i for i, h in enumerate(header) if h in ['department', 'dept']), None)
                lang_idx = next((i for i, h in enumerate(header) if h in ['languages', 'language']), None)
                building_idx = next((i for i, h in enumerate(header) if h in ['preferred building', 'preferredbuilding', 'building']), None)
                supervisor_idx = next((i for i, h in enumerate(header) if h in ['can be supervisor', 'canbesupervisor', 'supervisor']), None)
                reserve_idx = next((i for i, h in enumerate(header) if h in ['reserve', 'is reserve', 'reserve proctor']), None)

                if id_idx is None or name_idx is None or dept_idx is None:
                    ui.notify('CSV must contain columns: ID, Full Name, Department', type='error')
                    return

                rows = []
                for row in rows_raw[1:]:
                    try:
                        pid = int(row[id_idx])
                    except (ValueError, IndexError):
                        continue
                    full_name = row[name_idx].strip() if name_idx < len(row) else ''
                    department = row[dept_idx].strip() if dept_idx < len(row) else ''
                    if lang_idx is not None and lang_idx < len(row):
                        lang_list = [l.strip() for l in row[lang_idx].split(',') if l.strip()]
                    else:
                        lang_list = []
                    building_name = row[building_idx].strip() if building_idx is not None and building_idx < len(row) else ''
                    preferred_building_id = None
                    if building_name:
                        building = next((b for b in buildings if b.name.lower() == building_name.lower()), None)
                        if building:
                            preferred_building_id = building.id
                        else:
                            ui.notify(f'Building "{building_name}" not found; leaving as None', type='warning')
                    sup_value = row[supervisor_idx].strip().lower() if supervisor_idx is not None and supervisor_idx < len(row) else 'yes'
                    can_be_supervisor = sup_value in ['yes', 'true', '1', 'y']
                    reserve_value = row[reserve_idx].strip().lower() if reserve_idx is not None and reserve_idx < len(row) else 'no'
                    is_reserve = reserve_value in ['yes', 'true', '1', 'y']

                    rows.append({
                        'id': pid,
                        'full_name': full_name,
                        'department': department,
                        'languages': ', '.join(lang_list),
                        'preferred_building': building_name,
                        'preferred_building_id': preferred_building_id,
                        'can_be_supervisor': can_be_supervisor,
                        'is_reserve': is_reserve,
                    })
                data_holder['rows'] = rows
                preview_table.rows = rows
                preview_table.visible = True
                preview_table.update()
                ui.notify(f'Loaded {len(rows)} rows. Click Import to add.', type='positive')
            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', type='error')

        ui.upload(
            label='Choose File',
            auto_upload=True,
            max_file_size=10_000_000,
            on_upload=handle_upload
        ).classes('w-full')

        with ui.row().classes('items-center gap-2'):
            ui.button('Download CSV Template', on_click=download_proctor_template).props('color=secondary')
            ui.button('Download XLSX Template', on_click=download_proctor_template_xlsx).props('color=secondary')

        def do_import():
            rows = data_holder['rows']
            if not rows:
                ui.notify('No data to import. Please upload a CSV first.', type='warning')
                return
            global next_proctor_id
            existing_ids = {p.id for p in proctors}
            imported_count = 0
            for row in rows:
                if row['id'] in existing_ids:
                    ui.notify(f"Proctor ID {row['id']} already exists, skipping", type='warning')
                    continue
                new_proctor = models.Proctor(
                    id=row['id'],
                    full_name=row['full_name'],
                    department=row['department'],
                    languages=row['languages'].split(', ') if row['languages'] else [],
                    preferred_building_id=row['preferred_building_id'],
                    can_be_supervisor=row['can_be_supervisor'],
                    is_reserve=row['is_reserve'],
                )
                proctors.append(new_proctor)
                imported_count += 1
            if proctors:
                next_proctor_id = max(p.id for p in proctors) + 1
            if proctor_table_refresh:
                proctor_table_refresh()
            dialog.close()
            ui.notify(f'Imported {imported_count} proctors', type='positive')

        with ui.row():
            ui.button('Import', on_click=do_import).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

#------------------------------------
# Import Buildings Dialogue
#------------------------------------
def import_buildings_dialog():
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Import Buildings from CSV or XLSX').classes('text-lg font-bold')

        data_holder = {'rows': []}

        preview_columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'name', 'label': 'Name', 'field': 'name'},
        ]
        preview_table = ui.table(columns=preview_columns, rows=[], row_key='id').classes('w-full')
        preview_table.visible = False

        async def handle_upload(e):
            try:
                content = await e.file.read()
                rows_raw = read_upload_rows(content, getattr(e.file, 'name', ''))
                if not rows_raw:
                    ui.notify('File is empty', type='error')
                    return
                header = [h.strip().lower() for h in rows_raw[0]]
                id_idx = next((i for i, h in enumerate(header) if h in ['id', 'building id', 'buildingid']), None)
                name_idx = next((i for i, h in enumerate(header) if h in ['name', 'building name']), None)
                if id_idx is None or name_idx is None:
                    ui.notify('File must contain columns: ID, Name', type='error')
                    return

                rows = []
                for row in rows_raw[1:]:
                    try:
                        bid = int(row[id_idx])
                    except (ValueError, IndexError):
                        continue
                    name = row[name_idx].strip() if name_idx < len(row) else ''
                    if not name:
                        continue
                    rows.append({'id': bid, 'name': name})
                data_holder['rows'] = rows
                preview_table.rows = rows
                preview_table.visible = True
                preview_table.update()
                ui.notify(f'Loaded {len(rows)} rows. Click Import to add.', type='positive')
            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', type='error')

        ui.upload(
            label='Choose CSV or XLSX file',
            auto_upload=True,
            max_file_size=10_000_000,
            on_upload=handle_upload
        ).classes('w-full')

        with ui.row().classes('items-center gap-2'):
            ui.button('Download CSV Template', on_click=download_building_template).props('color=secondary')
            ui.button('Download XLSX Template', on_click=download_building_template_xlsx).props('color=secondary')

        def do_import():
            rows = data_holder['rows']
            if not rows:
                ui.notify('No data to import. Please upload a file first.', type='warning')
                return
            global next_building_id
            existing_ids = {b.id for b in buildings}
            imported_count = 0
            for row in rows:
                if row['id'] in existing_ids:
                    ui.notify(f"Building ID {row['id']} already exists, skipping", type='warning')
                    continue
                new_building = models.Building(id=row['id'], name=row['name'])
                buildings.append(new_building)
                imported_count += 1
            if buildings:
                next_building_id = max(b.id for b in buildings) + 1
            if building_table_refresh:
                building_table_refresh()
            autosave()
            dialog.close()
            ui.notify(f'Imported {imported_count} buildings', type='positive')

        with ui.row():
            ui.button('Import', on_click=do_import).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()
#--------------------------------
#Import Classrooms Dialogue
#---------------------------------
def import_classrooms_dialog():
    if not buildings:
        ui.notify('Please add at least one building first', type='warning')
        return

    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Import Classrooms from CSV').classes('text-lg font-bold')

        data_holder = {'rows': []}

        preview_columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'building', 'label': 'Building', 'field': 'building'},
            {'name': 'name', 'label': 'Classroom Name', 'field': 'name'},
            {'name': 'capacity', 'label': 'Capacity', 'field': 'capacity'},
            {'name': 'is_reserve', 'label': 'Reserve', 'field': 'is_reserve'},
        ]
        preview_table = ui.table(columns=preview_columns, rows=[], row_key='id').classes('w-full')
        preview_table.visible = False

        async def handle_upload(e):
            ui.notify('File uploaded, processing...', type='info')
            try:
                content = await e.file.read()
                rows_raw = read_upload_rows(content, getattr(e.file, 'name', ''))
                if not rows_raw:
                    ui.notify('CSV file is empty', type='error')
                    return
                header = [h.strip().lower() for h in rows_raw[0]]
                id_idx = next((i for i, h in enumerate(header) if h in ['id', 'classroom id', 'classroomid']), None)
                building_idx = next((i for i, h in enumerate(header) if h in ['building', 'building name']), None)
                name_idx = next((i for i, h in enumerate(header) if h in ['classroom name', 'classroomname', 'name']), None)
                capacity_idx = next((i for i, h in enumerate(header) if h in ['capacity', 'cap']), None)
                reserve_idx = next((i for i, h in enumerate(header) if h in ['is reserve', 'reserve', 'isreserve']), None)

                if id_idx is None or building_idx is None or name_idx is None or capacity_idx is None:
                    ui.notify('CSV must contain columns: ID, Building, Classroom Name, Capacity', type='error')
                    return

                rows = []
                for row in rows_raw[1:]:
                    try:
                        cid = int(row[id_idx])
                    except (ValueError, IndexError):
                        continue
                    building_name = row[building_idx].strip() if building_idx < len(row) else ''
                    classroom_name = row[name_idx].strip() if name_idx < len(row) else ''
                    capacity = int(row[capacity_idx]) if capacity_idx < len(row) else 0
                    is_reserve = False
                    if reserve_idx is not None and reserve_idx < len(row):
                        val = row[reserve_idx].strip().lower()
                        is_reserve = val in ['yes', 'true', '1', 'y']
                    building = next((b for b in buildings if b.name.lower() == building_name.lower()), None)
                    if not building:
                        ui.notify(f'Building "{building_name}" not found; skipping classroom {classroom_name}', type='warning')
                        continue
                    rows.append({
                        'id': cid,
                        'building': building_name,
                        'building_id': building.id,
                        'name': classroom_name,
                        'capacity': capacity,
                        'is_reserve': is_reserve,
                    })
                data_holder['rows'] = rows
                preview_table.rows = [
                    {'id': r['id'], 'building': r['building'], 'name': r['name'],
                     'capacity': r['capacity'], 'is_reserve': r['is_reserve']}
                    for r in rows
                ]
                preview_table.visible = True
                preview_table.update()
                ui.notify(f'Loaded {len(rows)} rows. Click Import to add.', type='positive')
            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', type='error')

        ui.upload(
            label='Choose File',
            auto_upload=True,
            max_file_size=10_000_000,
            on_upload=handle_upload
        ).classes('w-full')

        with ui.row().classes('items-center gap-2'):
            ui.button('Download CSV Template', on_click=download_classroom_template).props('color=secondary')
            ui.button('Download XLSX Template', on_click=download_classroom_template_xlsx).props('color=secondary')

        def do_import():
            rows = data_holder['rows']
            if not rows:
                ui.notify('No data to import. Please upload a CSV first.', type='warning')
                return
            global next_classroom_id
            existing_ids = {c.id for c in classrooms}
            imported_count = 0
            for row in rows:
                if row['id'] in existing_ids:
                    ui.notify(f"Classroom ID {row['id']} already exists, skipping", type='warning')
                    continue
                new_classroom = models.Classroom(
                    id=row['id'],
                    building_id=row['building_id'],
                    name=row['name'],
                    capacity=row['capacity'],
                    is_reserve=row['is_reserve'],
                )
                classrooms.append(new_classroom)
                imported_count += 1
            if classrooms:
                next_classroom_id = max(c.id for c in classrooms) + 1
            if classroom_table_refresh:
                classroom_table_refresh()
            dialog.close()
            ui.notify(f'Imported {imported_count} classrooms', type='positive')

        with ui.row():
            ui.button('Import', on_click=do_import).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

#------------------------------
# Import Building Supervisors Dialogue
#------------------------------
def import_supervisors_dialog():
    if not buildings:
        ui.notify('Please add at least one building first', type='warning')
        return

    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Import Building Supervisors from CSV').classes('text-lg font-bold')

        data_holder = {'rows': []}

        preview_columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
            {'name': 'building', 'label': 'Building', 'field': 'building'},
            {'name': 'proctor_id', 'label': 'Proctor ID', 'field': 'proctor_id'},
        ]
        preview_table = ui.table(columns=preview_columns, rows=[], row_key='id').classes('w-full')
        preview_table.visible = False

        async def handle_upload(e):
            ui.notify('File uploaded, processing...', type='info')
            try:
                content = await e.file.read()
                rows_raw = read_upload_rows(content, getattr(e.file, 'name', ''))
                if not rows_raw:
                    ui.notify('CSV file is empty', type='error')
                    return
                header = [h.strip().lower() for h in rows_raw[0]]
                id_idx = next((i for i, h in enumerate(header) if h in ['id', 'supervisor id', 'supervisorid']), None)
                name_idx = next((i for i, h in enumerate(header) if h in ['full name', 'fullname', 'name']), None)
                building_idx = next((i for i, h in enumerate(header) if h in ['building', 'building name']), None)
                proctor_idx = next((i for i, h in enumerate(header) if h in ['proctor id', 'proctorid']), None)

                if id_idx is None or name_idx is None or building_idx is None:
                    ui.notify('CSV must contain columns: ID, Full Name, Building', type='error')
                    return

                rows = []
                for row in rows_raw[1:]:
                    try:
                        sid = int(row[id_idx])
                    except (ValueError, IndexError):
                        continue
                    full_name = row[name_idx].strip() if name_idx < len(row) else ''
                    building_name = row[building_idx].strip() if building_idx < len(row) else ''
                    building = next((b for b in buildings if b.name.lower() == building_name.lower()), None)
                    if not building:
                        ui.notify(f'Building "{building_name}" not found; skipping supervisor {full_name}', type='warning')
                        continue
                    proctor_id = None
                    if proctor_idx is not None and proctor_idx < len(row) and row[proctor_idx].strip():
                        try:
                            proctor_id = int(row[proctor_idx])
                            if not any(p.id == proctor_id for p in proctors):
                                ui.notify(f'Proctor ID {proctor_id} not found; leaving unlinked', type='warning')
                                proctor_id = None
                        except ValueError:
                            ui.notify(f'Invalid Proctor ID "{row[proctor_idx]}" for {full_name}; skipping', type='warning')
                            continue
                    rows.append({
                        'id': sid,
                        'full_name': full_name,
                        'building': building_name,
                        'building_id': building.id,
                        'proctor_id': proctor_id,
                    })
                data_holder['rows'] = rows
                preview_table.rows = rows
                preview_table.visible = True
                preview_table.update()
                ui.notify(f'Loaded {len(rows)} rows. Click Import to add.', type='positive')
            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', type='error')

        ui.upload(
            label='Choose File',
            auto_upload=True,
            max_file_size=10_000_000,
            on_upload=handle_upload
        ).classes('w-full')

        with ui.row().classes('items-center gap-2'):
            ui.button('Download CSV Template', on_click=download_supervisor_template).props('color=secondary')
            ui.button('Download XLSX Template', on_click=download_supervisor_template_xlsx).props('color=secondary')

        def do_import():
            rows = data_holder['rows']
            if not rows:
                ui.notify('No data to import. Please upload a CSV first.', type='warning')
                return
            global next_building_supervisor_id
            existing_ids = {s.id for s in building_supervisors}
            imported_count = 0
            for row in rows:
                if row['id'] in existing_ids:
                    ui.notify(f"Supervisor ID {row['id']} already exists, skipping", type='warning')
                    continue
                new_supervisor = models.BuildingSupervisor(
                    id=row['id'],
                    full_name=row['full_name'],
                    building_id=row['building_id'],
                    proctor_id=row['proctor_id'],
                )
                building_supervisors.append(new_supervisor)
                imported_count += 1
            if building_supervisors:
                next_building_supervisor_id = max(s.id for s in building_supervisors) + 1
            if supervisor_table_refresh:
                supervisor_table_refresh()
            dialog.close()
            ui.notify(f'Imported {imported_count} building supervisors', type='positive')

        with ui.row():
            ui.button('Import', on_click=do_import).props('color=primary')
            ui.button('Cancel', on_click=dialog.close)
    dialog.open()

    autosave()

#----------------------------
# Export students
#----------------------------
def export_students_csv():
    if not students:
        ui.notify('No students to export', type='warning')
        return
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Full Name', 'Faculty', 'Department', 'Exam ID', 'Language'])
    for s in students:
        writer.writerow([s.id, s.full_name, s.faculty, s.department, s.exam_id, s.language or ''])
    csv_content = output.getvalue()
    # Trigger download using NiceGUI's ui.download
    ui.download(csv_content.encode('utf-8'), 'students.csv', 'text/csv')

# ------------------------------------------------------------
# Main UI
# ------------------------------------------------------------
auto_load()
ui.colors(primary='#243f90', secondary='#cb9932', accent='#77aed5', negative='#A91101')

with ui.header().classes('items-center justify-between'):
    ui.label('High Stakes Exam Organizer').classes('text-2xl font-bold text-white')
    ui.space()
    ui.button('Settings', on_click=lambda: ui.notify('Settings will be implemented later'))

with ui.tabs().classes('w-full') as tabs:
    tab_data = ui.tab('Data Entry')
    tab_assign = ui.tab('Assignment')
    tab_reports = ui.tab('Reports')
    tab_settings = ui.tab('Settings')
    tab_about = ui.tab('About')

with ui.tab_panels(tabs, value=tab_data).classes('w-full flex-grow'):
    # -------------------- DATA ENTRY TAB --------------------
    with ui.tab_panel(tab_data):
        with ui.tabs().classes('w-full') as data_tabs:
            subtab_exams = ui.tab('Exams')
            subtab_buildings = ui.tab('Buildings')
            subtab_classrooms = ui.tab('Classrooms')
            subtab_students = ui.tab('Students')
            subtab_proctors = ui.tab('Proctors')
            subtab_supervisors = ui.tab('Building Supervisors')

        with ui.tab_panels(data_tabs, value=subtab_exams).classes('w-full'):
        # -------------------- EXAMS --------------------
            with ui.tab_panel(subtab_exams):
                def get_exam_rows():
                    rows = []
                    for e in exams:
                        rows.append({
                            'id': e.id,
                            'name': e.name,
                            'date': e.date,
                            'time': e.time,
                            'language': e.language if e.language else '-',
                            'proctors_default': e.proctors_per_classroom_default,
                            'strategy': e.distribution_strategy,
                        })
                    return rows

                def refresh_exam_table(search_text=''):
                    all_rows = get_exam_rows()
                    if search_text:
                        s = search_text.lower()
                        filtered = [
                            r for r in all_rows
                            if s in str(r['id']).lower()
                            or s in r['name'].lower()
                            or s in r['language'].lower()
                            or s in r['date'].lower()
                        ]
                    else:
                        filtered = all_rows
                    exam_table.rows = filtered
                    exam_table.update()

                exam_table_refresh = refresh_exam_table

                def edit_selected_exam():
                    selected = exam_table.selected
                    if not selected:
                        ui.notify('No exam selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        exam_id = selected[0].get('id')
                    else:
                        try:
                            exam_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    exam = next((e for e in exams if e.id == exam_id), None)
                    if not exam:
                        ui.notify(f'Exam ID {exam_id} not found', type='error')
                        return

                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Exam').classes('text-lg font-bold')
                        name_input = ui.input('Exam Name', value=exam.name).classes('w-full')
                        date_input = ui.input('Date (e.g., 2025-06-15)', value=exam.date).classes('w-full')
                        time_input = ui.input('Time (e.g., 09:00)', value=exam.time).classes('w-full')
                        language_options = ['English', 'German', 'Turkish', 'French', 'Spanish']
                        language_input = ui.select(
                            label='Language (optional)',
                            options=language_options,
                            value=exam.language if exam.language else None,
                            with_input=True,
                            clearable=True
                        ).classes('w-full')
                        proctors_default_input = ui.number(
                            'Proctors per Classroom (default)',
                            value=exam.proctors_per_classroom_default,
                            min=1, max=5, step=1
                        ).classes('w-full')
                        strategy_options = {
                            'random': 'Random',
                            'same_department': 'Same Department',
                            'same_faculty': 'Same Faculty'
                        }
                        strategy_input = ui.select(
                            label='Distribution Strategy',
                            options=strategy_options,
                            value=exam.distribution_strategy,
                            with_input=False
                        ).classes('w-full')
                        session_group_input = ui.input(
                            'Session Group (exams with the same label run in parallel)',
                            value=exam.session_group,
                            placeholder='e.g., Spring 2025 Morning'
                        ).classes('w-full')
                        split_by_language_input = ui.checkbox(
                            'Split students by language (each language gets its own classrooms)',
                            value=exam.split_by_language
                        )

                        def save_edit(close_dialog=True):
                            old_count = exam.proctors_per_classroom_default
                            old_lang = exam.language
                            old_strategy = exam.distribution_strategy
                            old_session = exam.session_group
                            old_split = exam.split_by_language

                            new_count = int(proctors_default_input.value)
                            new_lang = language_input.value.strip() if language_input.value else None
                            new_strategy = strategy_input.value
                            new_session = session_group_input.value.strip()
                            new_split = split_by_language_input.value

                            exam.name = name_input.value.strip()
                            exam.date = date_input.value.strip()
                            exam.time = time_input.value.strip()
                            exam.language = new_lang
                            exam.proctors_per_classroom_default = new_count
                            exam.distribution_strategy = new_strategy
                            exam.session_group = new_session
                            exam.split_by_language = new_split

                            refresh_exam_table(exam_search_input.value)
                            if exam_select_refresh:
                                exam_select_refresh()
                            if report_exam_select_refresh:
                                report_exam_select_refresh()

                            has_assignments = any(a.exam_id == exam.id for a in assignments)
                            if has_assignments and (old_count != new_count or old_lang != new_lang or old_strategy != new_strategy or old_session != new_session or old_split != new_split):
                                ui.notify('Exam settings changed. Please re-run Auto-Assign for this exam.', type='warning')
                            else:
                                ui.notify('Exam updated', type='positive')
                            autosave()
                            if close_dialog:
                                edit_dialog.close()

                        def save_and_regenerate():
                            save_edit(close_dialog=False)
                            if run_assignment_global:
                                run_assignment_global(exam.id)
                                ui.notify('Assignments regenerated', type='positive')
                            else:
                                ui.notify('Assignment engine not ready', type='error')
                            edit_dialog.close()

                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Save & Regenerate', on_click=save_and_regenerate).props('color=accent')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                with ui.row().classes('items-center'):
                    ui.label('Exams').classes('text-xl font-bold')
                    ui.space()
                    ui.button('Add Exam', on_click=add_exam_dialog).props('color=primary')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_exam()).props('color=secondary')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_exams()).props('color=negative')

                exam_search_input = ui.input('Search exams...', placeholder='Type to filter').classes('w-full')

                exam_columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
                    {'name': 'date', 'label': 'Date', 'field': 'date', 'sortable': True},
                    {'name': 'time', 'label': 'Time', 'field': 'time', 'sortable': True},
                    {'name': 'language', 'label': 'Language', 'field': 'language', 'sortable': True},
                    {'name': 'proctors_default', 'label': 'Proctors/Class', 'field': 'proctors_default', 'sortable': True},
                    {'name': 'strategy', 'label': 'Strategy', 'field': 'strategy', 'sortable': True},
                ]
                exam_table = ui.table(
                    columns=exam_columns,
                    rows=get_exam_rows(),
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id'},
                ).classes('w-full')

                exam_search_input.on_value_change(lambda e: refresh_exam_table(e.value))

                def delete_selected_exams():
                    selected = exam_table.selected
                    if not selected:
                        ui.notify('No exams selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    for eid in selected_ids:
                        students_ref = [s for s in students if s.exam_id == eid]
                        assignments_ref = [a for a in assignments if a.exam_id == eid]
                        if students_ref or assignments_ref:
                            ui.notify(
                                f'Cannot delete exam ID {eid}: {len(students_ref)} students and '
                                f'{len(assignments_ref)} assignments reference it.',
                                type='error'
                            )
                            return
                    global exams
                    exams = [e for e in exams if e.id not in selected_ids]
                    refresh_exam_table(exam_search_input.value)
                    if exam_select_refresh:
                        exam_select_refresh()
                    if report_exam_select_refresh:
                        report_exam_select_refresh()
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} exam(s)', type='positive')

            # -------------------- BUILDINGS --------------------
            with ui.tab_panel(subtab_buildings):
                def get_building_rows():
                    return [{'id': b.id, 'name': b.name} for b in buildings]

                def refresh_building_table(search_text=''):
                    all_rows = get_building_rows()
                    if search_text:
                        s = search_text.lower()
                        filtered = [r for r in all_rows if s in str(r['id']).lower() or s in r['name'].lower()]
                    else:
                        filtered = all_rows
                    building_table.rows = filtered
                    building_table.update()

                building_table_refresh = refresh_building_table

                def edit_selected_building():
                    selected = building_table.selected
                    if not selected:
                        ui.notify('No building selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        building_id = selected[0].get('id')
                    else:
                        try:
                            building_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    building = next((b for b in buildings if b.id == building_id), None)
                    if not building:
                        ui.notify(f'Building ID {building_id} not found', type='error')
                        return
                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Building').classes('text-lg font-bold')
                        name_input = ui.input('Building Name', value=building.name).classes('w-full')
                        def save_edit():
                            building.name = name_input.value.strip()
                            if not building.name:
                                ui.notify('Name cannot be empty', type='error')
                                return
                            refresh_building_table(building_search_input.value)
                            autosave()
                            edit_dialog.close()
                            ui.notify('Building updated', type='positive')
                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                with ui.row().classes('items-center'):
                    ui.label('Buildings').classes('text-xl font-bold')
                    ui.space()
                    ui.button('Add Building', on_click=add_building_dialog).props('color=primary')
                    ui.button('Import', on_click=import_buildings_dialog).props('color=secondary')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_building()).props('color=secondary')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_buildings()).props('color=negative')

                building_search_input = ui.input('Search buildings...', placeholder='Type to filter').classes('w-full')

                building_columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
                ]
                building_table = ui.table(
                    columns=building_columns,
                    rows=get_building_rows(),
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id'},
                ).classes('w-full')

                building_search_input.on_value_change(lambda e: refresh_building_table(e.value))

                def delete_selected_buildings():
                    selected = building_table.selected
                    if not selected:
                        ui.notify('No buildings selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    classrooms_in_building = [c for c in classrooms if c.building_id in selected_ids]
                    if classrooms_in_building:
                        ui.notify('Cannot delete buildings that have classrooms. Delete classrooms first.', type='error')
                        return
                    global buildings
                    buildings = [b for b in buildings if b.id not in selected_ids]
                    refresh_building_table(building_search_input.value)
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} building(s)', type='positive')

            # -------------------- CLASSROOMS --------------------
            with ui.tab_panel(subtab_classrooms):
                def get_classroom_rows():
                    rows = []
                    for c in classrooms:
                        building_name = next((b.name for b in buildings if b.id == c.building_id), 'Unknown')
                        rows.append({
                            'id': c.id,
                            'building': building_name,
                            'name': c.name,
                            'capacity': c.capacity,
                            'is_reserve': c.is_reserve,
                        })
                    return rows

                def refresh_classroom_table(search_text=''):
                    all_rows = get_classroom_rows()
                    if search_text:
                        search_text = search_text.lower()
                        filtered = [
                            row for row in all_rows
                            if search_text in str(row['id']).lower()
                            or search_text in row['building'].lower()
                            or search_text in row['name'].lower()
                        ]
                    else:
                        filtered = all_rows
                    classroom_table.rows = filtered
                    classroom_table.update()

                classroom_table_refresh = refresh_classroom_table

                def edit_selected_classroom():
                    selected = classroom_table.selected
                    if not selected:
                        ui.notify('No classroom selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        classroom_id = selected[0].get('id')
                    else:
                        try:
                            classroom_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    classroom = next((c for c in classrooms if c.id == classroom_id), None)
                    if not classroom:
                        ui.notify(f'Classroom ID {classroom_id} not found', type='error')
                        return

                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Classroom').classes('text-lg font-bold')
                        building_options = {b.id: b.name for b in buildings}
                        building_select = ui.select(
                            label='Building',
                            options=building_options,
                            value=classroom.building_id,
                            with_input=False
                        ).classes('w-full')
                        name_input = ui.input('Classroom Name', value=classroom.name).classes('w-full')
                        capacity_input = ui.number('Capacity', value=classroom.capacity, min=1, step=1).classes('w-full')
                        reserve_checkbox = ui.checkbox('Reserve classroom', value=classroom.is_reserve)

                        def save_edit():
                            if building_select.value is None:
                                ui.notify('Please select a building', type='error')
                                return
                            classroom.building_id = building_select.value
                            classroom.name = name_input.value.strip()
                            if not classroom.name:
                                ui.notify('Name cannot be empty', type='error')
                                return
                            classroom.capacity = int(capacity_input.value)
                            classroom.is_reserve = reserve_checkbox.value
                            refresh_classroom_table(classroom_search_input.value)
                            autosave()
                            edit_dialog.close()
                            ui.notify('Classroom updated', type='positive')

                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                with ui.row().classes('items-center'):
                    ui.label('Classrooms').classes('text-xl font-bold')
                    ui.space()
                    ui.button('Add Classroom', on_click=add_classroom_dialog).props('color=primary')
                    ui.button('Import', on_click=import_classrooms_dialog).props('color=secondary')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_classroom()).props('color=secondary')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_classrooms()).props('color=negative')

                classroom_search_input = ui.input('Search classrooms...', placeholder='Type to filter').classes('w-full')

                classroom_columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'building', 'label': 'Building', 'field': 'building', 'sortable': True},
                    {'name': 'name', 'label': 'Classroom Name', 'field': 'name', 'sortable': True},
                    {'name': 'capacity', 'label': 'Capacity', 'field': 'capacity', 'sortable': True},
                    {'name': 'is_reserve', 'label': 'Reserve', 'field': 'is_reserve', 'sortable': True},
                ]
                classroom_table = ui.table(
                    columns=classroom_columns,
                    rows=get_classroom_rows(),
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id'},
                ).classes('w-full')

                classroom_search_input.on_value_change(lambda e: refresh_classroom_table(e.value))

                def delete_selected_classrooms():
                    selected = classroom_table.selected
                    if not selected:
                        ui.notify('No classrooms selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    global classrooms
                    classrooms = [c for c in classrooms if c.id not in selected_ids]
                    refresh_classroom_table(classroom_search_input.value)
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} classroom(s)', type='positive')

            # -------------------- STUDENTS --------------------
            with ui.tab_panel(subtab_students):
                def get_all_student_rows():
                    rows = []
                    for s in students:
                        rows.append({
                            'id': s.id,
                            'full_name': s.full_name,
                            'faculty': s.faculty,
                            'department': s.department,
                            'exam_id': s.exam_id,
                            'language': s.language if s.language else '-',
                        })
                    return rows

                # ----- Button row (top) -----
                with ui.row().classes('items-center'):
                    ui.label('Students').classes('text-xl font-bold')
                    count_label = ui.label(f'({len(students)} total)').classes('text-lg text-gray-500')
                    ui.space()
                    ui.button('Add Student', on_click=add_student_dialog).props('color=primary')
                    ui.button('Import', on_click=import_students_dialog).props('color=secondary')
                    ui.button('Export', on_click=export_students_csv).props('color=accent')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_student()).props('color=secondary')
                    ui.button('Assign to Exam', on_click=lambda: assign_selected_to_exam()).props('color=accent')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_students()).props('color=negative')
                    ui.button('Delete All', on_click=lambda: confirm_action(
                        f"Are you sure you want to delete ALL {len(students)} students? This cannot be undone.",
                        delete_all_students
                    )).props('color=negative')
                    ui.button('Refresh', on_click=lambda: refresh_student_table(search_input.value)).props('color=accent')
                    ui.button('Auto-match to Exams', on_click=lambda: auto_match_students_to_exams()).props('color=accent')

                # ------------- Show total number of students -------------------
                count_label = ui.label(f'({len(students)} total)').classes('text-lg text-gray-500')

                # ----- Search input -----
                search_input = ui.input(
                    'Search students...',
                    placeholder='Type to filter (shows up to 100 results if empty)'
                ).classes('w-full')

                # ----- Table -----
                student_columns = [
                    {'name': 'id', 'label': 'Student ID', 'field': 'id', 'sortable': True},
                    {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name', 'sortable': True},
                    {'name': 'faculty', 'label': 'Faculty', 'field': 'faculty', 'sortable': True},
                    {'name': 'department', 'label': 'Department', 'field': 'department', 'sortable': True},
                    {'name': 'exam_id', 'label': 'Exam ID', 'field': 'exam_id', 'sortable': True},
                    {'name': 'language', 'label': 'Language', 'field': 'language', 'sortable': True},
                ]
                student_table = ui.table(
                    columns=student_columns,
                    rows=get_all_student_rows()[:100],
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 20, 'sortBy': 'id'},
                ).classes('w-full')

                # ----- Refresh function -----
                def refresh_student_table(search_text=''):
                    all_rows = get_all_student_rows()
                    if search_text:
                        search_text = search_text.lower()
                        filtered = [
                            row for row in all_rows
                            if search_text in str(row['id']).lower()
                            or search_text in row['full_name'].lower()
                            or search_text in row['faculty'].lower()
                            or search_text in row['department'].lower()
                            or search_text in row['language'].lower()
                        ]
                    else:
                        filtered = all_rows[:100]
                    student_table.rows = filtered
                    student_table.update()
                    count_label.text = f'({len(students)} total)'
                    count_label.update()

                search_input.on_value_change(lambda e: refresh_student_table(e.value))
                student_table_refresh = refresh_student_table

                # ----- Edit function -----
                def edit_selected_student():
                    selected = student_table.selected
                    if not selected:
                        ui.notify('No student selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        student_id = selected[0].get('id')
                    else:
                        try:
                            student_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    student = next((s for s in students if s.id == student_id), None)
                    if not student:
                        ui.notify(f'Student ID {student_id} not found', type='error')
                        return

                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Student').classes('text-lg font-bold')
                        full_name_input = ui.input('Full Name', value=student.full_name).classes('w-full')
                        faculty_input = ui.input('Faculty', value=student.faculty).classes('w-full')
                        department_input = ui.input('Department', value=student.department).classes('w-full')
                        exam_select_input = ui.select(
                            label='Exam',
                            options={e.id: e.name for e in exams},
                            value=student.exam_id,
                            with_input=False
                        ).classes('w-full')
                        language_options = ['English', 'German', 'Turkish', 'French', 'Spanish']
                        if student.language and student.language not in language_options:
                            language_options.append(student.language)
                        language_input = ui.select(
                            label='Language (optional)',
                            options=language_options,
                            value=student.language if student.language else None,
                            with_input=True,
                            clearable=True
                        ).classes('w-full')

                        def save_edit():
                            full_name = full_name_input.value.strip()
                            faculty = faculty_input.value.strip()
                            department = department_input.value.strip()
                            if not full_name or not faculty or not department:
                                ui.notify('All fields are required', type='error')
                                return
                            if exam_select_input.value is None:
                                ui.notify('Please select an exam', type='error')
                                return
                            student.full_name = full_name
                            student.faculty = faculty
                            student.department = department
                            student.exam_id = exam_select_input.value
                            student.language = language_input.value.strip() if language_input.value else None
                            refresh_student_table(search_input.value)
                            autosave()
                            edit_dialog.close()
                            ui.notify('Student updated', type='positive')

                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                # ----- Delete function -----
                def delete_selected_students():
                    selected = student_table.selected
                    if not selected:
                        ui.notify('No students selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    global students
                    students = [s for s in students if s.id not in selected_ids]
                    refresh_student_table(search_input.value)
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} student(s)', type='positive')

                # ------ Delete All Students Function -----------
                def delete_all_students():
                    global students
                    count = len(students)
                    students = []
                    refresh_student_table(search_input.value)
                    autosave()
                    ui.notify(f'Deleted all {count} student(s)', type='positive')

                #------- Auto Match Students to Exams --------------
                def auto_match_students_to_exams():
                    if not exams:
                        ui.notify('No exams defined', type='warning')
                        return
                    matched = 0
                    ambiguous = 0
                    unmatched = 0
                    for s in students:
                        norm = normalize_language(s.language)
                        if not norm:
                            unmatched += 1
                            continue
                        candidates = [e for e in exams if normalize_language(e.language) == norm]
                        if len(candidates) == 1:
                            s.exam_id = candidates[0].id
                            matched += 1
                        elif len(candidates) > 1:
                            ambiguous += 1
                        else:
                            unmatched += 1
                    refresh_student_table(search_input.value)
                    autosave()
                    msg = f'Matched {matched} student(s)'
                    if unmatched:
                        msg += f' | {unmatched} unmatched'
                    if ambiguous:
                        msg += f' | {ambiguous} ambiguous (multiple exams with same language)'
                    ui.notify(msg, type='info')

                # ----- Bulk Assign to Exam -----
                def assign_selected_to_exam():
                    if not exams:
                        ui.notify('No exams available. Please create an exam first.', type='warning')
                        return
                    selected = student_table.selected
                    selected_ids = extract_selected_ids(selected) if selected else []

                    with ui.dialog() as assign_dialog, ui.card():
                        if selected_ids:
                            ui.label(f'Reassign {len(selected_ids)} selected student(s)').classes('text-lg font-bold')
                        else:
                            ui.label('Reassign ALL students').classes('text-lg font-bold')
                            ui.label(f'No rows selected. This will apply to all {len(students)} students.').classes('text-sm text-red-600')

                        exam_select_assign = ui.select(
                            label='Target Exam',
                            options={e.id: e.name for e in exams},
                            with_input=False
                        ).classes('w-full')

                        def apply():
                            if exam_select_assign.value is None:
                                ui.notify('Please select an exam', type='error')
                                return
                            target_exam_id = exam_select_assign.value
                            count = 0
                            if selected_ids:
                                for s in students:
                                    if s.id in selected_ids:
                                        s.exam_id = target_exam_id
                                        count += 1
                            else:
                                for s in students:
                                    s.exam_id = target_exam_id
                                    count += 1
                            refresh_student_table(search_input.value)
                            autosave()
                            assign_dialog.close()
                            ui.notify(f'Assigned {count} student(s) to exam ID {target_exam_id}', type='positive')

                        with ui.row():
                            ui.button('Apply', on_click=apply).props('color=primary')
                            ui.button('Cancel', on_click=assign_dialog.close)
                    assign_dialog.open()

            # -------------------- PROCTORS --------------------
            with ui.tab_panel(subtab_proctors):
                def get_proctor_rows():
                    rows = []
                    for p in proctors:
                        bld_name = 'None'
                        if p.preferred_building_id is not None:
                            bld_name = next((b.name for b in buildings if b.id == p.preferred_building_id), 'Unknown')
                        rows.append({
                            'id': p.id,
                            'full_name': p.full_name,
                            'department': p.department,
                            'languages': ', '.join(p.languages),
                            'preferred_building': bld_name,
                            'can_be_supervisor': p.can_be_supervisor,
                            'is_reserve': p.is_reserve,
                        })
                    return rows

                def refresh_proctor_table(search_text=''):
                    all_rows = get_proctor_rows()
                    if search_text:
                        search_text = search_text.lower()
                        filtered = [
                            row for row in all_rows
                            if search_text in str(row['id']).lower()
                            or search_text in row['full_name'].lower()
                            or search_text in row['department'].lower()
                            or search_text in row['languages'].lower()
                            or search_text in row['preferred_building'].lower()
                        ]
                    else:
                        filtered = all_rows
                    proctor_table.rows = filtered
                    proctor_table.update()

                proctor_table_refresh = refresh_proctor_table

                # Edit function
                def edit_selected_proctor():
                    selected = proctor_table.selected
                    if not selected:
                        ui.notify('No proctor selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        proctor_id = selected[0].get('id')
                    else:
                        try:
                            proctor_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    proctor = next((p for p in proctors if p.id == proctor_id), None)
                    if not proctor:
                        ui.notify(f'Proctor ID {proctor_id} not found', type='error')
                        return

                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Proctor').classes('text-lg font-bold')
                        full_name_input = ui.input('Full Name', value=proctor.full_name).classes('w-full')
                        department_input = ui.input('Department', value=proctor.department).classes('w-full')
                        languages_input = ui.input('Languages (comma-separated)', value=', '.join(proctor.languages)).classes('w-full')
                        building_options = {b.id: b.name for b in buildings}
                        building_options[0] = 'None'
                        preferred_building_select = ui.select(
                            label='Preferred Building (optional)',
                            options=building_options,
                            value=proctor.preferred_building_id if proctor.preferred_building_id else 0,
                            with_input=False
                        ).classes('w-full')
                        can_be_supervisor_checkbox = ui.checkbox('Can be building supervisor', value=proctor.can_be_supervisor)
                        is_reserve_checkbox = ui.checkbox('Reserve proctor', value=proctor.is_reserve)

                        def save_edit():
                            lang_list = [l.strip() for l in languages_input.value.split(',') if l.strip()]
                            proctor.full_name = full_name_input.value.strip()
                            proctor.department = department_input.value.strip()
                            proctor.languages = lang_list
                            proctor.preferred_building_id = preferred_building_select.value if preferred_building_select.value != 0 else None
                            proctor.can_be_supervisor = can_be_supervisor_checkbox.value
                            proctor.is_reserve = is_reserve_checkbox.value
                            refresh_proctor_table(search_input.value)
                            autosave()
                            edit_dialog.close()
                            ui.notify('Proctor updated', type='positive')

                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                # Buttons row
                with ui.row().classes('items-center'):
                    ui.label('Proctors').classes('text-xl font-bold')
                    ui.space()
                    ui.button('Add Proctor', on_click=add_proctor_dialog).props('color=primary')
                    ui.button('Import', on_click=import_proctors_dialog).props('color=secondary')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_proctor()).props('color=secondary')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_proctors()).props('color=negative')

                # Search input
                search_input = ui.input('Search proctors...', placeholder='Type to filter').classes('w-full')

                # Table
                proctor_columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name', 'sortable': True},
                    {'name': 'department', 'label': 'Department', 'field': 'department', 'sortable': True},
                    {'name': 'languages', 'label': 'Languages', 'field': 'languages', 'sortable': True},
                    {'name': 'preferred_building', 'label': 'Preferred Building', 'field': 'preferred_building', 'sortable': True},
                    {'name': 'can_be_supervisor', 'label': 'Supervisor?', 'field': 'can_be_supervisor', 'sortable': True},
                    {'name': 'is_reserve', 'label': 'Reserve?', 'field': 'is_reserve', 'sortable': True},
                ]
                proctor_table = ui.table(
                    columns=proctor_columns,
                    rows=get_proctor_rows(),
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id'},
                ).classes('w-full')

                search_input.on_value_change(lambda e: refresh_proctor_table(e.value))

                def delete_selected_proctors():
                    selected = proctor_table.selected
                    if not selected:
                        ui.notify('No proctors selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    global proctors
                    proctors = [p for p in proctors if p.id not in selected_ids]
                    refresh_proctor_table(search_input.value)
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} proctor(s)', type='positive')

            # -------------------- BUILDING SUPERVISORS --------------------
            with ui.tab_panel(subtab_supervisors):
                def get_supervisor_rows():
                    rows = []
                    for s in building_supervisors:
                        bld_name = next((b.name for b in buildings if b.id == s.building_id), 'Unknown')
                        proctor_name = ''
                        if s.proctor_id is not None:
                            proctor_name = next((p.full_name for p in proctors if p.id == s.proctor_id), 'Unknown')
                        rows.append({
                            'id': s.id,
                            'full_name': s.full_name,
                            'building': bld_name,
                            'proctor': proctor_name if proctor_name else '-',
                        })
                    return rows

                def refresh_supervisor_table(search_text=''):
                    all_rows = get_supervisor_rows()
                    if search_text:
                        s = search_text.lower()
                        filtered = [
                            r for r in all_rows
                            if s in str(r['id']).lower()
                            or s in r['full_name'].lower()
                            or s in r['building'].lower()
                            or s in r['proctor'].lower()
                        ]
                    else:
                        filtered = all_rows
                    supervisor_table.rows = filtered
                    supervisor_table.update()

                supervisor_table_refresh = refresh_supervisor_table

                def edit_selected_supervisor():
                    selected = supervisor_table.selected
                    if not selected:
                        ui.notify('No supervisor selected', type='warning')
                        return
                    if isinstance(selected[0], dict):
                        supervisor_id = selected[0].get('id')
                    else:
                        try:
                            supervisor_id = int(selected[0])
                        except (ValueError, TypeError):
                            ui.notify('Invalid selection', type='error')
                            return
                    supervisor = next((s for s in building_supervisors if s.id == supervisor_id), None)
                    if not supervisor:
                        ui.notify(f'Supervisor ID {supervisor_id} not found', type='error')
                        return

                    with ui.dialog() as edit_dialog, ui.card():
                        ui.label('Edit Building Supervisor').classes('text-lg font-bold')
                        use_proctor_checkbox = ui.checkbox('Select from existing proctor', value=supervisor.proctor_id is not None)
                        proctor_select = ui.select(
                            label='Proctor',
                            options={p.id: p.full_name for p in proctors},
                            value=supervisor.proctor_id if supervisor.proctor_id else None,
                            with_input=False
                        ).classes('w-full')
                        full_name_input = ui.input('Full Name', value=supervisor.full_name).classes('w-full')
                        building_select = ui.select(
                            label='Building',
                            options={b.id: b.name for b in buildings},
                            value=supervisor.building_id,
                            with_input=False
                        ).classes('w-full')

                        proctor_select.visible = use_proctor_checkbox.value
                        full_name_input.visible = not use_proctor_checkbox.value

                        def toggle_proctor_select(e):
                            proctor_select.visible = e.value
                            full_name_input.visible = not e.value
                            if e.value and proctors:
                                proctor_id = proctor_select.value
                                if proctor_id:
                                    proctor = next((p for p in proctors if p.id == proctor_id), None)
                                    if proctor:
                                        full_name_input.value = proctor.full_name

                        use_proctor_checkbox.on_value_change(toggle_proctor_select)

                        def on_proctor_change(e):
                            if use_proctor_checkbox.value and e.value:
                                proctor = next((p for p in proctors if p.id == e.value), None)
                                if proctor:
                                    full_name_input.value = proctor.full_name

                        proctor_select.on_value_change(on_proctor_change)

                        def save_edit():
                            if not use_proctor_checkbox.value:
                                supervisor.full_name = full_name_input.value.strip()
                                supervisor.proctor_id = None
                            else:
                                proctor_id = proctor_select.value
                                if proctor_id is None:
                                    ui.notify('Please select a proctor', type='error')
                                    return
                                proctor = next((p for p in proctors if p.id == proctor_id), None)
                                if proctor:
                                    supervisor.full_name = proctor.full_name
                                    supervisor.proctor_id = proctor_id
                            if building_select.value is None:
                                ui.notify('Please select a building', type='error')
                                return
                            supervisor.building_id = building_select.value
                            refresh_supervisor_table(supervisor_search_input.value)
                            autosave()
                            edit_dialog.close()
                            ui.notify('Supervisor updated', type='positive')

                        with ui.row():
                            ui.button('Save', on_click=save_edit).props('color=primary')
                            ui.button('Cancel', on_click=edit_dialog.close)
                    edit_dialog.open()

                with ui.row().classes('items-center'):
                    ui.label('Building Supervisors').classes('text-xl font-bold')
                    ui.space()
                    ui.button('Add Supervisor', on_click=add_building_supervisor_dialog).props('color=primary')
                    ui.button('Import', on_click=import_supervisors_dialog).props('color=secondary')
                    ui.button('Edit Selected', on_click=lambda: edit_selected_supervisor()).props('color=secondary')
                    ui.button('Delete Selected', on_click=lambda: delete_selected_supervisors()).props('color=negative')

                supervisor_search_input = ui.input('Search supervisors...', placeholder='Type to filter').classes('w-full')

                supervisor_columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name', 'sortable': True},
                    {'name': 'building', 'label': 'Building', 'field': 'building', 'sortable': True},
                    {'name': 'proctor', 'label': 'Linked Proctor', 'field': 'proctor', 'sortable': True},
                ]
                supervisor_table = ui.table(
                    columns=supervisor_columns,
                    rows=get_supervisor_rows(),
                    row_key='id',
                    selection='multiple',
                    pagination={'rowsPerPage': 10, 'sortBy': 'id'},
                ).classes('w-full')

                supervisor_search_input.on_value_change(lambda e: refresh_supervisor_table(e.value))

                def delete_selected_supervisors():
                    selected = supervisor_table.selected
                    if not selected:
                        ui.notify('No supervisors selected', type='warning')
                        return
                    selected_ids = extract_selected_ids(selected)
                    global building_supervisors
                    building_supervisors = [s for s in building_supervisors if s.id not in selected_ids]
                    refresh_supervisor_table(supervisor_search_input.value)
                    autosave()
                    ui.notify(f'Deleted {len(selected_ids)} supervisor(s)', type='positive')

    # -------------------- ASSIGNMENT TAB --------------------
    with ui.tab_panel(tab_assign):
        with ui.column().classes('w-full p-4 gap-4'):
            ui.label('Assignment').classes('text-2xl font-bold')

            # ---------- Exam selection ----------
            exam_select = ui.select(
                label='Select Exam',
                options={},
                with_input=False
            ).classes('w-64')

            def refresh_exam_options():
                exam_select.options = {e.id: e.name for e in exams}
                exam_select.update()

            refresh_exam_options()
            exam_select_refresh = refresh_exam_options

            # ---------- Helpers ----------
            def get_building_name(classroom):
                building = next((b for b in buildings if b.id == classroom.building_id), None)
                return building.name if building else 'Unknown'

            def get_assignment_rows():
                rows = []
                selected_exam_id = exam_select.value
                for a in assignments:
                    if selected_exam_id is not None and a.exam_id != selected_exam_id:
                        continue
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building_name = get_building_name(classroom)
                    proctor_names = []
                    for pid in a.proctor_ids:
                        p = next((p for p in proctors if p.id == pid), None)
                        if p:
                            proctor_names.append(p.full_name)
                    supervisor_name = ''
                    if a.building_supervisor_id:
                        sup = next((s for s in building_supervisors if s.id == a.building_supervisor_id), None)
                        if sup:
                            supervisor_name = sup.full_name
                        else:
                            pro = next((p for p in proctors if p.id == a.building_supervisor_id), None)
                            if pro:
                                supervisor_name = pro.full_name + " (proctor)"
                    rows.append({
                        'id': a.id,
                        'exam': next((e.name for e in exams if e.id == a.exam_id), '?'),
                        'building': building_name,
                        'classroom': classroom.name,
                        'proctors': ', '.join(proctor_names),
                        'students': len(a.student_ids),
                        'supervisor': supervisor_name,
                        'is_reserve': classroom.is_reserve,
                    })
                return rows

            def refresh_assignment_table():
                assignment_table.rows = get_assignment_rows()
                assignment_table.update()

            assignment_table_refresh = refresh_assignment_table

            exam_select.on_value_change(lambda e: refresh_assignment_table())

            def refresh_unused_proctors():
                if not exam_select.value:
                    unused_proctor_table.rows = []
                    unused_proctor_table.update()
                    return
                used_ids = set()
                for a in assignments:
                    if a.exam_id == exam_select.value:
                        used_ids.update(a.proctor_ids)
                unused = [p for p in proctors if p.id not in used_ids]
                unused_proctor_table.rows = [
                    {'id': p.id, 'full_name': p.full_name,
                     'department': p.department, 'languages': ', '.join(p.languages)}
                    for p in unused
                ]
                unused_proctor_table.update()

            # ---------- Edit selected assignment ----------
            def edit_selected_assignment():
                if not assignments:
                    ui.notify('No assignments to edit', type='warning')
                    return
                selected = assignment_table.selected
                if not selected:
                    ui.notify('Please select an assignment to edit', type='warning')
                    return
                if isinstance(selected[0], dict):
                    assignment_id = selected[0].get('id')
                else:
                    try:
                        assignment_id = int(selected[0])
                    except (ValueError, TypeError):
                        ui.notify('Invalid selection', type='error')
                        return
                assignment = next((a for a in assignments if a.id == assignment_id), None)
                if not assignment:
                    ui.notify(f'Assignment ID {assignment_id} not found', type='error')
                    return

                classroom = next((c for c in classrooms if c.id == assignment.classroom_id), None)
                if not classroom:
                    ui.notify('Classroom not found for this assignment', type='error')
                    return

                with ui.dialog() as edit_dialog, ui.card():
                    ui.label(f'Edit Assignment - {classroom.name}').classes('text-lg font-bold')

                    # Proctor multi-select
                    proctor_options = {p.id: p.full_name for p in proctors}
                    proctor_select = ui.select(
                        label='Proctors',
                        options=proctor_options,
                        value=assignment.proctor_ids,
                        multiple=True,
                        with_input=False
                    ).classes('w-full')

                    # Supervisor dropdown
                    supervisor_options = {0: 'None'}
                    for s in building_supervisors:
                        if s.building_id == classroom.building_id:
                            supervisor_options[s.id] = s.full_name
                    current_sup = assignment.building_supervisor_id
                    if current_sup and current_sup not in supervisor_options:
                        pro = next((p for p in proctors if p.id == current_sup), None)
                        if pro:
                            supervisor_options[current_sup] = pro.full_name + " (proctor)"
                        else:
                            supervisor_options[current_sup] = f"ID {current_sup}"
                    supervisor_select = ui.select(
                        label='Building Supervisor',
                        options=supervisor_options,
                        value=current_sup if current_sup else 0,
                        with_input=False
                    ).classes('w-full')

                    def save_edit():
                        assignment.proctor_ids = proctor_select.value or []
                        sup_id = supervisor_select.value
                        assignment.building_supervisor_id = None if sup_id == 0 else sup_id
                        refresh_assignment_table()
                        refresh_unused_proctors()
                        autosave()
                        edit_dialog.close()
                        ui.notify('Assignment updated', type='positive')

                    with ui.row():
                        ui.button('Save', on_click=save_edit).props('color=primary')
                        ui.button('Cancel', on_click=edit_dialog.close)
                edit_dialog.open()

            # ---------- Buttons ----------
            with ui.row().classes('gap-2'):
                ui.button('Auto-Assign', on_click=lambda: confirm_action(
                    "Are you sure you want to auto-assign? This will replace existing assignments for this exam.",
                    lambda: run_full_assignment(exam_select.value)
                )).props('color=primary')
                ui.button('Edit Selected', on_click=edit_selected_assignment).props('color=secondary')
                ui.button('Show Unused Proctors', on_click=refresh_unused_proctors).props('color=accent')
                ui.button('Clear Assignments', on_click=lambda: confirm_action(
                    "Are you sure you want to clear all assignments for this exam?",
                    lambda: clear_assignments(exam_select.value)
                )).props('color=negative')

            # ---------- Assignment table ----------
            assignment_columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                {'name': 'exam', 'label': 'Exam', 'field': 'exam', 'sortable': True},
                {'name': 'building', 'label': 'Building', 'field': 'building', 'sortable': True},
                {'name': 'classroom', 'label': 'Classroom', 'field': 'classroom', 'sortable': True},
                {'name': 'proctors', 'label': 'Proctors', 'field': 'proctors', 'sortable': False},
                {'name': 'students', 'label': 'Students', 'field': 'students', 'sortable': True},
                {'name': 'supervisor', 'label': 'Building Supervisor', 'field': 'supervisor', 'sortable': False},
                {'name': 'is_reserve', 'label': 'Reserve', 'field': 'is_reserve', 'sortable': True},
            ]
            assignment_table = ui.table(
                columns=assignment_columns,
                rows=[],
                row_key='id',
                selection='multiple',
                pagination={'rowsPerPage': 10, 'sortBy': 'id'},
            ).classes('w-full')

            # ---------- Unused proctors table ----------
            ui.label('Unused Proctors').classes('text-xl font-bold mt-4')
            unused_proctor_table = ui.table(
                columns=[
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                    {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name', 'sortable': True},
                    {'name': 'department', 'label': 'Department', 'field': 'department', 'sortable': True},
                    {'name': 'languages', 'label': 'Languages', 'field': 'languages', 'sortable': True},
                ],
                rows=[],
                row_key='id',
                pagination={'rowsPerPage': 15},
            ).classes('w-full')

            # ---------- Auto-assign ----------
            def run_full_assignment(exam_id):
                global assignments, next_assignment_id
                exam = next((e for e in exams if e.id == exam_id), None)
                if not exam:
                    ui.notify('Please select a valid exam', type='error')
                    return

                # Find all exams in the same session group (or just this one)
                if exam.session_group:
                    session_exams = [e for e in exams if e.session_group == exam.session_group]
                else:
                    session_exams = [exam]

                new_assignments, msg, total = assignment_engine.generate_session_assignments(
                    session_exams, students, classrooms, proctors, building_supervisors
                )
                if msg != "OK" and not msg.startswith("OK"):
                    ui.notify(msg, type='error')
                    return
                if msg.startswith("OK") and "warning" in msg:
                    ui.notify(msg, type='warning')

                # Replace assignments for ALL exams in the session
                session_ids = {e.id for e in session_exams}
                assignments = [a for a in assignments if a.exam_id not in session_ids]

                for a in new_assignments:
                    a.id = next_assignment_id
                    next_assignment_id += 1
                    assignments.append(a)

                refresh_assignment_table()
                refresh_unused_proctors()
                if report_preview_clear:
                    report_preview_clear()
                autosave()

                names = ', '.join(e.name for e in session_exams)
                ui.notify(f'Assignment completed for session [{names}]: {total} students', type='positive')
            # ---------- Clear ----------
            def clear_assignments(exam_id):
                global assignments
                assignments = [a for a in assignments if a.exam_id != exam_id]
                refresh_assignment_table()
                refresh_unused_proctors()
                if report_preview_clear:
                    report_preview_clear()
                autosave()
                ui.notify('Assignments cleared', type='info')

            # Expose for exam "Save & Regenerate"
            run_assignment_global = run_full_assignment

        # -------------------- REPORTS TAB --------------------
    with ui.tab_panel(tab_reports):
        with ui.column().classes('w-full p-4 gap-4'):
            ui.label('Reports').classes('text-2xl font-bold')

            report_exam_select = ui.select(
                label='Select Exam',
                options={},
                with_input=False
            ).classes('w-64')

            def refresh_report_exam_options():
                report_exam_select.options = {e.id: e.name for e in exams}
                report_exam_select.update()

            refresh_report_exam_options()
            report_exam_select_refresh = refresh_report_exam_options

            # Buttons for preview and export
            with ui.row().classes('gap-2'):
                ui.button('Show Proctor List', on_click=lambda: show_proctor_list(report_exam_select.value)).props('color=primary')
                ui.button('Show Student List', on_click=lambda: show_student_list(report_exam_select.value)).props('color=primary')
            with ui.row().classes('gap-2'):
                ui.button('Export Proctor CSV', on_click=lambda: export_proctor_list(report_exam_select.value)).props('color=secondary')
                ui.button('Export Proctor XLSX', on_click=lambda: export_proctor_list_xlsx(report_exam_select.value)).props('color=secondary')
                ui.button('Export Student CSV', on_click=lambda: export_student_list(report_exam_select.value)).props('color=secondary')
                ui.button('Export Student XLSX', on_click=lambda: export_student_list_xlsx(report_exam_select.value)).props('color=secondary')

            # Preview tables
            proctor_preview_table = ui.table(columns=[], rows=[], row_key='id').classes('w-full')
            student_preview_table = ui.table(columns=[], rows=[], row_key='id').classes('w-full')
            proctor_preview_table.visible = False
            student_preview_table.visible = False

            def clear_report_previews():
                proctor_preview_table.rows = []
                proctor_preview_table.columns = []
                proctor_preview_table.visible = False
                proctor_preview_table.update()
                student_preview_table.rows = []
                student_preview_table.columns = []
                student_preview_table.visible = False
                student_preview_table.update()

            report_preview_clear = clear_report_previews

            # Helper: get assignments for exam
            def get_assignments_for_exam(exam_id):
                return [a for a in assignments if a.exam_id == exam_id]

            # Function to show proctor list preview
            def show_proctor_list(exam_id):
                exam_assignments = get_assignments_for_exam(exam_id)
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                building_order = []
                building_classrooms = {}
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    if building_name not in building_classrooms:
                        building_classrooms[building_name] = []
                        building_order.append(building_name)
                    proctor_names = []
                    for pid in a.proctor_ids:
                        p = next((p for p in proctors if p.id == pid), None)
                        if p:
                            proctor_names.append(p.full_name)
                    supervisor_name = ''
                    if a.building_supervisor_id:
                        sup = next((s for s in building_supervisors if s.id == a.building_supervisor_id), None)
                        if sup:
                            supervisor_name = sup.full_name
                        else:
                            pro = next((p for p in proctors if p.id == a.building_supervisor_id), None)
                            if pro:
                                supervisor_name = pro.full_name + " (proctor)"
                    building_classrooms[building_name].append({
                        'classroom': classroom.name,
                        'proctors': ', '.join(proctor_names),
                        'supervisor': supervisor_name,
                        'students': len(a.student_ids),
                        'is_reserve': classroom.is_reserve,
                    })

                rows = []
                row_id = 0
                for building_name in building_order:
                    for item in building_classrooms[building_name]:
                        row_id += 1
                        rows.append({
                            'id': row_id,
                            'exam': next((e.name for e in exams if e.id == a.exam_id), '?'),
                            'building': building_name,
                            'classroom': item['classroom'],
                            'proctors': item['proctors'],
                            'supervisor': item['supervisor'],
                            'students': item['students'],
                            'is_reserve': item['is_reserve'],
                        })

                proctor_columns = [
                    {'name': 'id', 'label': '#', 'field': 'id'},
                    {'name': 'exam', 'label': 'Exam', 'field': 'exam'},
                    {'name': 'building', 'label': 'Building', 'field': 'building'},
                    {'name': 'classroom', 'label': 'Classroom', 'field': 'classroom'},
                    {'name': 'proctors', 'label': 'Proctors', 'field': 'proctors'},
                    {'name': 'supervisor', 'label': 'Building Supervisor', 'field': 'supervisor'},
                    {'name': 'students', 'label': 'Students', 'field': 'students'},
                    {'name': 'is_reserve', 'label': 'Reserve', 'field': 'is_reserve'},
                ]
                proctor_preview_table.columns = proctor_columns
                proctor_preview_table.rows = rows
                proctor_preview_table.visible = True
                proctor_preview_table.update()

            # Function to show student list preview
            def show_student_list(exam_id):
                exam_assignments = get_assignments_for_exam(exam_id)
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                rows = []
                row_id = 0
                for a in exam_assignments:
                                    rows = []
                seat_counter = 0
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    for sid in a.student_ids:
                        student = next((s for s in students if s.id == sid), None)
                        if not student:
                            continue
                        seat_counter += 1
                        rows.append({
                            'id': seat_counter,
                            'seat': seat_counter,
                            'exam': next((e.name for e in exams if e.id == a.exam_id), '?'),
                            'student_id': student.id,
                            'full_name': student.full_name,
                            'faculty': student.faculty,
                            'department': student.department,
                            'language': student.language or '-',
                            'building': building_name,
                            'classroom': classroom.name,
                        })

                student_columns = [
                    {'name': 'seat', 'label': 'Seat No', 'field': 'seat'},
                    {'name': 'exam', 'label': 'Exam', 'field': 'exam'},
                    {'name': 'student_id', 'label': 'Student ID', 'field': 'student_id'},
                    {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
                    {'name': 'faculty', 'label': 'Faculty', 'field': 'faculty'},
                    {'name': 'department', 'label': 'Department', 'field': 'department'},
                    {'name': 'language', 'label': 'Language', 'field': 'language'},
                    {'name': 'building', 'label': 'Building', 'field': 'building'},
                    {'name': 'classroom', 'label': 'Classroom', 'field': 'classroom'},
                ]
                student_preview_table.columns = student_columns
                student_preview_table.rows = rows
                student_preview_table.visible = True
                student_preview_table.update()

            # Export functions
            def export_proctor_list(exam_id):
                exam_assignments = [a for a in assignments if a.exam_id == exam_id]
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                rows = []
                no_counter = 0
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    exam_name = next((e.name for e in exams if e.id == a.exam_id), '?')
                    proctor_names = []
                    for pid in a.proctor_ids:
                        p = next((p for p in proctors if p.id == pid), None)
                        if p:
                            proctor_names.append(p.full_name)
                    supervisor_name = ''
                    if a.building_supervisor_id:
                        sup = next((s for s in building_supervisors if s.id == a.building_supervisor_id), None)
                        if sup:
                            supervisor_name = sup.full_name
                        else:
                            pro = next((p for p in proctors if p.id == a.building_supervisor_id), None)
                            if pro:
                                supervisor_name = pro.full_name + " (proctor)"
                    no_counter += 1
                    rows.append([
                        no_counter,
                        exam_name,
                        building_name,
                        classroom.name,
                        ', '.join(proctor_names),
                        supervisor_name,
                        len(a.student_ids),
                        'Yes' if classroom.is_reserve else 'No',
                    ])

                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['No', 'Exam', 'Building', 'Classroom', 'Proctors',
                                 'Building Supervisor', 'Students', 'Reserve'])
                for row in rows:
                    writer.writerow(row)
                csv_content = output.getvalue()

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"proctor_list_exam_{exam_id}.csv",
                    title="Save Proctor List As CSV"
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                            f.write(csv_content)
                        ui.notify(f'Proctor list saved to {file_path}', type='positive')
                    except Exception as e:
                        ui.notify(f'Error saving file: {e}', type='error')
                root.destroy()

            def export_proctor_list_xlsx(exam_id):
                exam_assignments = [a for a in assignments if a.exam_id == exam_id]
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                rows = []
                no_counter = 0
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    exam_name = next((e.name for e in exams if e.id == a.exam_id), '?')
                    proctor_names = []
                    for pid in a.proctor_ids:
                        p = next((p for p in proctors if p.id == pid), None)
                        if p:
                            proctor_names.append(p.full_name)
                    supervisor_name = ''
                    if a.building_supervisor_id:
                        sup = next((s for s in building_supervisors if s.id == a.building_supervisor_id), None)
                        if sup:
                            supervisor_name = sup.full_name
                        else:
                            pro = next((p for p in proctors if p.id == a.building_supervisor_id), None)
                            if pro:
                                supervisor_name = pro.full_name + " (proctor)"
                    no_counter += 1
                    rows.append([
                        no_counter,
                        exam_name,
                        building_name,
                        classroom.name,
                        ', '.join(proctor_names),
                        supervisor_name,
                        len(a.student_ids),
                        'Yes' if classroom.is_reserve else 'No',
                    ])

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=f"proctor_list_exam_{exam_id}.xlsx",
                    title="Save Proctor List As XLSX"
                )
                if file_path:
                    try:
                        save_xlsx_template(
                            file_path,
                            ['No', 'Exam', 'Building', 'Classroom', 'Proctors',
                             'Building Supervisor', 'Students', 'Reserve'],
                            rows,
                            sheet_name='Proctors'
                        )
                        ui.notify(f'Proctor list saved to {file_path}', type='positive')
                    except Exception as e:
                        ui.notify(f'Error saving file: {e}', type='error')
                root.destroy()

            def export_student_list(exam_id):
                exam_assignments = [a for a in assignments if a.exam_id == exam_id]
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                rows = []
                no_counter = 0
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    exam_name = next((e.name for e in exams if e.id == a.exam_id), '?')
                    seat_num = 0
                    for sid in a.student_ids:
                        student = next((s for s in students if s.id == sid), None)
                        if not student:
                            continue
                        no_counter += 1
                        seat_num += 1
                        rows.append([
                            no_counter,
                            exam_name,
                            student.id,
                            student.full_name,
                            student.faculty,
                            student.department,
                            student.language or '',
                            building_name,
                            classroom.name,
                            seat_num,
                        ])

                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['No', 'Exam', 'Student ID', 'Full Name', 'Faculty',
                                 'Department', 'Language', 'Exam Building', 'Exam Classroom', 'Seat Number'])
                for row in rows:
                    writer.writerow(row)
                csv_content = output.getvalue()

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"student_list_exam_{exam_id}.csv",
                    title="Save Student List As CSV"
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                            f.write(csv_content)
                        ui.notify(f'Student list saved to {file_path}', type='positive')
                    except Exception as e:
                        ui.notify(f'Error saving file: {e}', type='error')
                root.destroy()

            def export_student_list_xlsx(exam_id):
                exam_assignments = [a for a in assignments if a.exam_id == exam_id]
                if not exam_assignments:
                    ui.notify('No assignments for this exam yet', type='warning')
                    return

                rows = []
                no_counter = 0
                for a in exam_assignments:
                    classroom = next((c for c in classrooms if c.id == a.classroom_id), None)
                    if not classroom:
                        continue
                    building = next((b for b in buildings if b.id == classroom.building_id), None)
                    building_name = building.name if building else 'Unknown'
                    exam_name = next((e.name for e in exams if e.id == a.exam_id), '?')
                    seat_num = 0
                    for sid in a.student_ids:
                        student = next((s for s in students if s.id == sid), None)
                        if not student:
                            continue
                        no_counter += 1
                        seat_num += 1
                        rows.append([
                            no_counter,
                            exam_name,
                            student.id,
                            student.full_name,
                            student.faculty,
                            student.department,
                            student.language or '',
                            building_name,
                            classroom.name,
                            seat_num,
                        ])

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=f"student_list_exam_{exam_id}.xlsx",
                    title="Save Student List As XLSX"
                )
                if file_path:
                    try:
                        save_xlsx_template(
                            file_path,
                            ['No', 'Exam', 'Student ID', 'Full Name', 'Faculty',
                             'Department', 'Language', 'Exam Building', 'Exam Classroom', 'Seat Number'],
                            rows,
                            sheet_name='Students'
                        )
                        ui.notify(f'Student list saved to {file_path}', type='positive')
                    except Exception as e:
                        ui.notify(f'Error saving file: {e}', type='error')
                root.destroy()
    # -------------------- SETTINGS TAB --------------------
    with ui.tab_panel(tab_settings):
        with ui.column().classes('w-full p-4 gap-4'):
            ui.label('Settings').classes('text-2xl font-bold')

            # --- Project management ---
            ui.label('Project Management').classes('text-lg font-semibold')
            with ui.row().classes('gap-2'):
                ui.button('Save Project', on_click=save_project_dialog).props('color=primary')
                ui.button('Load Project', on_click=load_project_dialog).props('color=secondary')
                ui.button('Backup Now', on_click=lambda: backup_now()).props('color=accent')
                ui.button('Reset All Data', on_click=lambda: confirm_action(
                    "Are you sure you want to reset ALL data? This will clear students, buildings, classrooms, proctors, supervisors, exams, and assignments. You cannot undo this.",
                    reset_all_data
                )).props('color=negative')

            ui.separator()

            # --- Defaults for new exams ---
            ui.label('Defaults for New Exams').classes('text-lg font-semibold')
            default_proctors_input = ui.number(
                'Default proctors per classroom',
                value=default_proctors_per_classroom,
                min=1, max=5, step=1
            ).classes('w-64')

            def apply_defaults():
                global default_proctors_per_classroom
                default_proctors_per_classroom = int(default_proctors_input.value)
                autosave()
                ui.notify(f'Default proctors per classroom set to {default_proctors_per_classroom}', type='positive')

            ui.button('Apply Defaults', on_click=apply_defaults).props('color=primary')

            ui.separator()

            # --- Info ---
            ui.label(f'Autosave file: {AUTOSAVE_PATH}').classes('text-sm text-gray-500')
            ui.label(f'Backup folder: {BACKUP_DIR}').classes('text-sm text-gray-500')

    # -------------------- ABOUT TAB --------------------
    with ui.tab_panel(tab_about):
        with ui.column().classes('w-full p-8 gap-3 items-center'):
            ui.label('High Stakes Exam Organizer').classes('text-4xl font-bold text-primary')
            ui.label('Version 1.0.0').classes('text-lg text-gray-600')

            ui.separator().classes('w-2/3 my-4')

            ui.label('A desktop tool for organizing mid-size high-stakes exams.').classes('text-base text-center')

            ui.separator().classes('w-2/3 my-4')

            ui.label('Key Features').classes('text-xl font-semibold')
            with ui.column().classes('gap-1'):
                ui.label('• Manage buildings, classrooms, proctors, building supervisors, students, and exams').classes('text-base')
                ui.label('• Import and export CSV and Excel (.xlsx) files').classes('text-base')
                ui.label('• Automatic assignment engine with fair proctor distribution').classes('text-base')
                ui.label('• Language-aware assignment for parallel exams (e.g., English and German)').classes('text-base')
                ui.label('• Session groups for exams running in parallel').classes('text-base')
                ui.label('• Reserve classroom and reserve proctor support').classes('text-base')
                ui.label('• Manual adjustments for proctors, supervisors, and assignments').classes('text-base')
                ui.label('• Seat-numbered student lists and printable reports').classes('text-base')
                ui.label('• Autosave and manual backup/restore').classes('text-base')

            ui.separator().classes('w-2/3 my-4')

            ui.label('Workflow').classes('text-xl font-semibold')
            with ui.column().classes('gap-1'):
                ui.label('1. Create one or more exams (use the same Session Group for parallel exams).').classes('text-base')
                ui.label('2. Import or add buildings, classrooms, proctors, and students.').classes('text-base')
                ui.label('3. Use "Auto-match to Exams" to sort students by language.').classes('text-base')
                ui.label('4. Run Auto-Assign from the Assignment tab.').classes('text-base')
                ui.label('5. Review and adjust assignments manually if needed.').classes('text-base')
                ui.label('6. Export proctor and student lists from the Reports tab.').classes('text-base')

            ui.separator().classes('w-2/3 my-4')

            ui.label('This application has been developed by Kutay Uzun with assistance from Deepseek-v4.').classes('text-base text-center italic')
            ui.label('Built with Python, NiceGUI, and openpyxl.').classes('text-sm text-gray-500')

# ------------------------------------------------------------
# Run the app
# ------------------------------------------------------------
ui.run(native=True, title='Exam Organizer', window_size=(1200, 800), reload=False)