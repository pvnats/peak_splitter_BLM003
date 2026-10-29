import pandas as pd
from re import search
from tkinter import *
from tkinter import filedialog


def convert_data():  # Конвертируем сырые данные с добавлением временных интервалов
    
    with open(input_filename, "r", encoding="ANSI") as input_file:
        
        # Ищем использованную частоту отсчетов (временные интервалы) 
        for _ in range(10):
            prev_digit = input_file.readline().strip()
            time_match = search(r'Частота отсчетов:\s+\d{1,3}$', prev_digit)
            if time_match:
                digit = search(r'\d{1,3}', prev_digit)
                time_counter = int(digit.group())
                break
        
        # Создаем словарь данных, который будет содержать временные интервалы и значения измерений
        data_dict = {'time': []}
        
        # Задаем счетчик для разделения данных измерений на колонки
        counter = 1
                
        # Считываем стартовое значение записи данных
        start_value = int(start_value_entry.get())
        # Флаг начала записи значений в колонку при достижении заданного start_value
        start_flag = False
        
        # Считываем значение остановки записи данных
        terminal_value = int(terminal_value_entry.get())
        # Флаг окончания записи значений в колонку при достижении заданного terminal_value
        terminal_flag = True
        
        # Анализируем файл в поиске цифровых значений и разбиваем их на отдельные колонки    
        while True:
            next_digit = input_file.readline().strip()
            # Определяем конец файла и останавливаем цикл
            if not next_digit:
                break
            
            # Игнорируем строчки, содержащие вспомогательную информацию
            if prev_digit[0] == '/':  
                prev_digit = next_digit
                continue
            
            # Находим цифровые значения и работаем с 'разделителем' колонок (по умолчанию цифра 0)
            if int(prev_digit) == 0:
                # отключаем флаг так как обнаружен 0
                start_flag = False
                
                # включаем терминальный флаг записи, так как начинается следующая колонка
                terminal_flag = True
                
                # если текущее значение и следующее значение == разделитель, идем на следующий шаг 
                if int(next_digit) == 0:
                    prev_digit = next_digit
                    continue
                # если текущее значение разделитель, а следующее - данные, то  изменяем счетчик           
                elif int(next_digit) > 0:
                    counter += 1                
                    prev_digit = next_digit
                    continue
            
            # Если запись включена, т.е. на предыдущих циклах было найдено start_value,
            # но на текущем цикле обнаружено значение ниже terminal_value
            # то выключаем флаг и останавливаем запись
            if start_flag == True and int(prev_digit) <= terminal_value:
                terminal_flag = False
            
            # Переключаем флаг на запись при обнаружении start_value
            if int(prev_digit) >= start_value:
                start_flag = True            
            
            # Работаем с цифровыми значениями, которые больше значения 'разделителя'
            if int(prev_digit) > 0:
                # если флаг начала записи и окончания записи включены
                if start_flag == True  and terminal_flag == True:
                    # Задаем порядковый номер колонки
                    column_name = f'Column {counter}'
                    # Добавляем значения в словарь
                    data_dict[column_name] = data_dict.get(column_name, []) + [int(prev_digit)]
                    prev_digit = next_digit
                # в противном случае уходим на следующий шаг
                else:
                    prev_digit = next_digit
            
        # Добавляем в словарь последнее значение после остановки цикла
        if int(prev_digit) > 0 and start_flag == True and terminal_flag == True:
            data_dict[column_name] = data_dict.get(column_name, []) + [int(prev_digit)]
        
        # Вычисляем самую длинную колонку
        max_col_len = max([len(x) for x in data_dict.values()])
        
        # Генерируем временные точки согласно использованному временному интервалу отсчета
        data_dict['time'] = [i / time_counter for i in range(1, max_col_len + 1, 1)]
        
        # Выравниваем колонки с данными измерений по длине добавлением None
        for key in data_dict.keys():
           data_dict[key] = data_dict.get(key, []) + [None] * (max_col_len - len(data_dict[key]))
        
        # Переводим сконвертированные данные в pd.DataFrame
        final_df = pd.DataFrame(data_dict)   
        
        return final_df
    
def open_file():
    global input_filename
    global output_filename
    file_path = filedialog.askopenfilename(title="Open file", filetypes=(("BLM003_file (*.dat)", "*.dat"), ("All files", "*.*")))
    
    if file_path != "":
        input_filename = file_path
        output_filename = file_path.split('/')[-1][:-4]
        
        # Кнопка Calculate становится активной
        btn_calc.config(state="normal", cursor="hand2")
    
def save_file(final_df):  # Сохраняем выходные данные в csv файл
    # Задаем путь сохранения файла
    filepath = filedialog.asksaveasfilename(
        defaultextension="csv",
        initialfile=output_filename,
        filetypes=[("Comma Delimited", ".csv")],
    )
    
    # Сохраняем если путь задан корректно
    if filepath != "":
        final_df.to_csv(filepath, sep=',', index=False)

def start_calculation():    
    # Вызываем функцию конвертирования данных и сохраняем результат(словарь) в переменную
    final_df = convert_data()
    save_file(final_df)     
    


input_filename = "C:/"
output_filename = "new.csv"
 
    
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
