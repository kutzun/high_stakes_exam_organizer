# High Stakes Exam Organizer

A desktop application for organizing high-stakes university and school exams.
Developed by **Kutay Uzun** with assistance from **Deepseek-v4**.

---

## 1. Overview

The app helps you:
- Register buildings, classrooms, proctors, building supervisors, students, and exams.
- Import large datasets from CSV or Excel (.xlsx).
- Automatically assign students to classrooms and proctors to classrooms.
- Handle multiple languages (e.g., English and German) in the same session.
- Export proctor and student lists for exam day.

---

## 2. Quick Start

1. Launch the app:
2. The app opens in a native window.
3. If you had a previous session, the autosave is loaded automatically.
4. Follow the tabs in order: **Exams → Buildings → Classrooms → Students → Proctors → Building Supervisors → Assignment → Reports**.

---

## 3. Data Entry

Each tab supports **Add**, **Edit Selected**, **Delete Selected**, **Import**, **Export** (students only), and **Search**.

### 3.1 Exams
- Each exam has a name, date, time, optional language, default proctors per classroom, distribution strategy, optional session group, and a "Split students by language" option.
- **Session group**: give parallel exams the same label (e.g., "Spring 2025 Morning") if they run in the same time slot.
- **Split students by language**: check this if a single exam has students from multiple languages and you want each language in its own rooms.

### 3.2 Buildings
- Just ID and Name. Import from CSV or XLSX.

### 3.3 Classrooms
- Belongs to a building, has a name, a capacity, and can be marked "reserve".
- Reserve classrooms are only used if regular capacity is insufficient, or to host standby proctors.

### 3.4 Students
- Fields: Student ID, Full Name, Faculty, Department, Exam ID, Language.
- Bulk actions: **Assign to Exam** (single or all) and **Auto-match to Exams** (based on language).
- **Delete All** removes every student (with confirmation).

### 3.5 Proctors
- Fields: Full Name, Department, Languages, Preferred Building, Can be Supervisor, Reserve.
- **Reserve** proctors are assigned only to reserve classrooms.

### 3.6 Building Supervisors
- Optional link to a proctor.
- If a building has no dedicated supervisor, the engine promotes a proctor from that building.

---

## 4. Importing Data

### CSV
- Separator can be comma or tab.
- Encoding: UTF-8 (preferred), Windows-1254, or Latin-1 (auto-detected).
- Headers can be English or Turkish (e.g., "Öğrenci No" and "Student ID" both work).

### XLSX
- The first row must contain headers.
- The active sheet is used.

### Templates
Every import dialog has **Download CSV Template** and **Download XLSX Template** buttons.

---

## 5. Assignment Workflow

1. Create at least one exam.
2. Import or enter buildings, classrooms, students, proctors.
3. Go to the **Assignment** tab.
4. Select the exam.
5. Click **Auto-Assign**. Confirm.

The engine:
- Distributes students evenly across classrooms.
- Respects capacity and language (if split by language is enabled).
- Assigns building supervisors (dedicated or promoted proctors).
- Assigns proctors to classrooms, preferring:
1. Matching language,
2. Preferred building,
3. Fair distribution (every classroom gets at least one before anyone gets a second).
- Uses reserve classrooms only if regular capacity is insufficient.
- Assigns reserve proctors to reserve classrooms.

### Manual adjustments
- Select a row in the Assignment table → **Edit Selected** → change proctors or supervisor.
- **Show Unused Proctors** lists those not assigned; useful for planning.

---

## 6. Reports

In the Reports tab:
- Select an exam.
- **Show Proctor List** and **Show Student List** display previews.
- Export as **CSV** or **XLSX**.

### Proctor report columns
No, Exam, Building, Classroom, Proctors, Building Supervisor, Students, Reserve.

### Student report columns
No, Exam, Student ID, Full Name, Faculty, Department, Language, Exam Building, Exam Classroom, Seat Number.

**Seat numbers restart at 1 for each classroom**, matching the room's capacity.

---

## 7. Saving and Restoring

- The app **autosaves** to `autosave.json` in the project folder after every important change.
- **Save Project** / **Load Project** in the Settings tab lets you save or open a named JSON file.
- **Backup Now** creates a timestamped copy in the `backups` folder.
- **Reset All Data** clears everything in memory (confirmation required).

Keep backups before each exam.

---

## 8. Tips

- Save your work before large operations (imports, auto-assign).
- Use **Search** in each tab to find records quickly. The Students tab shows 100 rows by default; use search to see more.
- If you change an exam's proctor count, language, strategy, or session group after assigning, click **Save & Regenerate** (in the edit dialog) or re-run Auto-Assign.
- Reserve classrooms are for overflow and standby proctors. Mark them in the Classrooms tab.

---

## 9. Troubleshooting

**Import fails with encoding error**
- Save your file as UTF-8 or CSV UTF-8 in Excel.

**Students not matched to exams**
- Check the language values in Students and in Exams. The app recognizes Turkish and English names (İngilizce / English, Almanca / German, etc.).

**Proctors are doubled up**
- Check the exam's proctor count in the Exams tab. The engine uses exactly that value.

**Not enough capacity**
- The engine reports how many students are left unassigned. Add classrooms or mark some as regular (not reserve).

**App window feels slow with thousands of students**
- This is expected with 2000+ rows. Use search to work with smaller subsets.

---

## 10. Credits

Developed by **Kutay Uzun** with assistance from **Deepseek-v4**.
Built with Python, NiceGUI, and openpyxl.