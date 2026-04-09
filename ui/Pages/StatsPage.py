from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import modules.DataSQL as data
from modules.Settings import get_settings

import time

def prettyPrint(msg: str):
    print("[STATS]:", msg)

db = data.db

class StatsPageFrame(QWidget):
    def __init__(self):
        super().__init__()
        
        self.colors = get_settings().get_colors()
        self.stats = self.fetch_data()
        self.setup_ui()
    
    def fetch_data(self):
        data = {
            'total_students': 0,
            'total_programs': 0,
            'avg_year': 0.0,
            'genders': {'Male': 0, 'Female': 0},
            'programs': {},
            'years': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        try:
            start = time.perf_counter()
            with db._get_connection() as conn:
                totals = conn.execute("""
                    SELECT 
                        COUNT(*) as total_students,
                        AVG(year_level) as avg_year
                    FROM students
                """).fetchone()
                
                data['total_students'] = totals[0] or 0
                data['avg_year'] = round(totals[1], 1) if totals[1] else 0.0
                data['total_programs'] = conn.execute("SELECT COUNT(*) FROM programs").fetchone()[0] or 0
                
                for row in conn.execute("""
                    SELECT COALESCE(gender, 'Unspecified') as gender, COUNT(*) as count 
                    FROM students 
                    GROUP BY gender
                """):
                    data['genders'][row[0]] = row[1]
               
                for row in conn.execute("""
                    SELECT COALESCE(program_code, 'Unassigned') as program_code, COUNT(*) as count
                    FROM students 
                    GROUP BY program_code 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 15
                """):
                    data['programs'][row[0]] = row[1]
            
                for row in conn.execute("""
                    SELECT year_level, COUNT(*) as count 
                    FROM students 
                    WHERE year_level IS NOT NULL 
                    GROUP BY year_level
                """):
                    if row[0]:
                        data['years'][row[0]] = row[1]
                prettyPrint(f"queue time: {time.perf_counter() - start}")

        except Exception as e:
            prettyPrint(f"stats error: {e}")
            
        return data

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        summary_layout = QHBoxLayout()
        
        total_students_lbl = QLabel(f"Total Students\n{self.stats['total_students']}")
        total_programs_lbl = QLabel(f"Programs\n{self.stats['total_programs']}")
        avg_crime_coeff_lbl = QLabel(f"Avg. Year Level\n{self.stats['avg_year']}")

        for lbl in [total_students_lbl, total_programs_lbl, avg_crime_coeff_lbl]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px; border: 1px solid gray; border-radius: 5px;")
            summary_layout.addWidget(lbl)

        main_layout.addLayout(summary_layout)

        charts_layout = QHBoxLayout()
        gender_group  = QGroupBox("Gender Distribution")
        gender_layout = QVBoxLayout()
        
        g_labels = list(self.stats['genders'].keys())
        g_sizes  = list(self.stats['genders'].values())
        
        self.gender_canvas = self.create_pie_chart(
            labels = g_labels, 
            sizes  = g_sizes,
            colors = ['#4C72B0', '#DD8452', '#55A868'] 
        )
        gender_layout.addWidget(self.gender_canvas)
        gender_group.setLayout(gender_layout)

        program_group = QGroupBox("Top Programs")
        program_layout = QVBoxLayout()
        
        p_categories = list(self.stats['programs'].keys()) or ["No Data"]
        p_values = list(self.stats['programs'].values()) or [0]
        
        self.program_canvas = self.create_bar_chart(
            categories=p_categories, 
            values=p_values,
            color='#55A868'
        )
        program_layout.addWidget(self.program_canvas)
        program_group.setLayout(program_layout)

        charts_layout.addWidget(gender_group)
        charts_layout.addWidget(program_group)
        main_layout.addLayout(charts_layout)

        year_group = QGroupBox("Year Level Breakdown")
        year_layout = QVBoxLayout()
        
        y_categories = [f"{y} Year" for y in sorted(self.stats['years'].keys())]
        y_values = [self.stats['years'][y] for y in sorted(self.stats['years'].keys())]
        
        self.year_canvas = self.create_bar_chart(
            categories=y_categories,
            values=y_values,
            color="#4496CC"
        )
        year_layout.addWidget(self.year_canvas)
        year_group.setLayout(year_layout)
        main_layout.addWidget(year_group)

    def create_pie_chart(self, labels, sizes, colors):
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        text_color = self.colors["text_color"]
     
        if sum(sizes) == 0:
            patches, texts = ax.pie([1], labels=["No Data"], colors=[text_color])
            for text in texts:
                text.set_color(text_color)
        else:
            patches, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=colors
            )
         
            for text in texts:
                text.set_color(text_color)
            for autotext in autotexts:
                autotext.set_color(text_color)
                autotext.set_weight('bold') 
            
        ax.axis('equal') 
        fig.patch.set_facecolor('none') 
        fig.tight_layout()
        return FigureCanvas(fig)

    def create_bar_chart(self, categories, values, color):
        fig        = Figure(figsize=(5, 3), dpi=100)
        ax         = fig.add_subplot(111)
        text_color = self.colors["text_color"]
        
        bars = ax.bar(categories, values, color=color)
        total_bars = len(bars)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height*0.85,
                    f'{int(height)}',
                    ha='center', va='bottom', color=text_color, fontweight='bold', fontsize=max(5.5, 70 / (total_bars + 3)))

        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        total_categ = len(categories)
        if total_categ > 5:
            ax.tick_params(axis='x', colors=text_color, labelsize=total_categ/2, rotation=max(total_categ*2.5, 85))
        else:
            ax.tick_params(axis='x', colors=text_color, labelsize=10, rotation=0)
            
        ax.tick_params(axis='y', colors=text_color)
        
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout()
        return FigureCanvas(fig)