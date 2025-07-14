import sys
import os
import subprocess

def install_missing_packages():
    required_packages = {
        'PyQt6': 'PyQt6'
    }
    
    missing_packages = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Установка недостающих модулей: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при установке {package}: {e}")
                sys.exit(1)
        print("Модули успешно установлены. Перезапустите программу.")
        sys.exit(0)

# Проверяем и устанавливаем модули до всех остальных импортов
if not hasattr(sys, 'frozen'):
    install_missing_packages()

# Теперь импортируем все остальные модули
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider,
    QPushButton, QLineEdit, QGridLayout, QStyle, QStyleOptionSlider,
    QMessageBox
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QFont, QColor, QIcon


def resource_path(relative_path):
    """Позволяет находить файл как при запуске из IDE, так и из .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def calculate_flavour_volume(base_volume_ml, flavour_percent):
    flavour_volume_ml = (flavour_percent / 100 * base_volume_ml) / (1 - (flavour_percent / 100))
    total_volume = base_volume_ml + flavour_volume_ml
    return {
        "Объём базы (мл)": round(base_volume_ml, 2),
        "Объём ароматизатора (мл)": round(flavour_volume_ml, 2),
        "Итоговый объём жидкости (мл)": round(total_volume, 2)
    }


class TickSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None, tick_values=None):
        super().__init__(orientation, parent)
        self.tick_values = tick_values or []

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.tick_values:
            return

        painter = QPainter(self)
        painter.setPen(QColor("#50fa7b"))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)

        for v in self.tick_values:
            range_span = self.maximum() - self.minimum()
            if range_span == 0:
                continue
            x = groove.left() + int((v - self.minimum()) / range_span * groove.width())
            y = groove.bottom() + 15
            text = str(v)
            text_rect = painter.boundingRect(QRect(), Qt.AlignmentFlag.AlignCenter, text)
            painter.drawText(x - text_rect.width() // 2, y + text_rect.height(), text)
        painter.end()


class VapeCalcApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("app_icon.ico")))
        self.setWindowTitle("Калькулятор ароматизатора - Vape DIY")
        self.setFixedSize(680, 470)
        self.setStyleSheet("""
            QWidget {
                background-color: #12131a;
                color: #cbd5e1;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLabel#title {
                font-size: 18pt;
                font-weight: 700;
                color: #21d07a;
                margin-bottom: 10px;
            }
            QLabel {
                font-size: 13pt;
            }
            QLineEdit {
                background: #1e213a;
                border: 1px solid #21d07a;
                border-radius: 6px;
                padding: 5px 10px;
                color: #e0e6f7;
                font-size: 14pt;
                qproperty-alignment: AlignCenter;
                min-width: 70px;
                max-width: 80px;
            }
            QPushButton {
                background-color: #21d07a;
                border-radius: 8px;
                padding: 12px;
                font-weight: 700;
                font-size: 16pt;
                color: #12131a;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #1aae5b;
            }
            QLabel#result {
                background-color: #1e213a;
                border-radius: 12px;
                padding: 20px;
                font-size: 14pt;
                color: #d1d9ff;
                margin-top: 20px;
                min-height: 90px;
                font-weight: 600;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Калькулятор ароматизатора (по итоговому объёму)")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(20)

        label_base = QLabel("Объём базы (мл):")
        self.slider_base = TickSlider(Qt.Orientation.Horizontal, tick_values=list(range(10, 101, 10)))
        self.slider_base.setMinimum(10)
        self.slider_base.setMaximum(100)
        self.slider_base.setSingleStep(10)
        self.slider_base.setValue(30)
        self.slider_base.valueChanged.connect(self.sync_base_line_edit)

        self.line_base = QLineEdit("30")
        self.line_base.editingFinished.connect(self.sync_base_slider)

        grid.addWidget(label_base, 0, 0)
        grid.addWidget(self.slider_base, 0, 1)
        grid.addWidget(self.line_base, 0, 2)

        label_flavour = QLabel("Ароматизатор (%):")
        self.slider_flavour = TickSlider(Qt.Orientation.Horizontal, tick_values=list(range(1, 31)))
        self.slider_flavour.setMinimum(1)
        self.slider_flavour.setMaximum(30)
        self.slider_flavour.setSingleStep(1)
        self.slider_flavour.setValue(5)
        self.slider_flavour.valueChanged.connect(self.sync_flavour_line_edit)

        self.line_flavour = QLineEdit("5")
        self.line_flavour.editingFinished.connect(self.sync_flavour_slider)

        grid.addWidget(label_flavour, 1, 0)
        grid.addWidget(self.slider_flavour, 1, 1)
        grid.addWidget(self.line_flavour, 1, 2)

        layout.addLayout(grid)

        btn_calc = QPushButton("Рассчитать")
        btn_calc.clicked.connect(self.calculate)
        layout.addWidget(btn_calc)

        self.label_result = QLabel("")
        self.label_result.setObjectName("result")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_result.setWordWrap(True)
        layout.addWidget(self.label_result)

        self.setLayout(layout)

    def sync_base_line_edit(self):
        self.line_base.setText(str(self.slider_base.value()))

    def sync_base_slider(self):
        try:
            val = int(self.line_base.text())
            if val not in range(10, 101, 10):
                raise ValueError
            self.slider_base.setValue(val)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный объём базы (10, 20, ..., 100 мл)")
            self.line_base.setText(str(self.slider_base.value()))

    def sync_flavour_line_edit(self):
        self.line_flavour.setText(str(self.slider_flavour.value()))

    def sync_flavour_slider(self):
        try:
            val = int(self.line_flavour.text())
            if val not in range(1, 31):
                raise ValueError
            self.slider_flavour.setValue(val)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный процент ароматизатора (1-30%)")
            self.line_flavour.setText(str(self.slider_flavour.value()))

    def calculate(self):
        try:
            base_volume = float(self.line_base.text())
            flavour_percent = float(self.line_flavour.text())
            result = calculate_flavour_volume(base_volume, flavour_percent)
            res_text = (
                f"Объём базы: {result['Объём базы (мл)']} мл\n"
                f"Ароматизатор: {result['Объём ароматизатора (мл)']} мл\n"
                f"Итоговый объём: {result['Итоговый объём жидкости (мл)']} мл"
            )
            self.label_result.setText(res_text)
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при расчёте. Проверьте введённые данные.")


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("app_icon.ico")))
    window = VapeCalcApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()