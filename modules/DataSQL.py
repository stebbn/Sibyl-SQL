import sqlite3
import re
import os
import sys
import math

import time

from typing import Literal

def prettyPrint(msg):
    print("[DATA]:", msg)

def get_save_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
  
    data_dir = os.path.join(base_path, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    return os.path.join(data_dir, filename)

dataFormat = {
    "Student" : ["id_number", "first_name", "last_name", "program_code", "year_level", "gender"],
    "College" : ["college_code","college_name"],
    "Program" : ["program_code","program_name","college_code"]
}

# ------------------------- main data funcs --------------------------------- #

class DatabaseManager:
    def __init__(self):
        self.db_path  = get_save_path("university.db")
        self.Settings = {
            "MaxPageSize" : 50,
        }
        self.infos    = {
            "students": {
                "Pages" : 0,
                "Total" : 0
            },

            "colleges": {
                "Pages" : 0,
                "Total" : 0
            },

            "programs": {
                "Pages" : 0,
                "Total" : 0
            }
        }

        self._initialize_database()
        self._load_pages()
   
    def _load_pages(self):
        self.infos["students"]["Pages"] = self._calculate_pages("students")
        self.infos["colleges"]["Pages"] = self._calculate_pages("colleges")
        self.infos["programs"]["Pages"] = self._calculate_pages("programs")

    def _get_pages(self, table):
        tables = self.infos.get(table)
        value = tables.get("Pages")

        if value: return self.infos[table]["Pages"]
        prettyPrint(f"get pages error: {table}, {tables} {value}")
        return None
    
    def _get_table_val(self, table, val):
        table = self.infos.get(table)
        value = table.get(val)
        if table and value: return value
        prettyPrint(f"get error: {table}, {val}")
        return None

    def _calculate_pages(self, table, search="", search_field=None):
        try:
            with self._get_connection() as conn:
                if search and search_field:
                    query = f"SELECT COUNT(*) FROM {table} WHERE {search_field} LIKE ?"
                    search_term = f"{search}%"
                    cursor = conn.execute(query, (search_term,))
                else:
                    query = f"SELECT COUNT(*) FROM {table}"
                    cursor = conn.execute(query)
               
                total_count = int(cursor.fetchone()[0])
              
                if not search:
                    self.infos[table]["Total"] = total_count
             
                calculated_pages = math.ceil(total_count / self.Settings["MaxPageSize"])
                return max(1, calculated_pages)
                
        except Exception as e:
            prettyPrint(f"Error calculating pages for {table}: {e}")
            return 1

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row 
        return conn

    def _initialize_database(self):
        query = """
        CREATE TABLE IF NOT EXISTS colleges (
            college_code TEXT PRIMARY KEY,
            college_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS programs (
            program_code TEXT PRIMARY KEY,
            program_name TEXT NOT NULL,
            college_code TEXT NOT NULL,
            FOREIGN KEY (college_code) REFERENCES colleges (college_code) ON UPDATE CASCADE ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS students (
            id_number TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            year_level INTEGER,
            gender TEXT,
            program_code TEXT,
            FOREIGN KEY (program_code) REFERENCES programs (program_code) ON UPDATE CASCADE ON DELETE SET NULL
        );
        """
        try:
            with self._get_connection() as conn:
                conn.executescript(query)
        except Exception as e:
            prettyPrint(f"Error init database: {e}")

    def query_students(self, search="", search_field="id_number", page=1, sort="id_number", asc=True):
        start_time = time.perf_counter()

        try:
            with self._get_connection() as conn:
                max_page = self.Settings["MaxPageSize"]
                offset   = (page - 1) * max_page
                sort_dir = "ASC" if asc else "DESC"

                search_term = f"{search}%"
              
                search_max_page = self._calculate_pages("students", search, search_field)
                self.infos["students"]["Pages"] = search_max_page

                cursor = conn.execute(f"""
                                        SELECT id_number, first_name, last_name, year_level, gender, program_code 
                                        FROM students
                                        WHERE {search_field} LIKE ?
                                        ORDER BY {sort} {sort_dir}
                                        LIMIT ? OFFSET ?
                                        """,
                                        (search_term, max_page, offset) 
                                     )

                prettyPrint(f"current student queue time: {time.perf_counter() - start_time}")
                return [dict(row) for row in cursor.fetchall()], search_max_page
                
        except Exception as e:
            prettyPrint(f"Error fetching students: {e}")
            return [], 1

    def query_college(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT college_code, college_name FROM colleges")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            prettyPrint(f"Error fetching colleges: {e}")
            return []

    def query_programs(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT program_code, program_name, college_code FROM programs")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            prettyPrint(f"Error fetching programs: {e}")
            return []
        

db = DatabaseManager()

#-----------------------------utils---------------------------------#

def format_college_prog(code: str) -> bool | str:
    code = code.strip().upper()
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("SELECT program_code FROM programs WHERE UPPER(program_code) = ?", (code,))
            result = cursor.fetchone()
            if result:
                return result['program_code']
    except Exception as e:
        prettyPrint(f"Error formatting program: {e}")
    return False

def VerifyFormat(data_type : str, user_input : str, name : str) -> list[bool, str]:
    val = user_input.strip()
    student_format = dataFormat["Student"]

    if not val:
        return [False, f"{name} is required."]

    if data_type == student_format[0]:
        if FindStudentData(val): 
            return [False, "ID already exists."]
        if not re.match(r"^\d{4}-\d{4}$", val):
            return [False, "Format: 0000-0000"]
        year = int(val.split("-")[0])
        if 2000 <= year <= 2026:
            return [True, val]
        return [False, "Year must be 2000-2026"]

    elif data_type in (student_format[1], student_format[2]):
        if all(x.isalpha() or x.isspace() for x in val):
            return [True, val.title()]
        return [False, "Letters only"]
    
    elif data_type == student_format[3]:
        fmt = format_college_prog(val)
        return [True, fmt] if fmt else [False, "Invalid program"]

    elif data_type == student_format[4]:
        if val.isdigit() and 1 <= int(val) <= 5:
            return [True, val]
        return [False, "Range: 1-5"]

    return [True, val]

# Add datas ------------------------------------------------------------------------

def AddStudent(data_list) -> bool:
    query = """
        INSERT INTO students (id_number, first_name, last_name, program_code, year_level, gender)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with db._get_connection() as conn:
            conn.execute(query, (data_list[0], data_list[1], data_list[2], data_list[3], int(data_list[4]), data_list[5]))
        prettyPrint(f"Adding Student: {data_list[0]}")
        return True
    except Exception as e:
        prettyPrint(f"Error adding student: {e}")
        return False

def AddCollege(data_list) -> bool:
    query = "INSERT INTO colleges (college_code, college_name) VALUES (?, ?)"
    code = data_list[0].upper()
    try:
        with db._get_connection() as conn:
            conn.execute(query, (code, data_list[1]))
        prettyPrint(f"Adding College: {code}")
        return True
    except Exception as e:
        prettyPrint(f"Error adding college: {e}")
        return False

def AddProgram(data_list) -> bool:
    query = "INSERT INTO programs (program_code, program_name, college_code) VALUES (?, ?, ?)"
    p_code = data_list[0].upper()
    c_code = data_list[2].upper()
    try:
        with db._get_connection() as conn:
            conn.execute(query, (p_code, data_list[1], c_code))
        prettyPrint(f"Adding Program: {p_code}")
        return True
    except Exception as e:
        prettyPrint(f"Error adding program: {e}")
        return False

# Edit datas -----------------------------------------------------------------------

def EditStudent(sid: str, new_data_list : list) -> bool:
    query = """
        UPDATE students 
        SET id_number = ?, first_name = ?, last_name = ?, program_code = ?, year_level = ?, gender = ?
        WHERE id_number = ?
    """
    try:
        with db._get_connection() as conn:
            conn.execute(query, (new_data_list[0], new_data_list[1], new_data_list[2], new_data_list[3], int(new_data_list[4]), new_data_list[5], sid))
        return True
    except Exception as e:
        prettyPrint(f"Error editing student: {e}")
        return False

def EditCollege(code: str, new_name: str) -> bool:
    query = "UPDATE colleges SET college_name = ? WHERE UPPER(college_code) = ?"
    try:
        with db._get_connection() as conn:
            conn.execute(query, (new_name, code.upper()))
        return True
    except Exception as e:
        prettyPrint(f"Error editing college: {e}")
        return False

def EditProgram(p_code: str, new_data_list : list) -> bool:
    query = "UPDATE programs SET program_name = ?, college_code = ? WHERE UPPER(program_code) = ?"
    try:
        with db._get_connection() as conn:
            conn.execute(query, (new_data_list[0], new_data_list[1].upper(), p_code.upper()))
        return True
    except Exception as e:
        prettyPrint(f"Error editing program: {e}")
        return False

# Delete datas ---------------------------------------------------------------------

def DeleteCollege(code: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM colleges WHERE UPPER(college_code) = ?", (code.upper(),))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting college: {e}")
        return False

def DeleteProgram(p_code: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM programs WHERE UPPER(program_code) = ?", (p_code.upper(),))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting program: {e}")
        return False

def DeleteStudent(sid: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM students WHERE id_number = ?", (sid,))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting student: {e}")
        return False

# ------------------------- retrieve stuff ----------------------------------------- #

def get_college_by_program(program_code: str) -> str:
    code = format_college_prog(program_code)
    if not code: 
        return "invalid program code"

    query = """
        SELECT c.college_name 
        FROM programs p
        JOIN colleges c ON p.college_code = c.college_code
        WHERE p.program_code = ?
    """
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query, (code,))
            result = cursor.fetchone()
            if result:
                return result['college_name']
    except Exception as e:
        prettyPrint(f"Error getting college: {e}")
    return "College Not Found"

def GetProgramDetails(program_code: str) -> dict | bool:
    query = """
        SELECT p.program_name, c.college_name 
        FROM programs p
        JOIN colleges c ON p.college_code = c.college_code
        WHERE UPPER(p.program_code) = ?
    """
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query, (program_code.strip().upper(),))
            result = cursor.fetchone()
            
            if result:
                return {
                    "program_name": result['program_name'],
                    "college_name": result['college_name']
                }
    except Exception as e:
        prettyPrint(f"Error getting program details: {e}")
        
    return False

def FindStudentData(student_id : str) -> bool | dict:
    query = "SELECT * FROM students WHERE id_number = ?"
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query, (student_id,))
            result = cursor.fetchone()
            if result:
                return {
                    result['id_number']: {
                        'first_name': result['first_name'],
                        'last_name': result['last_name'],
                        'program_code': result['program_code'],
                        'year': str(result['year_level']),
                        'gender': result['gender']
                    }
                }
    except Exception as e:
        prettyPrint(f"Error finding student: {e}")
    return False

def GetFormat(type : Literal["Student", "College", "Program"]) -> dict : return dataFormat[type]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)