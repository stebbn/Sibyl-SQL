import sqlite3
import re
import os
import sys
import math

import time

from modules.Settings import get_settings
from typing import Literal, Union

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
        self.settings_module = get_settings()

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
        """recalculated all pages"""

        self.infos["students"]["Pages"] = self._calculate_pages("students")
        self.infos["colleges"]["Pages"] = self._calculate_pages("colleges")
        self.infos["programs"]["Pages"] = self._calculate_pages("programs")

    def _get_pages(self, table : Literal["students", "colleges", "programs"]) -> int:
        """returns pages for table"""

        tables = self.infos.get(table)
        value = tables.get("Pages")

        if value: return self.infos[table]["Pages"]
        prettyPrint(f"get pages error: {table}, {tables} {value}")
        return None
    
    def _get_table_val(self, table : Literal["students", "colleges", "programs"], val : Literal["Pages", "Total"]):
        table = self.infos.get(table)
        value = table.get(val)
        if table and value: return value
        prettyPrint(f"get error: {table}, {val}")
        return None

    def _calculate_pages(self, table : str, search="", search_field=None) -> int:
        try:
            with self._get_connection() as conn:

                if table == "students" and search_field and search_field.lower() == "unassigned":
                    query = "SELECT COUNT(*) FROM students WHERE program_code IS NULL OR TRIM(program_code) = ''"
                    cursor = conn.execute(query)
                elif search and search_field:
                    query = f"SELECT COUNT(*) FROM {table} WHERE {search_field} LIKE ?"
                    search_term = f"{search}%"
                    cursor = conn.execute(query, (search_term,))
                else:
                    query = f"SELECT COUNT(*) FROM {table}"
                    cursor = conn.execute(query)
               
                total_count = int(cursor.fetchone()[0])
              
                if not search and not (search_field and search_field.lower() == "unassigned"):
                    self.infos[table]["Total"] = total_count
             
                calculated_pages = math.ceil(total_count / self.settings_module.settings.get("page_content_size"))
                return max(1, calculated_pages)
                
        except Exception as e:
            prettyPrint(f"Error calculating pages for {table}: {e}")
            return 1

    def _get_connection(self) -> sqlite3.Connection:
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
            college_code TEXT,
            FOREIGN KEY (college_code) REFERENCES colleges (college_code) ON UPDATE CASCADE ON DELETE SET NULL
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

    def query_students(self, search="", search_field="id_number", page=1, sort="id_number", asc=True) -> list[dict]:
        """default search function for students"""

        start_time = time.perf_counter()

        try:
            with self._get_connection() as conn:
                max_page = self.settings_module.settings.get("page_content_size")
                offset   = (page - 1) * max_page
                sort_dir = "ASC" if asc else "DESC"
              
                search_max_page = self._calculate_pages("students", search, search_field)
                self.infos["students"]["Pages"] = search_max_page

                if search_field and search_field.lower() == "unassigned":
                    where = "WHERE program_code IS NULL OR TRIM(program_code) = ''"
                    query_params = (max_page, offset)
                    queued_search = "N/A (Unassigned Filter)"
            
                elif search and search_field:
                    where = f"WHERE {search_field} LIKE ?"
                    search_term = f"{search}%"
                    query_params = (search_term, max_page, offset)
                    queued_search = search_term
             
                else:
                    where = ""
                    query_params = (max_page, offset)
                    queued_search = "None"

                query = f"""
                    SELECT id_number, first_name, last_name, year_level, gender, program_code 
                    FROM students
                    {where}
                    ORDER BY {sort} {sort_dir}
                    LIMIT ? OFFSET ?
                """
                
                cursor = conn.execute(query, query_params)

                prettyPrint(f"queued: {queued_search}, {search_field}, {page}, {sort}, {sort_dir} | time: {time.perf_counter() - start_time}")
                return [dict(row) for row in cursor.fetchall()], search_max_page
                
        except Exception as e:
            prettyPrint(f"Error fetching students: {e}")
            return [], 1

    def query_college(self) -> list[dict]:
        """returns all colleges"""

        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT college_code, college_name FROM colleges")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            prettyPrint(f"Error fetching colleges: {e}")
            return []

    def query_programs(self) -> list[dict]:
        """returns all programs"""

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
    """formats any given college code to how the system reads it. If dosent exist returns False"""

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
    """handles verification inputs for student data"""

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
        if 2023 <= year <= 2026:
            return [True, val]
        return [False, "Year must be 2023-2026"]

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
        return False, f"{e}"

styled_error = {

}

def AddCollege(data_list) -> bool:
    query = "INSERT INTO colleges (college_code, college_name) VALUES (?, ?)"
    code = data_list[0].upper()
    try:
        with db._get_connection() as conn:
            conn.execute(query, (code, data_list[1]))
        prettyPrint(f"Adding College: {code}")
        return True, "success"
    except sqlite3.IntegrityError as e:
        styled_error = ""
        if "college.college_code" in str(e) or "college" in str(e):
            styled_error = "That college code address is already registered. Please try another."
        else:
            styled_error = "A database conflict occurred. Please check your inputs."
        return False, f"{styled_error}"
    except Exception as e:
        prettyPrint(f"Error adding college: {e}")
        return False, f"{e}"

def AddProgram(data_list) -> bool:
    query = "INSERT INTO programs (program_code, program_name, college_code) VALUES (?, ?, ?)"
    p_code = data_list[0].upper()
    c_code = data_list[2].upper()
    try:
        with db._get_connection() as conn:
            conn.execute(query, (p_code, data_list[1], c_code))
        prettyPrint(f"Adding Program: {p_code}")
        return True, "success"
    except sqlite3.IntegrityError as e:
        styled_error = ""
        if "programs.program_code" in str(e) or "programs" in str(e):
            styled_error = "That program code address is already registered. Please try another."
        else:
            styled_error = f"A database conflict occurred. Please check your inputs. ({e})"
        return False, f"{styled_error}"
    except Exception as e:
        prettyPrint(f"Error adding program: {e}")
        return False, f"{e}"

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
        return True, "success"
    except Exception as e:
        prettyPrint(f"Error editing student: {e}")
        return False, f"{e}"

def EditCollege(code: str, new_name: str) -> bool:
    query = "UPDATE colleges SET college_name = ? WHERE UPPER(college_code) = ?"
    try:
        with db._get_connection() as conn:
            conn.execute(query, (new_name, code.upper()))
        return True, "success"
    except Exception as e:
        prettyPrint(f"Error editing college: {e}")
        return False, f"{e}"

def EditProgram(p_code: str, new_data_list : list) -> bool:
    query = "UPDATE programs SET program_name = ?, college_code = ? WHERE UPPER(program_code) = ?"
    try:
        with db._get_connection() as conn:
            conn.execute(query, (new_data_list[1], new_data_list[2].upper(), p_code.upper().strip()))
        return True, "success"
    except Exception as e:
        prettyPrint(f"Error editing program: {e} | {p_code} | {new_data_list}")
        return False, f"{e}"

# Delete datas ---------------------------------------------------------------------    

def checkCollegeDelete(code: str) -> list[Union[int,int]]:
    """checks for programs under a college and if you can safely delete it"""

    query = """
        SELECT program_code
        FROM programs
        WHERE UPPER(college_code) = ?
    """
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query, (code.upper(),))
            results = cursor.fetchall()
            
            program_codes = [row['program_code'] for row in results]
            
            if len(program_codes) == 0:
                prettyPrint(f"can safely delete {code}")
                return True
            else:
                return [len(program_codes), get_students_in_program(program_codes)]
                
    except Exception as e:
        prettyPrint(f"Error checking safe college: {e}")
        return f"error: [{e}]"

def DeleteCollege(code: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM colleges WHERE UPPER(college_code) = ?", (code.upper(),))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting college: {e}")
        return False, f"{e}"

def DeleteProgram(p_code: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM programs WHERE UPPER(program_code) = ?", (p_code.upper(),))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting program: {e}")
        return False, f"{e}"

def DeleteStudent(sid: str) -> bool:
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("DELETE FROM students WHERE id_number = ?", (sid,))
            if cursor.rowcount > 0:
                return True
            return False
    except Exception as e:
        prettyPrint(f"Error deleting student: {e}")
        return False, f"{e}"

# ------------------------- retrieve stuff ----------------------------------------- #

def get_students_in_program(program_codes: tuple | list) -> int:
    
    qmarks = ", ".join(["?"] * len(program_codes))
    query = f"""
                SELECT COUNT(id_number)
                FROM students
                WHERE UPPER(program_code) IN ({qmarks})
            """
    try:
        with db._get_connection() as conn:
            codelist = tuple(str(code).strip().upper() for code in program_codes)
        
            cursor = conn.execute(query, codelist)
            count = int(cursor.fetchone()[0]) 
            
            prettyPrint(f"total students affected by {codelist}: {count}")
            return count
            
    except Exception as e:
        prettyPrint(f"Error checking affected students: {e}")
        return f"error: [{e}]"

def get_college_name(college_code : str) -> str:
    college_code = college_code.upper()
    
    query = """
        SELECT college_name 
        FROM colleges
        WHERE college_code = ?
    """
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query, (college_code,))
            result = cursor.fetchone()[0]
            if result:
                return result
    except Exception as e:
        prettyPrint(e)

def get_colleges() -> list:
    query = """
        SELECT college_code
        FROM colleges
        ORDER BY college_code ASC
    """
    try:
        with db._get_connection() as conn:
            cursor = conn.execute(query)
            return [row["college_code"] for row in cursor.fetchall()]

    except Exception as e:
        prettyPrint(f"tried getting colleges: {e}")


def get_college_by_program(program_code : str) -> str:
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

def GetProgramDetails(program_code : str) -> dict | bool:
    query = """
     SELECT p.program_name, c.college_name 
     FROM programs p
     LEFT JOIN colleges c ON p.college_code = c.college_code
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
                        key: result[key] for key in dataFormat['Student'][1:]
                    }
                }               
    except Exception as e:
        prettyPrint(f"Error finding student: {e}")
    return False

def GetFormat(type : Literal["Student", "College", "Program"]) -> dict : return dataFormat[type]