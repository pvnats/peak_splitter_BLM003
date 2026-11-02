import pandas as pd
from re import search
from tkinter import *
from tkinter import filedialog

"""
Peak splitter by pvnats
Finds and separates signal peaks 
from a single line raw data 
obtained by a BLM003 bioluminometer
"""

class Peaks:
    def __init__(self):
        self.data_dict = {}
        self.start_value = 100
        self.terminal_value = 0
        self.input_filename = ''
        self.output_filename = ''
    
    def set_value(self, start_value, terminal_value):
        self.start_value = int(start_value)
        self.terminal_value = int(terminal_value)       
    
    def set_filename(self, filepath):
        self.input_filename = filepath
        self.output_filename = filepath.split('/')[-1][:-4] + '_output'
             
    def convert_data(self):  
        """Finds and separates signal peaks. Adds time interavals"""
        
        with open(self.input_filename, "r", encoding="ANSI") as input_file:
            
            temp_data_dict = {'time': []}
        
            # Finds time intervals in log info 
            for _ in range(10):
                curr_digit = input_file.readline().strip()
                time_match = search(r'Частота отсчетов:\s+\d{1,3}$', curr_digit)
                if time_match:
                    digit = search(r'\d{1,3}', curr_digit)
                    time_counter = int(digit.group())
                    break
        
            # Columns counter
            counter = 1
            
            # A flag for starting to record values ​​into a column when a 'start_value' is reached.
            start_flag = False
        
            # A flag for finishing to record values ​​into a column when a 'terminal_value' is reached. 
            terminal_flag = True
        
            # Line-by-line data analysis to find and separate peaks    
            while True:
                next_digit = input_file.readline().strip()
                # Stops the cycle when the file ends
                if not next_digit:
                    break
            
                # Skips lines containing information from the log
                if curr_digit[0] == '/':  
                    curr_digit = next_digit
                    continue
            
                # Finds the column 'separator' (by default, the digit 0)
                # By default the system records the '0' signal at the time of samples changing
                if int(curr_digit) == 0:
                    # Switch off the start record because of '0'
                    start_flag = False
                
                    # Switch on the terminal flag to prepare for the next column(peak) data set
                    terminal_flag = True
                
                    # If current digit == 'separator' and next digit == 'separator', go to next step 
                    if int(next_digit) == 0:
                        curr_digit = next_digit
                        continue
                    # If current digit == 'separator' and next digit == signal data ( > 'separator), change the counter           
                    elif int(next_digit) > 0:
                        counter += 1                
                        curr_digit = next_digit
                        continue
                    
                # If recording is on — meaning a 'start_value' was found in previous cycles, 
                # but the current value < 'terminal_value' in the current cycle
                # then switches off 'terminal_flag' and stops recording                
                if start_flag == True and int(curr_digit) <= self.terminal_value:
                    terminal_flag = False
            
                # switches on 'start_flag' if 'start_value'
                if int(curr_digit) >= self.start_value:
                    start_flag = True            
            
                # Работаем с цифровыми значениями, которые больше значения 'разделителя'
                if int(curr_digit) > 0:
                    # если флаг начала записи и окончания записи включены
                    if start_flag == True  and terminal_flag == True:
                        # Задаем порядковый номер колонки
                        column_name = f'Column {counter}'
                        # Добавляем значения в словарь
                        temp_data_dict[column_name] = temp_data_dict.get(column_name, []) + [int(curr_digit)]
                        curr_digit = next_digit
                    # в противном случае уходим на следующий шаг
                    else:
                        curr_digit = next_digit
            
            # Добавляем в словарь последнее значение после остановки цикла
            if int(curr_digit) > 0 and start_flag == True and terminal_flag == True:
                temp_data_dict[column_name] = temp_data_dict.get(column_name, []) + [int(curr_digit)]
     
            # Вычисляем самую длинную колонку
            max_col_len = max([len(x) for x in temp_data_dict.values()])
        
            # Генерируем временные точки согласно использованному временному интервалу отсчета
            temp_data_dict['time'] = [i / time_counter for i in range(1, max_col_len + 1, 1)]
        
            # Выравниваем колонки с данными измерений по длине добавлением None
            for key in temp_data_dict.keys():
               temp_data_dict[key] = temp_data_dict.get(key, []) + [None] * (max_col_len - len(temp_data_dict[key]))
               
            self.data_dict = temp_data_dict
        
    def get_data(self):
        # Переводим сконвертированные данные в pd.DataFrame
        final_df = pd.DataFrame(self.data_dict)   
        
        return final_df


splitted_peaks = Peaks()        
    
def open_file():
    filepath = filedialog.askopenfilename(title="Open file", filetypes=(("BLM003_file (*.dat)", "*.dat"), ("All files", "*.*")))
    
    if filepath != "":
        # Кнопка Calculate становится активной
        btn_calc.config(state="normal", cursor="hand2")
            
        splitted_peaks.set_filename(filepath)
           
def save_file(data):  # Сохраняем выходные данные в csv файл
    # Задаем путь сохранения файла
    filepath = filedialog.asksaveasfilename(
        defaultextension="csv",
        initialfile=data.output_filename,
        filetypes=[("Comma Delimited", ".csv")],
    )
    
    # Сохраняем если путь задан корректно
    if filepath != "":
        data.get_data().to_csv(filepath, sep=',', index=False)
    

def start_calculation():    
    # Вызываем функцию конвертирования данных и сохраняем результат(словарь) в переменную
        
    splitted_peaks.set_value(start_value_entry.get(), terminal_value_entry.get())
    splitted_peaks.convert_data()
    save_file(splitted_peaks)   
    
    
root = Tk()
root.geometry("500x300+800+300")
root.title("Peak splitter for BLM003")

frame_title = Frame(root, width=400, height=50)
frame_title.pack()

title_l = Label(
    frame_title,
    text="Please enter a starting value:",
    font=("Arial", 14),
    height=2,
)
title_l.pack()

frame_start_entry = Frame(root, width=500, height=50)
frame_start_entry.pack()

start_value_entry = Entry(
    frame_start_entry,
    width=10,
    fg="black",
    font=("Arial", 14),
    justify=CENTER
)
start_value_entry.insert(0, 100)
start_value_entry.place(relx=0.40, rely=0.2)

frame_terminal_title = Frame(root, width=400, height=50)
frame_terminal_title.pack()

terminal_title_l = Label(
    frame_terminal_title,
    text="and a terminal value (default = 0):",
    font=("Arial", 14),
    height=2,
)
terminal_title_l.pack()

frame_terminal_entry = Frame(root, width=500, height=50)
frame_terminal_entry.pack()

terminal_value_entry = Entry(
    frame_terminal_entry,
    width=10,
    fg="black",
    font=("Arial", 14),
    justify=CENTER
)
terminal_value_entry.insert(0, 0)
terminal_value_entry.place(relx=0.40, rely=0.2)

frame_open = Frame(root, width=500, height=50)
frame_open.pack()

btn_open = Button(
    frame_open,
    text="Open File...",
    font=("Arial", 12),
    bg="lightgrey",
    command=open_file,
)
btn_open.place(width=150, height=30, relx=0.36, rely=0.2)

frame_calculate = Frame(root, width=500, height=50)
frame_calculate.pack()

btn_calc = Button(
    frame_calculate,
    text="Calculate",
    font=("Arial", 12),
    bg="lightgrey",
    cursor="hand2",
    state="disabled",
    command=start_calculation,
)
btn_calc.place(width=150, height=30, relx=0.36, rely=0.2)


root.mainloop()