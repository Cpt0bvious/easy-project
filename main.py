import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
import csv
import logging
import bd

# Настройка логирования
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class App:
    def __init__(self, root, db_user, db_password):
        self.root = root
        self.db_user = db_user
        self.db_password = db_password
        self.user_role = None
        self.s = None  # Данные квартир
        self.l = None  # Данные пользователей

        # Настройка окна
        self.root.title("Оценка стоимости квартиры")
        x, y = (root.winfo_screenwidth() // 2) - (800 // 2), (root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"{800}x{600}+{x}+{y}")
        self.root.configure(bg="#71C9CE")

        # Стили
        style = ttk.Style()
        style.configure("TLabel", font="helvetica 13", padding=5, background="#71C9CE", foreground="#000000")
        style.configure("TButton", font="helvetica 10", padding=5)
        style.configure("TEntry", font="helvetica 12", padding=5)

        # Инициализация экрана логина
        self.setup_login_screen()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def setup_login_screen(self):
        self.frame = tk.Frame(self.root, bg="#71C9CE")
        self.frame.pack(expand=True, fill="both")

        ttk.Label(self.frame, text="Логин:").grid(row=0, column=0, padx=10, pady=5)
        self.entry1 = ttk.Entry(self.frame)
        self.entry1.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.frame, text="Пароль:").grid(row=1, column=0, padx=10, pady=5)
        self.entry2 = ttk.Entry(self.frame, show="*")
        self.entry2.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(self.frame, text="Войти", command=self.button1_click).grid(row=2, column=1, pady=10)
        ttk.Button(self.frame, text="Зарегистрироваться", command=self.button2_click).grid(row=3, column=1, pady=10)

    def setup_register_screen(self):
        self.clear_frame(self.frame)

        ttk.Label(self.frame, text="Придумайте логин:").grid(row=0, column=0, padx=10, pady=5)
        self.ent1 = ttk.Entry(self.frame)
        self.ent1.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.frame, text="Придумайте пароль:").grid(row=1, column=0, padx=10, pady=5)
        self.ent2 = ttk.Entry(self.frame, show="*")
        self.ent2.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.frame, text="Подтвердите пароль:").grid(row=2, column=0, padx=10, pady=5)
        self.ent3 = ttk.Entry(self.frame, show="*")
        self.ent3.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(self.frame, text="Подтвердить", command=self.button3_click).grid(row=3, column=1, pady=10)
        ttk.Button(self.frame, text="Назад", command=self.setup_login_screen).grid(row=4, column=1, pady=10)

    def setup_main_screen(self):
        self.clear_frame(self.frame)
        self.frame.pack_forget()

        self.frame = tk.Frame(self.root, bg="#71C9CE")
        self.frame.pack(expand=True, fill="both")

        # Таблица
        columns = ("ID", "Площадь", "Кол-во комнат", "Адрес", "Этаж", "Состояние", "Расстояние до центра")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        self.tree.heading("ID", text="ID", anchor="w", command=lambda: self.sort(0, False, int))
        self.tree.heading("Площадь", text="Площадь", anchor="w", command=lambda: self.sort(1, False, float))
        self.tree.heading("Кол-во комнат", text="Кол-во комнат", anchor="w", command=lambda: self.sort(2, False, int))
        self.tree.heading("Адрес", text="Адрес", anchor="w", command=lambda: self.sort(3, False, str))
        self.tree.heading("Этаж", text="Этаж", anchor="w", command=lambda: self.sort(4, False, int))
        self.tree.heading("Состояние", text="Состояние", anchor="w", command=lambda: self.sort(5, False, str))
        self.tree.heading("Расстояние до центра", text="Расстояние до центра", anchor="w", command=lambda: self.sort(6, False, float))
        self.tree.column("ID", width=50)
        self.tree.column("Площадь", width=60)
        self.tree.column("Кол-во комнат", width=100)
        self.tree.column("Адрес", width=150)
        self.tree.column("Этаж", width=60)
        self.tree.column("Состояние", width=100)
        self.tree.column("Расстояние до центра", width=150)

        # Панель кнопок
        self.button_frame = tk.Frame(self.frame, bg="#71C9CE")
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Button(self.button_frame, text="Поиск", command=self.search_apartments).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="Сбросить поиск", command=self.refresh_table).grid(row=0, column=1, padx=5)
        ttk.Button(self.button_frame, text="Экспорт в CSV", command=self.export_to_csv).grid(row=0, column=2, padx=5)
        ttk.Button(self.button_frame, text="Оценить стоимость", command=self.evaluate_apartment).grid(row=0, column=3, padx=5)

        if self.user_role == 'admin':
            ttk.Button(self.button_frame, text="Добавить квартиру", command=self.create_add_window).grid(row=0, column=4, padx=5)
            ttk.Button(self.button_frame, text="Удалить квартиру", command=self.delete_apartment).grid(row=0, column=5, padx=5)
            self.tree.bind("<Double-1>", self.edit_apartment)
            self.tree.bind("<Delete>", lambda event: self.delete_apartment())

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        self.refresh_table()

    def sort(self, col, reverse, key):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children()]
        items.sort(reverse=reverse, key=lambda t: key(t[0]))
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort(col, not reverse, key))

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        self.s, self.l = bd.connection_(self.db_password, self.db_user)
        if self.s is None:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {self.l}")
            return
        for apartment in self.s:
            self.tree.insert("", "end", values=apartment)

    def create_add_window(self):
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"{500}x{400}+{x}+{y}")
        self.window.title("Добавить квартиру")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь (м²):").grid(row=0, column=0, padx=10, pady=5)
        self.entr1 = ttk.Entry(window_frame)
        self.entr1.grid(row=0, column=1, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr2 = ttk.Entry(window_frame)
        self.entr2.grid(row=1, column=1, pady=5)

        ttk.Label(window_frame, text="Адрес:").grid(row=2, column=0, padx=10, pady=5)
        self.entr3 = ttk.Entry(window_frame)
        self.entr3.grid(row=2, column=1, pady=5)

        ttk.Label(window_frame, text="Этаж:").grid(row=3, column=0, padx=10, pady=5)
        self.entr4 = ttk.Entry(window_frame)
        self.entr4.grid(row=3, column=1, pady=5)

        ttk.Label(window_frame, text="Состояние:").grid(row=4, column=0, padx=10, pady=5)
        self.entr5 = ttk.Combobox(window_frame, values=["poor", "average", "good"])
        self.entr5.grid(row=4, column=1, pady=5)

        ttk.Label(window_frame, text="Расстояние до центра (км):").grid(row=5, column=0, padx=10, pady=5)
        self.entr6 = ttk.Entry(window_frame)
        self.entr6.grid(row=5, column=1, pady=5)

        ttk.Button(window_frame, text="Добавить", command=self.button4_click).grid(row=6, column=0, columnspan=2, pady=10)

    def search_apartments(self):
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"{500}x{400}+{x}+{y}")
        self.window.title("Поиск квартир")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь (мин, м²):").grid(row=0, column=0, padx=10, pady=5)
        self.entr_area_min = ttk.Entry(window_frame)
        self.entr_area_min.grid(row=0, column=1, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr_rooms = ttk.Entry(window_frame)
        self.entr_rooms.grid(row=1, column=1, pady=5)

        ttk.Label(window_frame, text="Адрес (часть):").grid(row=2, column=0, padx=10, pady=5)
        self.entr_address = ttk.Entry(window_frame)
        self.entr_address.grid(row=2, column=1, pady=5)

        ttk.Label(window_frame, text="Этаж (мин):").grid(row=3, column=0, padx=10, pady=5)
        self.entr_floor_min = ttk.Entry(window_frame)
        self.entr_floor_min.grid(row=3, column=1, pady=5)

        ttk.Label(window_frame, text="Состояние:").grid(row=4, column=0, padx=10, pady=5)
        self.entr_sost = ttk.Combobox(window_frame, values=["", "poor", "average", "good"])
        self.entr_sost.grid(row=4, column=1, pady=5)

        ttk.Label(window_frame, text="Расстояние до центра (макс, км):").grid(row=5, column=0, padx=10, pady=5)
        self.entr_distance_max = ttk.Entry(window_frame)
        self.entr_distance_max.grid(row=5, column=1, pady=5)

        ttk.Button(window_frame, text="Поиск", command=self.search).grid(row=6, column=0, columnspan=2, pady=10)

    def search(self):
        try:
            area_min = self.entr_area_min.get().strip()
            rooms = self.entr_rooms.get().strip()
            address_part = self.entr_address.get().strip().lower()
            floor_min = self.entr_floor_min.get().strip()
            sost = self.entr_sost.get().strip()
            distance_max = self.entr_distance_max.get().strip()

            filtered_apartments = []
            for apartment in self.s:
                if area_min and float(apartment[1]) < float(area_min):
                    continue
                if rooms and int(apartment[2]) != int(rooms):
                    continue
                if address_part and address_part not in apartment[3].lower():
                    continue
                if floor_min and int(apartment[4]) < int(floor_min):
                    continue
                if sost and apartment[5] != sost:
                    continue
                if distance_max and float(apartment[6]) > float(distance_max):
                    continue
                filtered_apartments.append(apartment)

            self.tree.delete(*self.tree.get_children())
            for apartment in filtered_apartments:
                self.tree.insert("", "end", values=apartment)
            self.window.destroy()
        except ValueError:
            messagebox.showwarning("Ошибка", "Проверьте формат данных!")

    def evaluate_apartment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите квартиру для оценки")
            return

        self.eval_window = tk.Toplevel(self.root)
        x, y = (self.eval_window.winfo_screenwidth() // 2) - (600 // 2), (self.eval_window.winfo_screenheight() // 2) - (600 // 2)
        self.eval_window.geometry(f"{600}x{600}+{x}+{y}")
        self.eval_window.title("Оценка стоимости квартиры")
        self.eval_window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.eval_window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        # Сравнительный подход
        ttk.Label(window_frame, text="Сравнительный подход: Аналоги").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(window_frame, text="Стоимость (аналог 1, руб):").grid(row=1, column=0, padx=5)
        self.entr_comp_price1 = ttk.Entry(window_frame)
        self.entr_comp_price1.grid(row=1, column=1, pady=2)
        ttk.Label(window_frame, text="Площадь (аналог 1, м²):").grid(row=2, column=0, padx=5)
        self.entr_comp_area1 = ttk.Entry(window_frame)
        self.entr_comp_area1.grid(row=2, column=1, pady=2)
        ttk.Label(window_frame, text="Состояние (аналог 1):").grid(row=3, column=0, padx=5)
        self.entr_comp_sost1 = ttk.Combobox(window_frame, values=["poor", "average", "good"])
        self.entr_comp_sost1.grid(row=3, column=1, pady=2)
        ttk.Label(window_frame, text="Этаж (аналог 1):").grid(row=4, column=0, padx=5)
        self.entr_comp_floor1 = ttk.Entry(window_frame)
        self.entr_comp_floor1.grid(row=4, column=1, pady=2)
        ttk.Label(window_frame, text="Стоимость (аналог 2, руб):").grid(row=5, column=0, padx=5)
        self.entr_comp_price2 = ttk.Entry(window_frame)
        self.entr_comp_price2.grid(row=5, column=1, pady=2)
        ttk.Label(window_frame, text="Площадь (аналог 2, м²):").grid(row=6, column=0, padx=5)
        self.entr_comp_area2 = ttk.Entry(window_frame)
        self.entr_comp_area2.grid(row=6, column=1, pady=2)
        ttk.Label(window_frame, text="Состояние (аналог 2):").grid(row=7, column=0, padx=5)
        self.entr_comp_sost2 = ttk.Combobox(window_frame, values=["poor", "average", "good"])
        self.entr_comp_sost2.grid(row=7, column=1, pady=2)
        ttk.Label(window_frame, text="Этаж (аналог 2):").grid(row=8, column=0, padx=5)
        self.entr_comp_floor2 = ttk.Entry(window_frame)
        self.entr_comp_floor2.grid(row=8, column=1, pady=2)

        # Затратный подход
        ttk.Label(window_frame, text="Затратный подход").grid(row=9, column=0, columnspan=2, pady=5)
        ttk.Label(window_frame, text="Стоимость строительства (руб/м²):").grid(row=10, column=0, padx=5)
        self.entr_cost_build = ttk.Entry(window_frame)
        self.entr_cost_build.grid(row=10, column=1, pady=2)
        ttk.Label(window_frame, text="Год постройки:").grid(row=11, column=0, padx=5)
        self.entr_cost_year = ttk.Entry(window_frame)
        self.entr_cost_year.grid(row=11, column=1, pady=2)
        ttk.Label(window_frame, text="Стоимость земли (руб):").grid(row=12, column=0, padx=5)
        self.entr_cost_land = ttk.Entry(window_frame)
        self.entr_cost_land.grid(row=12, column=1, pady=2)

        # Доходный подход
        ttk.Label(window_frame, text="Доходный подход").grid(row=13, column=0, columnspan=2, pady=5)
        ttk.Label(window_frame, text="Арендная ставка (руб/м²/мес):").grid(row=14, column=0, padx=5)
        self.entr_inc_rent = ttk.Entry(window_frame)
        self.entr_inc_rent.grid(row=14, column=1, pady=2)
        ttk.Label(window_frame, text="Ставка капитализации (%):").grid(row=15, column=0, padx=5)
        self.entr_inc_cap = ttk.Entry(window_frame)
        self.entr_inc_cap.grid(row=15, column=1, pady=2)

        ttk.Button(window_frame, text="Рассчитать", command=lambda: self.calculate_cost(selected_item)).grid(row=16, column=0, columnspan=2, pady=10)

    def calculate_cost(self, selected_item):
        apartment_data = self.tree.item(selected_item)["values"]
        area = float(apartment_data[1])
        floor = int(apartment_data[4])
        sost = apartment_data[5]

        try:
            # Сравнительный подход
            price1 = float(self.entr_comp_price1.get())
            area1 = float(self.entr_comp_area1.get())
            sost1 = self.entr_comp_sost1.get()
            floor1 = int(self.entr_comp_floor1.get())
            price2 = float(self.entr_comp_price2.get())
            area2 = float(self.entr_comp_area2.get())
            sost2 = self.entr_comp_sost2.get()
            floor2 = int(self.entr_comp_floor2.get())
            price_per_m2_1 = price1 / area1
            price_per_m2_2 = price2 / area2
            avg_price_per_m2 = (price_per_m2_1 + price_per_m2_2) / 2
            correction = 1.0
            if sost == "good" and sost1 == "average":
                correction *= 1.05
            elif sost == "poor" and sost1 == "average":
                correction *= 0.95
            if sost == "good" and sost2 == "average":
                correction *= 1.05
            elif sost == "poor" and sost2 == "average":
                correction *= 0.95
            if floor <= 2 and floor1 > 2:
                correction *= 0.95
            elif floor > 2 and floor1 <= 2:
                correction *= 1.05
            if floor <= 2 and floor2 > 2:
                correction *= 0.95
            elif floor > 2 and floor2 <= 2:
                correction *= 1.05
            comp_cost = avg_price_per_m2 * area * correction

            # Затратный подход
            build_cost_per_m2 = float(self.entr_cost_build.get())
            year_built = int(self.entr_cost_year.get())
            land_cost = float(self.entr_cost_land.get())
            wear = min((2025 - year_built) * 0.01, 0.5)  # 1% износа в год, макс 50%
            cost_cost = (build_cost_per_m2 * area * (1 - wear)) + land_cost

            # Доходный подход
            rent_per_m2 = float(self.entr_inc_rent.get())
            cap_rate = float(self.entr_inc_cap.get()) / 100
            annual_income = rent_per_m2 * area * 12
            inc_cost = annual_income / cap_rate

            # Комбинированная оценка
            final_cost = (comp_cost * 0.5) + (inc_cost * 0.3) + (cost_cost * 0.2)

            # Вывод результатов
            messagebox.showinfo(
                "Результат оценки",
                f"Сравнительный подход: {comp_cost:,.0f} руб.\n"
                f"Затратный подход: {cost_cost:,.0f} руб.\n"
                f"Доходный подход: {inc_cost:,.0f} руб.\n"
                f"Итоговая стоимость: {final_cost:,.0f} руб."
            )
            self.eval_window.destroy()
        except ValueError:
            messagebox.showwarning("Ошибка", "Проверьте формат данных!")

    def edit_apartment(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        apartment_data = self.tree.item(selected_item)["values"]
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"{500}x{400}+{x}+{y}")
        self.window.title("Редактировать квартиру")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь (м²):").grid(row=0, column=0, padx=10, pady=5)
        self.entr_edit_area1 = ttk.Entry(window_frame)
        self.entr_edit_area1.insert(0, apartment_data[1])
        self.entr_edit_area1.grid(row=0, column=1, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr_edit_area2 = ttk.Entry(window_frame)
        self.entr_edit_area2.insert(0, apartment_data[2])
        self.entr_edit_area2.grid(row=1, column=1, pady=5)

        ttk.Label(window_frame, text="Адрес:").grid(row=2, column=0, padx=10, pady=5)
        self.entr_edit_area3 = ttk.Entry(window_frame)
        self.entr_edit_area3.insert(0, apartment_data[3])
        self.entr_edit_area3.grid(row=2, column=1, pady=5)

        ttk.Label(window_frame, text="Этаж:").grid(row=3, column=0, padx=10, pady=5)
        self.entr_edit_area4 = ttk.Entry(window_frame)
        self.entr_edit_area4.insert(0, apartment_data[4])
        self.entr_edit_area4.grid(row=3, column=1, pady=5)

        ttk.Label(window_frame, text="Состояние:").grid(row=4, column=0, padx=10, pady=5)
        self.entr_edit_area5 = ttk.Combobox(window_frame, values=["poor", "average", "good"])
        self.entr_edit_area5.insert(0, apartment_data[5])
        self.entr_edit_area5.grid(row=4, column=1, pady=5)

        ttk.Label(window_frame, text="Расстояние до центра (км):").grid(row=5, column=0, padx=10, pady=5)
        self.entr_edit_area6 = ttk.Entry(window_frame)
        self.entr_edit_area6.insert(0, apartment_data[6])
        self.entr_edit_area6.grid(row=5, column=1, pady=5)

        ttk.Button(window_frame, text="Подтвердить", command=lambda: self.edit_button_click(apartment_data, selected_item)).grid(row=6, column=0, columnspan=2, pady=10)

    def button1_click(self):
        login = self.entry1.get()
        password = self.entry2.get()
        self.s, self.l = bd.connection_(self.db_password, self.db_user)
        if self.s is None:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {self.l}")
            return

        for user_data in self.l:
            if user_data[0] == login and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                self.user_role = user_data[2]
                self.setup_main_screen()
                return
        messagebox.showwarning("Ошибка", "Неверный логин или пароль")

    def button2_click(self):
        self.setup_register_screen()

    def button3_click(self):
        login = self.ent1.get()
        password = self.ent2.get()
        confirm_password = self.ent3.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return
        if password != confirm_password:
            messagebox.showwarning("Ошибка", "Пароли не совпадают")
            return
        if any(user_data[0] == login for user_data in self.l):
            messagebox.showwarning("Ошибка", "Пользователь уже существует")
            return

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        success, error = bd.add_user(self.db_password, self.db_user, login, hashed)
        if success:
            messagebox.showinfo("Успех", "Регистрация успешна")
            logging.info(f"New user registered: {login}")
            self.setup_login_screen()
        else:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {error}")

    def button4_click(self):
        try:
            area = float(self.entr1.get())
            rooms = int(self.entr2.get())
            address = self.entr3.get().strip()
            floor = int(self.entr4.get())
            sost = self.entr5.get()
            distance = float(self.entr6.get())
            if area <= 0 or rooms <= 0 or not address or floor <= 0 or not sost or distance < 0:
                messagebox.showwarning("Ошибка", "Некорректные данные")
                return

            success, error = bd.add_apartment(self.db_password, self.db_user, area, rooms, address, floor, sost, distance)
            if success:
                messagebox.showinfo("Успех", "Квартира добавлена")
                logging.info(f"User {self.db_user} added apartment: {area}, {rooms}, {address}, {floor}, {sost}, {distance}")
                self.window.destroy()
                self.refresh_table()
            else:
                messagebox.showwarning("Ошибка", error)
        except ValueError:
            messagebox.showwarning("Ошибка", "Проверьте формат данных")

    def edit_button_click(self, apartment_data, selected_item):
        try:
            area = float(self.entr_edit_area1.get())
            rooms = int(self.entr_edit_area2.get())
            address = self.entr_edit_area3.get().strip()
            floor = int(self.entr_edit_area4.get())
            sost = self.entr_edit_area5.get()
            distance = float(self.entr_edit_area6.get())
            if area <= 0 or rooms <= 0 or not address or floor <= 0 or not sost or distance < 0:
                messagebox.showwarning("Ошибка", "Некорректные данные")
                return

            updated_data = [apartment_data[0], area, rooms, address, floor, sost, distance]
            confirmation = messagebox.askyesno("Подтверждение", "Применить изменения?")
            if not confirmation:
                return

            success, error = bd.edit_apartment_bd(self.db_password, self.db_user, updated_data)
            if success:
                self.tree.item(selected_item, values=updated_data)
                messagebox.showinfo("Успех", "Квартира обновлена")
                logging.info(f"User {self.db_user} edited apartment ID {apartment_data[0]}")
                self.window.destroy()
                self.refresh_table()
            else:
                messagebox.showerror("Ошибка", error)
        except ValueError:
            messagebox.showwarning("Ошибка", "Проверьте формат данных")

    def delete_apartment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите квартиру")
            return

        apartment_data = self.tree.item(selected_item)["values"]
        confirmation = messagebox.askyesno("Подтверждение", "Удалить выбранную квартиру?")
        if not confirmation:
            return

        success, error = bd.delete_apartment_bd(self.db_password, self.db_user, apartment_data[0])
        if success:
            self.tree.delete(selected_item)
            messagebox.showinfo("Успех", "Квартира удалена")
            logging.info(f"User {self.db_user} deleted apartment ID {apartment_data[0]}")
            self.refresh_table()
        else:
            messagebox.showerror("Ошибка", error)

    def export_to_csv(self):
        try:
            with open("apartments.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Площадь", "Кол-во комнат", "Адрес", "Этаж", "Состояние", "Расстояние до центра"])
                for apartment in self.s:
                    writer.writerow(apartment)
            messagebox.showinfo("Успех", "Данные экспортированы в apartments.csv")
            logging.info(f"User {self.db_user} exported data to CSV")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

if __name__ == "__main__":
    from getpass import getpass
    db_user = input("Имя пользователя БД: ")
    db_password = getpass("Пароль БД (скрыт): ")
    root = tk.Tk()
    app = App(root, db_user, db_password)
    root.mainloop()
