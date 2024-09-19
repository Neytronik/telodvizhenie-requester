import os
import sys

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QCheckBox, QComboBox
)

from excel_processing import Composer
from logger import logger
from sheet_params import material_params, default_material


class ExcelApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Расчет заявок на раскрой')

        self.sheet_name = QComboBox(self)
        self.sheet_name.setEditable(True)
        self.sheet_name.addItems(material_params.keys())
        self.sheet_name.setCurrentText("Кулирка")
        self.sheet_name.currentTextChanged.connect(self.update_params)

        # Поля ввода
        self.param1 = QLineEdit(self)
        self.param2 = QLineEdit(self)
        self.param3 = QLineEdit(self)
        self.param4 = QLineEdit(self)

        self.file_input_name = QLineEdit(self)
        self.output_folder = QLineEdit(self)
        self.reverse_order = QCheckBox("Компоновать от большего к меньшему", self)

        # Кнопки
        select_file_btn = QPushButton('Выберите файл потребности', self)
        select_file_btn.setStyleSheet("""
                   QPushButton {
                       background-color: #E0FFFF;  
                       border: 1px solid black;   /* Черная граница */
                       border-radius: 2px;       /* Закругленные углы */
                       padding: 2px;             /* Внутренние отступы */
                   }
                   QPushButton:hover {
                       background-color: #008B8B;  /* Цвет фона при наведении */
                   }
               """)
        select_file_btn.clicked.connect(self.select_file)
        select_folder_btn = QPushButton('Выберите папку сохранения', self)
        select_folder_btn.setStyleSheet("""
                          QPushButton {
                              background-color: #E0FFFF;  
                              border: 1px solid black;   /* Черная граница */
                              border-radius: 2px;       /* Закругленные углы */
                              padding: 2px;             /* Внутренние отступы */
                          }
                          QPushButton:hover {
                              background-color: #008B8B;  /* Цвет фона при наведении */
                          }
                      """)
        select_folder_btn.clicked.connect(self.select_folder)
        process_btn = QPushButton('Расчитать', self)
        process_btn.setStyleSheet("""
                   QPushButton {
                       background-color: #32CD32;  /* Светло-зеленый цвет */
                       border: 1px solid black;   /* Черная граница */
                       border-radius: 5px;       /* Закругленные углы */
                       padding: 2px;             /* Внутренние отступы */
                   }
                   QPushButton:hover {
                       background-color: #006400;  /* Цвет фона при наведении */
                   }
               """)
        process_btn.clicked.connect(self.process_excel)
        exit_btn = QPushButton('Выход', self)
        exit_btn.setStyleSheet("""
                   QPushButton {
                       background-color: #B22222;  /* Светло-зеленый цвет */
                       border: 1px solid black;   /* Черная граница */
                       border-radius: 5px;       /* Закругленные углы */
                       padding: 2px;             /* Внутренние отступы */
                   }
                   QPushButton:hover {
                       background-color: #8B0000;  /* Цвет фона при наведении */
                   }
               """)
        exit_btn.clicked.connect(self.close)

        # Текстовое поле для вывода консоли
        logger.init_ui_console(self)
        self.console_output = logger.console_output

        # Layouts
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel('Название вкладки excel:'))
        input_layout.addWidget(self.sheet_name)
        input_layout.addWidget(QLabel('Минимальное количество слоев в заявке:'))
        input_layout.addWidget(self.param1)
        input_layout.addWidget(QLabel('Максимальное количество слоев в заявке:'))
        input_layout.addWidget(self.param2)
        input_layout.addWidget(QLabel('Минимальное количество секций для раскроя в заявке:'))
        input_layout.addWidget(self.param3)
        input_layout.addWidget(QLabel('Максимальное количество секций для раскроя в заявке:'))
        input_layout.addWidget(self.param4)

        input_layout.addWidget(select_file_btn)
        input_layout.addWidget(self.file_input_name)
        input_layout.addWidget(select_folder_btn)
        input_layout.addWidget(self.output_folder)
        input_layout.addWidget(self.reverse_order)
        input_layout.addWidget(process_btn)
        input_layout.addWidget(exit_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)

        # Создаем заголовок для текстового поля
        console_label = QLabel('Console Logs', self)

        # Создаем layout для заголовка и текстового поля
        console_layout = QVBoxLayout()
        console_layout.addWidget(console_label)
        console_layout.addWidget(self.console_output)
        main_layout.addLayout(console_layout)
        self.setLayout(main_layout)

        # Установить начальные значения параметров
        self.update_params(self.sheet_name.currentText())

    def update_params(self, material_name):
        material = material_params.get(material_name)
        if material:
            self.param1.setText(str(material.min_layers))
            self.param2.setText(str(material.max_layers))
            self.param3.setText(str(material.min_sections))
            self.param4.setText(str(material.max_sections))
        else:
            self.param1.setText(str(default_material.min_layers))
            self.param2.setText(str(default_material.max_layers))
            self.param3.setText(str(default_material.min_sections))
            self.param4.setText(str(default_material.max_sections))

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsb *.xlsx *.xls)")
        if file_path:
            self.file_input_name.setText(file_path)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder.setText(folder_path)

    def process_excel(self):
        file_input_name = self.file_input_name.text()
        sheet_name = self.sheet_name.currentText()
        output_folder = self.output_folder.text()
        reverse_order = self.reverse_order.isChecked()

        if not file_input_name or not sheet_name or not output_folder:
            QMessageBox.critical(self, "Error", "Пожалуйста заполните все поля")
            return

        try:
            logger.print("Reading Excel file...")
            # Прочитать файл Excel без пропуска строк
            df_initial = pd.read_excel(file_input_name, sheet_name=sheet_name, header=None)
            # Найти индекс строки, содержащей слово "Код"
            skiprows = \
                df_initial[df_initial.apply(lambda row: row.astype(str).str.contains('Код').any(), axis=1)].index[0]
            # Чтение данных из Excel файла
            df = pd.read_excel(file_input_name, skiprows=skiprows, sheet_name=sheet_name)
            # Переименовываем колонку "ЗАКАЗ" в "Количество" для удобства
            logger.print("Replace 'Надо' to 0")
            df = df.rename(columns={'ЗАКАЗ': 'Количество'}).replace("Надо", 0)
            # Приводим значения в столбце 'Артикул' к нижнему регистру
            logger.print("Update 'Артикул' to lower case")
            df['Артикул'] = df['Артикул'].str.lower()
            logger.print("Aggregating by 'Цвет', 'Артикул', 'Размер' by 'Количество': 'sum'")

            df = df.groupby(['Цвет', 'Артикул', 'Размер', ], as_index=False).agg({
                'Количество': 'sum',
            })
            logger.print("Filter by ['Количество'] > 0")
            df = df[df['Количество'] > 0]

            # Пример использования параметров и выполнения расчетов
            min_layers = int(self.param1.text())
            max_layers = int(self.param2.text())
            min_sections = int(self.param3.text())
            max_sections = int(self.param4.text())

            logger.print(
                f"Parameters: {sheet_name}"
                f"\n\tmin_layers:{min_layers}"
                f"\n\tmax_layers:{max_layers}"
                f"\n\tmin_sections:{min_sections}"
                f"\n\tmax_sections:{max_sections}")

            composer = Composer(min_layers, max_layers, min_sections, max_sections, reverse_order)

            orders = []
            base_path = f'{output_folder}/{sheet_name}'
            # Создаем все вложенные папки, если они не существуют
            if not os.path.exists(base_path):
                os.makedirs(base_path)

            # cохранили сгруппированный и отфильтрованный excel
            base_quantity_path = f'{base_path}/base_quantity.xlsx'
            logger.print(f"Saving base aggregated excel to '{base_quantity_path}'")
            with pd.ExcelWriter(base_quantity_path, engine='xlsxwriter') as writer:
                # Записываем DataFrame на соответствующий лист
                df.to_excel(writer, index=False)
            orders_path = f'{base_path}/orders.xlsx'
            remaining_path = f'{base_path}/remaining_items.xlsx'

            logger.print(f'Старт обработки файла...')
            while True:
                df_selected_items, remaining_df = composer.selector_composer(df)
                # Преобразуем в заявку
                layers, remaining_df = composer.slice_layers(df_selected_items, remaining_df)
                df = remaining_df
                if len(layers) == 0:
                    logger.print(f'Запись созданных заявок: {orders_path}')
                    composer.save_orders_to_excel(orders, file_path=orders_path)
                    logger.print(f'Запись заявок завершена!')

                    logger.print(f'Запись остатков: {remaining_path}')
                    with pd.ExcelWriter(remaining_path, engine='xlsxwriter') as writer:
                        # Записываем DataFrame на соответствующий лист
                        remaining_df.to_excel(writer, index=False)
                        logger.print(f'Запись остатков завершена!')

                    break
                order = composer.create_order(layers)
                orders.append(order)
            QMessageBox.information(self, "Success", f"File processed and saved to {f'{output_folder}/{sheet_name}'}")

        except Exception as e:
            logger.print(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelApp()
    window.show()
    sys.exit(app.exec_())
