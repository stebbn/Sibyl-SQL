# jarvis give me random people

import random
import sys 

from modules.DataSQL import db

first_names_m = [
    "Aaron","Adam","Adrian","Aiden","Alan","Albert","Alex","Alexander","Andrew","Anthony",
    "Arthur","Austin","Benjamin","Blake","Brandon","Brian","Caleb","Calvin","Cameron","Carl",
    "Carlos","Carter","Charles","Christian","Christopher","Cole","Connor","Daniel","David","Dean",
    "Derek","Dominic","Dylan","Edward","Eli","Elijah","Elliot","Ethan","Evan","Felix",
    "Francis","Gabriel","Gavin","George","Grant","Gregory","Harrison","Henry","Hunter","Ian",
    "Isaac","Jack","Jackson","Jacob","James","Jason","Jasper","Jayden","Jeremy","Joel",
    "John","Jonathan","Jordan","Joseph","Joshua","Julian","Justin","Keith","Kevin","Kyle",
    "Landon","Lawrence","Leo","Leon","Leonard","Liam","Logan","Louis","Lucas","Luke",
    "Marcus","Mark","Martin","Mason","Matthew","Max","Michael","Miles","Nathan","Nicholas",
    "Noah","Oliver","Oscar","Owen","Patrick","Paul","Peter","Philip","Preston","Raymond",
    "Richard","Robert","Ryan","Samuel","Scott","Sean","Sebastian","Simon","Spencer","Stephen",
    "Steven","Theo","Thomas","Timothy","Tristan","Tyler","Victor","Vincent","Walter","William",
    "Zachary"
]

first_names_f = [
    "Abigail","Ada","Adeline","Alexandra","Alice","Alicia","Allison","Alyssa","Amelia","Amy",
    "Andrea","Angela","Anna","Annabelle","Ashley","Audrey","Autumn","Ava","Avery","Bella",
    "Bethany","Bianca","Brenda","Brianna","Brooke","Camila","Carla","Carmen","Caroline","Cassandra",
    "Catherine","Charlotte","Chloe","Christina","Claire","Clara","Danielle","Diana","Eleanor","Elena",
    "Elise","Elizabeth","Ella","Emily","Emma","Erica","Eva","Evelyn","Faith","Fiona",
    "Gabriella","Georgia","Grace","Hailey","Hannah","Hazel","Heather","Heidi","Isabel","Isabella",
    "Isla","Ivy","Jade","Jamie","Jane","Jasmine","Jennifer","Jessica","Julia","Juliana",
    "Kaitlyn","Karen","Katherine","Kayla","Kelly","Kimberly","Kristen","Laura","Lauren","Layla",
    "Leah","Lena","Lillian","Lily","Luna","Madeline","Madison","Maria","Maya","Megan",
    "Melanie","Mia","Michelle","Mila","Molly","Naomi","Natalie","Nicole","Nina","Nora",
    "Olivia","Paige","Patricia","Penelope","Rachel","Rebecca","Riley","Rose","Ruby","Samantha",
    "Sara","Savannah","Scarlett","Sienna","Sophia","Stella","Summer","Sydney","Taylor","Valerie",
    "Vanessa","Victoria","Violet","Zoe"
]

last_names = [
    "Adams","Allen","Anderson","Armstrong","Atkins","Austin","Bailey","Baker","Barnes","Bennett",
    "Bishop","Black","Bowman","Boyd","Bradley","Brooks","Brown","Bryant","Burke","Burns",
    "Butler","Campbell","Carter","Chambers","Chapman","Clark","Cole","Coleman","Collins","Cook",
    "Cooper","Cox","Crawford","Cruz","Daniels","Davidson","Davis","Dawson","Diaz","Dixon",
    "Douglas","Duncan","Edwards","Ellis","Evans","Ferguson","Fisher","Fleming","Ford","Foster",
    "Fox","Garcia","Gardner","George","Gibson","Gomez","Gonzalez","Gordon","Graham","Grant",
    "Gray","Green","Griffin","Hall","Hamilton","Hansen","Harris","Harrison","Hart","Harvey",
    "Hawkins","Hayes","Henderson","Henry","Hernandez","Hicks","Hill","Hoffman","Holmes","Howard",
    "Hudson","Hughes","Hunt","Hunter","Jackson","James","Jenkins","Johnson","Johnston","Jones",
    "Jordan","Keller","Kelly","Kennedy","Kim","King","Knight","Lane","Lawrence","Lawson",
    "Lee","Lewis","Long","Lopez","Marshall","Martin","Martinez","Mason","Matthews","Mccoy",
    "Mendoza","Mills","Mitchell","Moore","Morales","Morgan","Morris","Murphy","Myers","Nelson",
    "Nguyen","Nichols","Ortiz","Owens","Palmer","Parker","Patel","Patterson","Payne","Perez",
    "Perkins","Perry","Peterson","Phillips","Pierce","Porter","Powell","Price","Ramirez","Ramos",
    "Reed","Reyes","Reynolds","Rice","Richards","Richardson","Rivera","Roberts","Robinson","Rodriguez",
    "Rogers","Ross","Russell","Sanchez","Sanders","Schmidt","Scott","Shaw","Simmons","Simpson",
    "Smith","Snyder","Spencer","Stephens","Stevens","Stewart","Stone","Sullivan","Taylor","Thomas",
    "Thompson","Torres","Tucker","Turner","Vasquez","Wagner","Walker","Wallace","Walsh","Ward",
    "Washington","Watkins","Watson","Weaver","Webb","Weber","Wells","West","Wheeler","White",
    "Williams","Williamson","Willis","Wilson","Woods","Wright","Young"
]


colleges = [
    ("CCS", "College of Computer Studies"),
    ("COE", "College of Engineering and Technology"),
    ("CSM", "College of Science and Mathematics"),
    ("CASS", "College of Arts and Social Sciences"),
    ("CEBA", "College of Economics, Business and Accountancy"),
    ("CED", "College of Education"),
    ("CHS", "College of Health Sciences"),
    ("DSC", "Demon Slayer Corps")
]

programs = [
    ("BSCS", "Bachelor of Science in Computer Science", "CCS"),
    ("BSIT", "Bachelor of Science in Information Technology", "CCS"),
    ("BSIS", "Bachelor of Science in Information Systems", "CCS"),
    ("BSCA", "Bachelor of Science in Computer Applications", "CCS"),
    ("BSCE", "Bachelor of Science in Civil Engineering", "COE"),
    ("BSCerE", "Bachelor of Science in Ceramics Engineering", "COE"),
    ("BSChE", "Bachelor of Science in Chemical Engineering", "COE"),
    ("BSCpE", "Bachelor of Science in Computer Engineering", "COE"),
    ("BSECE", "Bachelor of Science in Electronics & Communications Engineering", "COE"),
    ("BSEE", "Bachelor of Science in Electrical Engineering", "COE"),
    ("BSME", "Bachelor of Science in Mechanical Engineering", "COE"),
    ("BSMetE", "Bachelor of Science in Metallurgical Engineering", "COE"),
    ("BS-EMET", "Bachelor of Science in Environmental Engineering Technology", "COE"),
    ("BSIAM", "Bachelor of Science in Industrial Automation & Mechatronics", "COE"),
    ("BSETM", "Bachelor of Science in Engineering Technology Management", "COE"),
    ("BSBio-Bot", "Bachelor of Science in Biology (Botany)", "CSM"),
    ("BSBio-Zoo", "Bachelor of Science in Biology (Zoology)", "CSM"),
    ("BSBio-Mar", "Bachelor of Science in Biology (Marine)", "CSM"),
    ("BSBio-Gen", "Bachelor of Science in Biology (General)", "CSM"),
    ("BSChem", "Bachelor of Science in Chemistry", "CSM"),
    ("BSMath", "Bachelor of Science in Mathematics", "CSM"),
    ("BSPhys", "Bachelor of Science in Physics", "CSM"),
    ("BSStat", "Bachelor of Science in Statistics", "CSM"),
    ("BSPsych", "Bachelor of Science in Psychology", "CASS"),
    ("BA-ENG", "Bachelor of Arts in English", "CASS"),
    ("BA-FIL", "Bachelor of Arts in Filipino", "CASS"),
    ("BA-HIS", "Bachelor of Arts in History", "CASS"),
    ("BA-POLSCI", "Bachelor of Arts in Political Science", "CASS"),
    ("BSA", "Bachelor of Science in Accountancy", "CEBA"),
    ("BSBA-BE", "Bachelor of Science in Business Administration - Business Economics", "CEBA"),
    ("BSBA-Econ", "Bachelor of Science in Business Administration - Economics", "CEBA"),
    ("BSBA-EM", "Bachelor of Science in Business Administration - Entrepreneurial Marketing", "CEBA"),
    ("BSHRM", "Bachelor of Science in Hotel and Restaurant Management", "CEBA"),
    ("BSEd-Bio", "Bachelor of Secondary Education (Biology)", "CED"),
    ("BSEd-Chem", "Bachelor of Secondary Education (Chemistry)", "CED"),
    ("BSEd-Phys", "Bachelor of Secondary Education (Physics)", "CED"),
    ("BSEd-Math", "Bachelor of Secondary Education (Mathematics)", "CED"),
    ("BSEd-MAPEH", "Bachelor of Secondary Education (MAPEH)", "CED"),
    ("BSEd-TLE", "Bachelor of Secondary Education (TLE)", "CED"),
    ("BEEd-Eng", "Bachelor of Elementary Education (English)", "CED"),
    ("BSN", "Bachelor of Science in Nursing", "CHS"),
    ("BSDM", "Bachelor in Demon Slaying", "DSC")
]

def run_seeder(student_count):
    print("YES SIR INITING THE SEEDER")

    program_codes = [p[0] for p in programs]

    print(f"Generating {student_count} random students...")
    students_to_insert = []
    
    for i in range(1, student_count + 1):
        id_num = f"2024-{i:04d}" 
        is_male = random.choice([True, False])
        gender = "Male" if is_male else "Female"
        
        first_name = random.choice(first_names_m) if is_male else random.choice(first_names_f)
        last_name = random.choice(last_names)
        program = random.choice(program_codes)
        year = random.randint(1, 5)
        
        students_to_insert.append((id_num, first_name, last_name, program, year, gender))

    try:
        with db._get_connection() as conn:
            conn.executemany("INSERT OR REPLACE INTO colleges (college_code, college_name) VALUES (?, ?)", colleges)
            conn.executemany("INSERT OR REPLACE INTO programs (program_code, program_name, college_code) VALUES (?, ?, ?)", programs)
            
            conn.executemany("""
                INSERT OR IGNORE INTO students (id_number, first_name, last_name, program_code, year_level, gender)
                VALUES (?, ?, ?, ?, ?, ?)
            """, students_to_insert)
            
        print(f"Success! Seeded {len(colleges)} Colleges, {len(programs)} Programs, and {student_count} Students.")
    except Exception as e:
        print(f"Database error during seed: {e}")

if __name__ == "__main__":
    run_seeder(3000)
