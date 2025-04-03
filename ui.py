import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel, QLineEdit, QComboBox, QHBoxLayout,
                           QGroupBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator, QPixmap
import numpy as np
import lashing as ls
import load as ld
import forces as ff
import calcs
import latex_report

class LashingInput(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        layout = QHBoxLayout(self)
        
        # Left column
        left_column = QVBoxLayout()
        self.add_input_field(left_column, "Angle α (deg):", "alpha")
        self.add_input_field(left_column, "Angle β (deg):", "beta")
        self.add_input_field(left_column, "Breaking Strength:", "breaking_strength")
        left_column.addStretch()
        
        # Right column
        right_column = QVBoxLayout()
        self.add_input_field(right_column, "Side:", "side", is_combo=True)
        right_column.addStretch()
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_self)
        right_column.addWidget(remove_btn)
        
        layout.addLayout(left_column)
        layout.addLayout(right_column)
    
    def add_input_field(self, layout, label_text, field_name, is_combo=False):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        label = QLabel(label_text)
        label.setFont(QFont('Arial', 10))
        container_layout.addWidget(label)
        
        if is_combo:
            field = QComboBox()
            field.addItems(["Front (F)", "Rear (R)", "Left (L)", "Aft (A)"])
        else:
            field = QLineEdit()
            field.setValidator(QDoubleValidator())
        
        field.setFont(QFont('Arial', 10))
        field.setMinimumHeight(25)
        setattr(self, field_name, field)
        container_layout.addWidget(field)
        
        layout.addWidget(container)
    
    def remove_self(self):
        self.deleteLater()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lashing Calculator")
        self.setMinimumSize(1400, 800)  # Increased width to accommodate image
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Changed to horizontal layout
        
        # Left side - Input sections
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create scroll area for inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_layout.addWidget(scroll)
        
        # Create content widget
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        
        # Add title
        title = QLabel("Lashing Calculator")
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add input sections
        self.create_load_section(layout)
        self.create_environment_section(layout)
        self.create_lashing_section(layout)
        
        # Set default values for load and environment
        self.dimx.setText("3")
        self.dimy.setText("23")
        self.dimz.setText("2.7")
        self.mass.setText("160")
        self.slope.setText("3")
        self.wind_force.setCurrentText("0")
        self.friction_coeff.setText("0.2")
        
        # Add calculate button
        calculate_btn = QPushButton("Calculate")
        calculate_btn.setFont(QFont('Arial', 14))
        calculate_btn.clicked.connect(self.calculate)
        calculate_btn.setMinimumHeight(50)
        layout.addWidget(calculate_btn)
        
        # Add result display
        self.result_label = QLabel("")
        self.result_label.setFont(QFont('Arial', 16))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        # Add some spacing
        layout.addStretch()
        
        # Right side - Image display
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(350, 350)
        self.image_label.setStyleSheet("border: 1px solid black;")
        right_layout.addWidget(self.image_label)
        
        # Add image description
        image_desc = QLabel("Lashing Configuration Diagram")
        image_desc.setFont(QFont('Arial', 14))
        image_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(image_desc)
        
        # Add stretch to push content to top
        right_layout.addStretch()
        
        # Add both sides to main layout
        main_layout.addWidget(left_widget, stretch=2)  # Input section takes 2/3 of space
        main_layout.addWidget(right_widget, stretch=1)  # Image section takes 1/3 of space
        
        # Load initial image
        self.load_image("pics/lashingPic.png")
    
    def create_load_section(self, layout):
        group = QGroupBox("Load Specifications")
        group.setFont(QFont('Arial', 14))
        group_layout = QVBoxLayout()
        
        # Create grid for load inputs
        load_grid = QWidget()
        load_layout = QHBoxLayout(load_grid)
        
        # Left column
        left_column = QVBoxLayout()
        self.add_input_field(left_column, "Length (m):", "dimx")
        self.add_input_field(left_column, "Width (m):", "dimy")
        left_column.addStretch()
        
        # Right column
        right_column = QVBoxLayout()
        self.add_input_field(right_column, "Height (m):", "dimz")
        self.add_input_field(right_column, "Mass (tonnes):", "mass")
        right_column.addStretch()
        
        load_layout.addLayout(left_column)
        load_layout.addLayout(right_column)
        group_layout.addWidget(load_grid)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_environment_section(self, layout):
        group = QGroupBox("Environmental Conditions")
        group.setFont(QFont('Arial', 14))
        group_layout = QVBoxLayout()
        
        # Create grid for environment inputs
        env_grid = QWidget()
        env_layout = QHBoxLayout(env_grid)
        
        # Left column
        left_column = QVBoxLayout()
        self.add_input_field(left_column, "Slope (degrees):", "slope")
        self.add_input_field(left_column, "Friction Coefficient:", "friction_coeff")
        left_column.addStretch()
        
        # Right column
        right_column = QVBoxLayout()
        self.add_input_field(right_column, "Wind Force (Beaufort):", "wind_force", is_combo=True)
        right_column.addStretch()
        
        env_layout.addLayout(left_column)
        env_layout.addLayout(right_column)
        group_layout.addWidget(env_grid)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_lashing_section(self, layout):
        group = QGroupBox("Lashing Configuration")
        group.setFont(QFont('Arial', 14))
        group_layout = QVBoxLayout()
        
        # Container for lashing inputs
        self.lashing_container = QWidget()
        self.lashing_layout = QVBoxLayout(self.lashing_container)
        group_layout.addWidget(self.lashing_container)
        
        # Add first lashing input
        self.add_lashing_input()
        
        # Add button to add more lashings
        add_lashing_btn = QPushButton("Add Another Lashing")
        add_lashing_btn.clicked.connect(self.add_lashing_input)
        group_layout.addWidget(add_lashing_btn)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_lashing_input(self):
        # Create new lashing input widget
        lashing_input = LashingInput()
        
        # If this is not the first lashing, copy values from the first one
        if self.lashing_layout.count() > 0:
            first_lashing = self.lashing_layout.itemAt(0).widget()
            lashing_input.alpha.setText(first_lashing.alpha.text())
            lashing_input.beta.setText(first_lashing.beta.text())
            lashing_input.breaking_strength.setText(first_lashing.breaking_strength.text())
            lashing_input.side.setCurrentText(first_lashing.side.currentText())
        
        # Add to layout
        self.lashing_layout.addWidget(lashing_input)
        
        # Add remove button if this is not the first lashing
        if self.lashing_layout.count() > 1:
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda: self.remove_lashing_input(lashing_input, remove_btn))
            self.lashing_layout.addWidget(remove_btn)
    
    def remove_lashing_input(self, lashing_input, remove_btn):
        lashing_input.deleteLater()
        remove_btn.deleteLater()
    
    def add_input_field(self, layout, label_text, field_name, is_combo=False):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        label = QLabel(label_text)
        label.setFont(QFont('Arial', 12))
        container_layout.addWidget(label)
        
        if is_combo:
            field = QComboBox()
            if field_name == "wind_force":
                field.addItems([str(i) for i in range(13)])  # Beaufort scale 0-12
        else:
            field = QLineEdit()
            if field_name in ["dimx", "dimy", "dimz", "mass", "slope"]:
                field.setValidator(QDoubleValidator())
        
        field.setFont(QFont('Arial', 12))
        field.setMinimumHeight(30)
        setattr(self, field_name, field)
        container_layout.addWidget(field)
        
        layout.addWidget(container)
    
    def calculate(self):
        try:
            # Get load parameters
            dimx = float(self.dimx.text())
            dimy = float(self.dimy.text())
            dimz = float(self.dimz.text())
            mass = float(self.mass.text())  # Convert tonnes to kg for calculations
            
            # Create Load object
            load = ld.Load(dimx, dimy, dimz, mass)
            print(load.weight)
            
            # Get environmental parameters
            slope = float(self.slope.text())
            wind_force = int(self.wind_force.currentText())
            friction_coeff = float(self.friction_coeff.text())
            
            # Create Wind and Forces objects
            wind = ff.Wind(load, wind_force)
            forces = ff.Forces(load, slope, wind)
            
            # Get lashing parameters and create Lashing objects
            lashings = []
            lashings_data = []  # Store raw lashing data for LaTeX report
            for i in range(self.lashing_layout.count()):
                widget = self.lashing_layout.itemAt(i).widget()
                if isinstance(widget, LashingInput):
                    try:
                        alpha = float(widget.alpha.text())
                        beta = float(widget.beta.text())
                        breaking_strength = float(widget.breaking_strength.text())
                        side = widget.side.currentText()[0]  # Get first letter (F, R, L, A)
                        
                        # Store raw lashing data
                        lashings_data.append({
                            'alpha': alpha,
                            'beta': beta,
                            'breaking_strength': breaking_strength,
                            'side': side
                        })
                        
                        # Create Lashing object
                        lashing = ls.Lashing(
                            alpha=alpha,
                            beta=beta,
                            BreakingStrength=breaking_strength,
                            FrictionCoefficient=friction_coeff,
                            RelativeSide=side
                        )
                        lashings.append(lashing)
                        print(lashing.fx,lashing.fy)
                    except ValueError as e:
                        raise ValueError(f"Invalid input in lashing {i+1}: {str(e)}")
            
            # Perform calculations
            transverse_result = []
            longitudinal_result = []
            
            # Capture print output from calculations
            import io
            from contextlib import redirect_stdout
            
            # Transverse sliding calculation
            f = io.StringIO()
            with redirect_stdout(f):
                calcs.transverseSliding(load, lashings, forces)
            transverse_result = f.getvalue().split('\n')
            
            # Longitudinal sliding calculation
            f = io.StringIO()
            with redirect_stdout(f):
                calcs.longtidunalSliding(load, lashings, forces)
            longitudinal_result = f.getvalue().split('\n')
            
            # Generate LaTeX report with raw input values
            latex_report.generate_latex_report(
                dimx, dimy, dimz, mass,
                slope, wind_force, friction_coeff,
                lashings_data,
                transverse_result,
                longitudinal_result
            )
            
            # Format the result
            result = (
                f"Calculation Results:\n\n"
                f"Transverse Sliding Analysis:\n"
            )
            
            # Add transverse sliding results
            for line in transverse_result:
                if line.strip():
                    result += f"  {line}\n"
            
            result += "\nLongitudinal Sliding Analysis:\n"
            # Add longitudinal sliding results
            for line in longitudinal_result:
                if line.strip():
                    result += f"  {line}\n"
            
            result += "\nLaTeX report has been generated as 'lashing_report.tex'"
            self.result_label.setText(result)
            
        except ValueError as e:
            self.result_label.setText(f"Error: Please check your input values\n{str(e)}")
        except Exception as e:
            self.result_label.setText(f"Unexpected error: {str(e)}")

    def load_image(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale the image to a fixed size while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    350, 350,  # Increased from 280 to 350 pixels
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Image not found")
        except Exception as e:
            self.image_label.setText(f"Error loading image: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 