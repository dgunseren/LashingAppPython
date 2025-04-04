import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel, QLineEdit, QComboBox, QHBoxLayout,
                           QGroupBox, QScrollArea, QFrame, QMenuBar, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator, QPixmap, QAction
import numpy as np
import lashing as ls
import load as ld
import forces as ff
import calcs
import latex_report
import sphericalCoords  # Add import for spherical coordinates

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
        self.add_input_field(right_column, "Direction:", "direction", is_combo=True)
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
            if field_name == "side":
                field.addItems(["Front (F)", "Rear (R)", "Left (L)", "Aft (A)"])
            elif field_name == "direction":
                field.addItems(["R", "L"])
                field.currentTextChanged.connect(self.update_leaning_toward)
        else:
            field = QLineEdit()
            field.setValidator(QDoubleValidator())
        
        field.setFont(QFont('Arial', 10))
        field.setMinimumHeight(25)
        setattr(self, field_name, field)
        container_layout.addWidget(field)
        
        layout.addWidget(container)
    
    def update_leaning_toward(self, direction):
        self.leaningToward = direction
    
    def remove_self(self):
        self.deleteLater()

class LashingPositionInput(QFrame):
    def __init__(self, lashing_number, lashing_input):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.lashing_input = lashing_input  # Store reference to the lashing input
        
        layout = QHBoxLayout()
        
        # Add lashing number label
        number_label = QLabel(f"Lashing {lashing_number}")
        number_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(number_label)
        
        # Add original parameters
        params_label = QLabel(f"α: {lashing_input.alpha.text()}° β: {lashing_input.beta.text()}° "
                            f"BS: {lashing_input.breaking_strength.text()}kN Side: {lashing_input.side.currentText()} "
                            f"Direction: {lashing_input.direction.currentText()}")
        params_label.setFont(QFont('Arial', 10))
        layout.addWidget(params_label)
        
        # Add position input fields
        self.x = QLineEdit()
        self.y = QLineEdit()
        self.z = QLineEdit()
        
        # Set validators
        self.x.setValidator(QDoubleValidator())
        self.y.setValidator(QDoubleValidator())
        self.z.setValidator(QDoubleValidator())
        
        # Add labels and fields
        layout.addWidget(QLabel("X:"))
        layout.addWidget(self.x)
        layout.addWidget(QLabel("Y:"))
        layout.addWidget(self.y)
        layout.addWidget(QLabel("Z:"))
        layout.addWidget(self.z)
        
        self.setLayout(layout)
        
        # Connect textChanged signals to update loadPosition
        self.x.textChanged.connect(self.update_load_position)
        self.y.textChanged.connect(self.update_load_position)
        self.z.textChanged.connect(self.update_load_position)
    
    def update_load_position(self):
        try:
            x = float(self.x.text()) if self.x.text() else 0
            y = float(self.y.text()) if self.y.text() else 0
            z = float(self.z.text()) if self.z.text() else 0
            self.lashing_input.loadPosition = [x, y, z]
        except ValueError:
            pass

class SecondPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QHBoxLayout()  # Changed to horizontal layout like calculator page
        
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
        self.content_layout = QVBoxLayout(content_widget)
        
        # Add title
        title = QLabel("Lashing Positions")
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Add description
        desc = QLabel("Enter position coordinates for each lashing (in meters)")
        desc.setFont(QFont('Arial', 14))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(desc)
        
        # Create group box for lashing positions
        group = QGroupBox("Lashing Positions")
        group.setFont(QFont('Arial', 14))
        group_layout = QVBoxLayout()
        
        # Container for position inputs
        self.position_container = QWidget()
        self.position_layout = QVBoxLayout(self.position_container)
        group_layout.addWidget(self.position_container)
        
        group.setLayout(group_layout)
        self.content_layout.addWidget(group)
        
        # Add save button
        save_btn = QPushButton("Save Positions")
        save_btn.setFont(QFont('Arial', 14))
        save_btn.clicked.connect(self.save_positions)
        save_btn.setMinimumHeight(50)
        self.content_layout.addWidget(save_btn)
        
        # Add tipping analysis button
        tipping_btn = QPushButton("Tipping Analysis")
        tipping_btn.setFont(QFont('Arial', 14))
        tipping_btn.clicked.connect(self.perform_tipping_analysis)
        tipping_btn.setMinimumHeight(50)
        self.content_layout.addWidget(tipping_btn)
        
        # Add some spacing
        self.content_layout.addStretch()
        
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
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(right_widget, stretch=1)
        
        self.setLayout(layout)
        
        # Create position inputs for existing lashings
        self.update_lashing_positions()
        
        # Load the same image as calculator page
        self.load_image("pics/lashingPic.png")
    
    def load_image(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    350, 350,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Image not found")
        except Exception as e:
            self.image_label.setText(f"Error loading image: {str(e)}")
    
    def update_lashing_positions(self):
        # Clear existing position inputs
        for i in reversed(range(self.position_layout.count())):
            widget = self.position_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add position inputs for each lashing
        lashing_count = 0
        for i in range(self.main_window.lashing_layout.count()):
            widget = self.main_window.lashing_layout.itemAt(i).widget()
            if isinstance(widget, LashingInput):
                lashing_count += 1
                position_input = LashingPositionInput(lashing_count, widget)
                self.position_layout.addWidget(position_input)
        
        # Add stretch at the end
        self.position_layout.addStretch()
    
    def save_positions(self):
        positions = []
        for i in range(self.position_layout.count()):
            widget = self.position_layout.itemAt(i).widget()
            if isinstance(widget, LashingPositionInput):
                try:
                    x = float(widget.x.text()) if widget.x.text() else 0
                    y = float(widget.y.text()) if widget.y.text() else 0
                    z = float(widget.z.text()) if widget.z.text() else 0
                    widget.lashing_input.loadPosition = [x, y, z]
                    positions.append((x, y, z))
                except ValueError:
                    positions.append((0, 0, 0))
        
        # Here you can save the positions to a file or use them in calculations
        print("Saved positions:", positions)
    
    def perform_tipping_analysis(self):
        # Get the lashings list from the main window
        lashings = []
        for i in range(self.main_window.lashing_layout.count()):
            widget = self.main_window.lashing_layout.itemAt(i).widget()
            if isinstance(widget, LashingInput):
                try:
                    alpha = float(widget.alpha.text())
                    beta = float(widget.beta.text())
                    breaking_strength = float(widget.breaking_strength.text())
                    friction_coeff = float(self.main_window.friction_coeff.text())
                    side = widget.side.currentText()[0]  # Get first letter (F, R, L, A)
                    
                    # Create Lashing object
                    lashing = ls.Lashing(
                        alpha=alpha,
                        beta=beta,
                        BreakingStrength=breaking_strength,
                        FrictionCoefficient=friction_coeff,
                        RelativeSide=side,
                        LoadPosition=widget.loadPosition  # Use the stored position
                    )
                    lashings.append(lashing)
                except ValueError:
                    print('Value error')
        
        # Convert forces to spherical coordinates for each lashing
        for lashing in lashings:
            spherical_force = sphericalCoords.convertForceToSpherical(lashing)
            print(f"Lashing at position {lashing.LoadPosition} has spherical force: {spherical_force}")
        
        # Here you can perform tipping analysis with the lashings
        print("Tipping analysis with lashings:", lashings)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lashing Calculator")
        self.setMinimumSize(1400, 800)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.calculator_page = self.create_calculator_page()
        self.second_page = SecondPage(self)  # Pass self to access lashing_layout
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.calculator_page)
        self.stacked_widget.addWidget(self.second_page)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Load initial image
        self.load_image("pics/lashingPic.png")
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Create File menu
        file_menu = menubar.addMenu('File')
        
        # Add actions to switch pages
        calculator_action = QAction('Calculator', self)
        calculator_action.triggered.connect(self.switch_to_calculator)
        file_menu.addAction(calculator_action)
        
        positions_action = QAction('Lashing Positions', self)
        positions_action.triggered.connect(self.switch_to_positions)
        file_menu.addAction(positions_action)
    
    def switch_to_calculator(self):
        self.stacked_widget.setCurrentWidget(self.calculator_page)
    
    def switch_to_positions(self):
        # Update position inputs when switching to positions page
        self.second_page.update_lashing_positions()
        self.stacked_widget.setCurrentWidget(self.second_page)
    
    def create_calculator_page(self):
        # Create widget for calculator page
        calculator_page = QWidget()
        layout = QHBoxLayout(calculator_page)
        
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
        content_layout = QVBoxLayout(content_widget)
        
        # Add title
        title = QLabel("Lashing Calculator")
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        # Add input sections
        self.create_load_section(content_layout)
        self.create_environment_section(content_layout)
        self.create_lashing_section(content_layout)
        
        # Add calculate button
        calculate_btn = QPushButton("Calculate")
        calculate_btn.setFont(QFont('Arial', 14))
        calculate_btn.clicked.connect(self.calculate)
        calculate_btn.setMinimumHeight(50)
        content_layout.addWidget(calculate_btn)
        
        # Add result display
        self.result_label = QLabel("")
        self.result_label.setFont(QFont('Arial', 16))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        content_layout.addWidget(self.result_label)
        
        # Add some spacing
        content_layout.addStretch()
        
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
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(right_widget, stretch=1)
        
        return calculator_page
    
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