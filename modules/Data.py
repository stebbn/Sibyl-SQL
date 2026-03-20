import csv
import re
import os
import sys
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

colleges_path = get_save_path("colleges.csv")
programs_path = get_save_path("programs.csv")
data_path     = get_save_path("data.csv")

dataFormat = {
    "Student" : ["id_no", "first_name", "last_name", "program_code", "year", "gender"],
    "College" : ["college_code","college_name"],
    "Program" : ["program_code","program_name","college_code"]
}

college_data  = {}
program_data  = {}
student_data  = {}

paths = {"Student": data_path, "College": colleges_path, "Program": programs_path}
#-----------------------------utils---------------------------------#

def format_college_prog(code: str) -> bool | str:
    for i in program_data:
        if i.upper() == code.strip().upper():
            return i
    return False

def get_college_by_program(program_code: str) -> str:
    program_code = format_college_prog(program_code)
    if not program_code: 
        return "invalid program code"

    college_code = program_data[program_code].get("college")
    return college_data.get(college_code, "College Not Found")

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

def LoadCSV(file_path, callback) -> dict:
    try:
        if not os.path.exists(file_path):
            prettyPrint(f"Warning: {os.path.basename(file_path)} not found.")
            return {}
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return callback(reader)
    except Exception as e:
        prettyPrint(f"Load Error [{os.path.basename(file_path)}]: {e}")
        return {"actual bum x3"}

# ------------------------- main data funcs --------------------------------- #

def SyncAll():
    global student_data, college_data, program_data
    
    start = time.perf_counter()

    def student_cb(reader):
        return {row['id_no']: {k: row[k] for k in dataFormat["Student"][1:]} for row in reader}
    
    student_data = LoadCSV(data_path, student_cb)
    college_data = LoadCSV(colleges_path, lambda r: {row[dataFormat["College"][0]]: row[dataFormat["College"][1]] for row in r})

    def program_cb(reader):
        return {row['program_code']: {"name": row[dataFormat["Program"][1]], "college": row[dataFormat["Program"][2]]} for row in reader}
    program_data = LoadCSV(programs_path, program_cb)

    prettyPrint(f"Total data load took {time.perf_counter() - start:.4f} seconds.")

def SaveData(type: Literal["Student", "College", "Program"], data_dict: dict) -> bool:
    start = time.perf_counter()

    try:
        with open(paths[type], mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=dataFormat[type])
            writer.writeheader()
            
            for key, info in data_dict.items():
                primary_key = dataFormat[type][0]
              
                if type == "College":
                    row = {primary_key: key, dataFormat[type][1]: info}
                elif type == "Program":
                   row = {primary_key: key, dataFormat[type][1]: info.get("name"), dataFormat[type][2]: info.get("college")}
                elif type == "Student":
                    row = {primary_key: key, **info}
                else:
                    prettyPrint("attempt save data but unknown type", type)
                    break
                    
                writer.writerow(row)
        prettyPrint(f"Saved {type} | time elapsed {time.perf_counter() - start:.4f} seconds.")

        return True
    except Exception as e:
        prettyPrint(f"Unable to save [{type}]: {e}")
        return False    
    
# Add datas ------------------------------------------------------------------------

def AddStudent(data_list) -> bool:
    global student_data
    sid = data_list[0]
   
    student_data[sid] = {}

    for i,v in enumerate(dataFormat["Student"][1:], start=1):
        student_data[sid][v] = data_list[i]
    
    prettyPrint(f"Adding Student: {sid}")
    return SaveData("Student", student_data)

def AddCollege(data_list) -> bool:
    global college_data
    code = data_list[0].upper()
   
    college_data[code] = data_list[1]
    
    prettyPrint(f"Adding College: {code}")
    return SaveData("College", college_data)

def AddProgram(data_list) -> bool:
    global program_data
    p_code = data_list[0].upper()
    
    program_data[p_code] = {
        "name": data_list[1],
        "college": data_list[2].upper()
    }
    
    prettyPrint(f"Adding Program: {p_code}")
    return SaveData("Program", program_data)

# Edit datas -----------------------------------------------------------------------

def EditStudent(sid: str, new_data_list : dict) -> bool:
    global student_data
    if sid not in student_data: return False

    student_data[sid] = {}

    for i,v in enumerate(dataFormat["Student"][1:], start=1):
        student_data[sid][v] = new_data_list[i]

    return SaveData("Student", student_data)

def EditCollege(code: str, new_name: str) -> bool:
    global college_data
    code = code.upper()
    if code not in college_data: return False

    college_data[code] = new_name
    return SaveData("College", college_data)

def EditProgram(p_code: str, new_data_list : list) -> bool:
    global program_data
    p_code = format_college_prog(p_code)
    if p_code not in program_data: return False

    program_data[p_code] = {
        "name": new_data_list[0],
        "college": new_data_list[1].upper()
    }
    return SaveData("Program", program_data)

# Delete datas ---------------------------------------------------------------------

def DeleteStudent(sid: str) -> bool:
    global student_data
    if sid in student_data:
        del student_data[sid]
        return SaveData("Student", student_data)
    return False

def DeleteCollege(code: str) -> bool:
    global college_data
    code = code.upper()
    if code in college_data:
        del college_data[code]
        return SaveData("College", college_data)
    return False

def DeleteProgram(p_code: str) -> bool:
    global program_data
    p_code = p_code.upper()
    if p_code in program_data:
        del program_data[p_code]
        return SaveData("Program", program_data)
    return False

# ------------------------- retrieve stuff ----------------------------------------- #

def FindStudentData(student_id : str) -> bool | dict:
    all_students = student_data
    if student_id in all_students:
        return {student_id: all_students[student_id]}
    return False

def GetFormat(type : Literal["Student", "College", "Program"]) -> dict : return dataFormat[type]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

SyncAll()