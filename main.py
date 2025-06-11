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
        self.root.title("ИС студента Шабанов,МИУ23-01, Real Estate")
        x, y = (root.winfo_screenwidth() // 2) - (750 // 2), (root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"{750}x{500}+{x}+{y}")
        self.root.configure(bg="#71C9CE")

        # Стили
        style = ttk.Style()
        style.configure("TLabel", font="helvetica 13", padding=5, background="#71C9CE", foreground="#E3FDFD")
        style.configure("TButton", font="helvetica 10", padding=5, background="#3DC2C7", foreground="#222831")
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

    def evaluate_apartment(self, apartment):
        """Calculate an evaluation score for an apartment based on area, rooms, and price."""
        if not self.s:
            return 0
        areas = [float(a[1]) for a in self.s]
        rooms = [int(a[2]) for a in self.s]
        prices = [int(a[3]) for a in self.s]
        
        max_area, min_area = max(areas), min(areas)
        max_rooms, min_rooms = max(rooms), min(rooms)
        max_price, min_price = max(prices), min(prices)
        
        # Avoid division by zero
        area_range = max_area - min_area if max_area != min_area else 1
        rooms_range = max_rooms - min_rooms if max_rooms != min_rooms else 1
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Normalize values (0 to 1)
        norm_area = (float(apartment[1]) - min_area) / area_range
        norm_rooms = (int(apartment[2]) - min_rooms) / rooms_range
        norm_price = 1 - ((int(apartment[3]) - min_price) / price_range)  # Lower price is better
        
        # Weighted score (area: 40%, rooms: 30%, price: 30%)
        score = (0.4 * norm_area + 0.3 * norm_rooms + 0.3 * norm_price) * 100
        return round(score, 2)

    def setup_main_screen(self):
        self.clear_frame(self.frame)
        self.frame.pack_forget()

        self.frame = tk.Frame(self.root, bg="#71C9CE")
        self.frame.pack(expand=True, fill="both")

        # Таблица
        columns = ("Номер", "Площадь", "Кол-во комнат", "Цена за месяц", "Адрес", "Оценка")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Используем grid для точного размещения
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        self.tree.heading("Номер", text="ID", anchor="w", command=lambda: self.sort(0, False, int))
        self.tree.heading("Площадь", text="Площадь", anchor="w", command=lambda: self.sort(1, False, float))
        self.tree.heading("Кол-во комнат", text="Кол-во комнат", anchor="w", command=lambda: self.sort(2, False, int))
        self.tree.heading("Цена за месяц", text="Цена за месяц", anchor="w", command=lambda: self.sort(3, False, int))
        self.tree.heading("Адрес", text="Адрес", anchor="w", command=lambda: self.sort(4, False, str))
        self.tree.heading("Оценка", text="Оценка", anchor="w", command=lambda: self.sort(5, False, float))
        self.tree.column("#1", width=50)
        self.tree.column("#2", width=80)
        self.tree.column("#3", width=100)
        self.tree.column("#4", width=120)
        self.tree.column("#5", width=150)
        self.tree.column("#6", width=80)

        # Панель кнопок
        self.button_frame = tk.Frame(self.frame, bg="#71C9CE")
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Button(self.button_frame, text="Поиск", command=self.search_apartments).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Сбросить поиск", command=self.refresh_table).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Экспорт в CSV", command=self.export_to_csv).pack(side="left", padx=5)

        if self.user_role == 'admin':
            ttk.Button(self.button_frame, text="Добавить квартиру", command=self.create_add_window).pack(side="left", padx=5)
            ttk.Button(self.button_frame, text="Удалить квартиру", command=self.delete_apartment).pack(side="left", padx=5)
            self.tree.bind("<Double-1>", self.edit_apartment)
            self.tree.bind("<Delete>", lambda event: self.delete_apartment())

        # Настройка веса строк и столбцов для grid
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=0)
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
            evaluation = self.evaluate_apartment(apartment)
            self.tree.insert("", "end", values=(*apartment, evaluation))

    def create_add_window(self):
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"{500}x{300}+{x}+{y}")
        self.window.title("Добавить квартиру")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь:").grid(row=0, column=0, padx=10, pady=5)
        self.entr2 = ttk.Entry(window_frame)
        self.entr2.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr3 = ttk.Entry(window_frame)
        self.entr3.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Цена за месяц:").grid(row=2, column=0, padx=10, pady=5)
        self.entr4 = ttk.Entry(window_frame)
        self.entr4.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Адрес:").grid(row=3, column=0, padx=10, pady=5)
        self.entr5 = ttk.Entry(window_frame)
        self.entr5.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(window_frame, text="Добавить", command=self.button4_click).grid(row=4, column=0, columnspan=2, pady=10)

    def search_apartments(self):
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"{500}x{300}+{x}+{y}")
        self.window.title("Поиск квартир")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь (мин):").grid(row=0, column=0, padx=10, pady=5)
        self.entr_area_min = ttk.Entry(window_frame)
        self.entr_area_min.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr_rooms = ttk.Entry(window_frame)
        self.entr_rooms.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Цена (мин):").grid(row=2, column=0, padx=10, pady=5)
        self.entr_price_min = ttk.Entry(window_frame)
        self.entr_price_min.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Цена (макс):").grid(row=3, column=0, padx=10, pady=5)
        self.entr_price_max = ttk.Entry(window_frame)
        self.entr_price_max.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Адрес (часть):").grid(row=4, column=0, padx=10, pady=5)
        self.entr_address = ttk.Entry(window_frame)
        self.entr_address.grid(row=4, column=1, padx=10, pady=5)

        ttk.Button(window_frame, text="Поиск", command=self.search).grid(row=5, column=0, columnspan=2, pady=10)

    def search(self):
        try:
            area_min = self.entr_area_min.get()
            rooms = self.entr_rooms.get()
            price_min = self.entr_price_min.get()
            price_max = self.entr_price_max.get()
            address_part = self.entr_address.get().strip().lower()

            filtered_apartments = []
            for apartment in self.s:
                if area_min and (not area_min.strip() or float(apartment[1]) < float(area_min)):
                    continue
                if rooms and (not rooms.strip() or int(apartment[2]) != int(rooms)):
                    continue
                if price_min and (not price_min.strip() or int(apartment[3]) < int(price_min)):
                    continue
                if price_max and (not price_max.strip() or int(apartment[3]) > int(price_max)):
                    continue
                if address_part and address_part not in apartment[4].lower():
                    continue
                filtered_apartments.append(apartment)

            self.tree.delete(*self.tree.get_children())
            for apartment in filtered_apartments:
                evaluation = self.evaluate_apartment(apartment)
                self.tree.insert("", "end", values=(*apartment, evaluation))
            self.window.destroy()
        except ValueError:
            messagebox.showwarning("Ошибка", "Проверьте формат данных!")

    def edit_apartment(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        apartment_data = self.tree.item(selected_item)["values"]
        self.window = tk.Toplevel(self.root)
        x, y = (self.window.winfo_screenwidth() // 2) - (500 // 2), (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"{500}x{300}+{x}+{y}")
        self.window.title("Редактировать квартиру")
        self.window.configure(bg="#71C9CE")

        window_frame = tk.Frame(self.window, bg="#71C9CE")
        window_frame.pack(expand=True, fill="both")

        ttk.Label(window_frame, text="Площадь:").grid(row=0, column=0, padx=10, pady=5)
        self.entr_edit_area1 = ttk.Entry(window_frame)
        self.entr_edit_area1.insert(0, apartment_data[1])
        self.entr_edit_area1.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Кол-во комнат:").grid(row=1, column=0, padx=10, pady=5)
        self.entr_edit_area2 = ttk.Entry(window_frame)
        self.entr_edit_area2.insert(0, apartment_data[2])
        self.entr_edit_area2.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Цена за месяц:").grid(row=2, column=0, padx=10, pady=5)
        self.entr_edit_area3 = ttk.Entry(window_frame)
        self.entr_edit_area3.insert(0, apartment_data[3])
        self.entr_edit_area3.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(window_frame, text="Адрес:").grid(row=3, column=0, padx=10, pady=5)
        self.entr_edit_area4 = ttk.Entry(window_frame)
        self.entr_edit_area4.insert(0, apartment_data[4])  # Adjusted index for address
        self.entr_edit_area4.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(window_frame, text="Подтвердить", command=lambda: self.edit_button_click(apartment_data, selected_item)).grid(row=4, column=0, columnspan=2, pady=10)

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
            area = float(self.entr2.get())
            rooms = int(self.entr3.get())
            price = int(self.entr4.get())
            address = self.entr5.get().strip()
            if area <= 0 or rooms <= 0 or price <= 0 or not address:
                messagebox.showwarning("Ошибка", "Некорректные данные")
                return

            success, error = bd.add_apartment(self.db_password, self.db_user, area, rooms, price, address)
            if success:
                messagebox.showinfo("Успех", "Квартира добавлена")
                logging.info(f"User {self.db_user} added apartment: {area}, {rooms}, {price}, {address}")
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
            price = int(self.entr_edit_area3.get())
            address = self.entr_edit_area4.get().strip()
            if area <= 0 or rooms <= 0 or price <= 0 or not address:
                messagebox.showwarning("Ошибка", "Некорректные данные")
                return

            updated_data = [apartment_data[0], area, rooms, price, address]
            confirmation = messagebox.askyesno("Подтверждение", "Применить изменения?")
            if not confirmation:
                return

            success, error = bd.edit_apartment_bd(self.db_password, self.db_user, updated_data)
            if success:
                evaluation = self.evaluate_apartment(updated_data)
                self.tree.item(selected_item, values=(*updated_data, evaluation))
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
                writer.writerow(["ID", "Площадь", "Кол-во комнат", "Цена за месяц", "Адрес", "Оценка"])
                for apartment in self.s:
                    evaluation = self.evaluate_apartment(apartment)
                    writer.writerow([*apartment, evaluation])
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