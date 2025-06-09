import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# Данные о компонентах на основе презентации
market_data = {
    "Резистор 220 Ом": {"оптовая": 0.5, "розничная": 1.0},
    "Резистор 10 кОм": {"оптовая": 0.6, "розничная": 1.2},
    "Светодиод красный": {"оптовая": 1.0, "розничная": 2.0},
    "Светодиод зелёный": {"оптовая": 1.2, "розничная": 2.5},
    "Фоторезистор": {"оптовая": 5.0, "розничная": 10.0},
    "Потенциометр 10 кОм": {"оптовая": 10.0, "розничная": 20.0},
    "Кнопка тактовая": {"оптовая": 2.0, "розничная": 4.0},
    "Arduino-совместимая плата": {"оптовая": 500.0, "розничная": 1000.0},
    "Макетная плата": {"оптовая": 150.0, "розничная": 300.0},
    "Провода (джамперы)": {"оптовая": 0.3, "розничная": 0.6},
    "Источник питания 5 В": {"оптовая": 50.0, "розничная": 100.0},
    "Прозрачный картридж": {"оптовая": 100.0, "розничная": 200.0}
}

class ElectronicsKitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор стоимости набора электроники")
        self.root.geometry("900x700")

        # Хранилища данных
        self.selected_components = {}
        self.entries = {}

        # Фреймы
        self.frame_select = ttk.LabelFrame(root, text="Выбор компонентов", padding=10)
        self.frame_select.pack(fill="x", padx=10, pady=10)

        self.frame_cost = ttk.LabelFrame(root, text="Общая стоимость", padding=10)
        self.frame_cost.pack(fill="x", padx=10, pady=10)

        self.frame_graph = ttk.LabelFrame(root, text="График", padding=10)
        self.frame_graph.pack(fill="both", expand=True, padx=10, pady=10)

        # Заполнение списка компонентов
        self.components_list = list(market_data.keys())
        for idx, component in enumerate(self.components_list):
            ttk.Label(self.frame_select, text=component).grid(row=idx, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(self.frame_select, text=f"Опт: {market_data[component]['оптовая']} руб., Розн: {market_data[component]['розничная']} руб.").grid(row=idx, column=1, padx=5, pady=2)
            entry = ttk.Entry(self.frame_select, width=10)
            entry.grid(row=idx, column=2, padx=5, pady=2)
            entry.insert(0, "0")
            self.entries[component] = entry

        # Кнопки
        ttk.Button(self.frame_select, text="Обновить цены", command=self.update_prices).grid(row=len(self.components_list), column=0, pady=10)
        ttk.Button(self.frame_select, text="Рассчитать стоимость", command=self.calculate_cost).grid(row=len(self.components_list), column=1, pady=10)
        ttk.Button(self.frame_select, text="Сохранить данные", command=self.save_to_file).grid(row=len(self.components_list)+1, column=0, pady=10)

        # Поля для стоимости
        self.total_wholesale_label = ttk.Label(self.frame_cost, text="Оптовая: 0.00 руб.")
        self.total_wholesale_label.pack(pady=5)
        self.total_retail_label = ttk.Label(self.frame_cost, text="Розничная: 0.00 руб.")
        self.total_retail_label.pack(pady=5)

        # Настройка графика
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        ttk.Button(self.frame_graph, text="Сохранить график", command=self.save_plot).pack(pady=5)

    def update_prices(self):
        update_window = tk.Toplevel(self.root)
        update_window.title("Обновить цены")
        update_window.geometry("500x600")

        entries = {}
        for idx, component in enumerate(self.components_list):
            ttk.Label(update_window, text=component).grid(row=idx*2, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(update_window, text=f"Текущая опт: {market_data[component]['оптовая']}, розн: {market_data[component]['розничная']}").grid(row=idx*2, column=1, padx=5, pady=2)

            ttk.Label(update_window, text="Новая оптовая:").grid(row=idx*2+1, column=0, padx=5, pady=2)
            wholesale_entry = ttk.Entry(update_window, width=10)
            wholesale_entry.grid(row=idx*2+1, column=1, padx=5, pady=2)
            wholesale_entry.insert(0, str(market_data[component]["оптовая"]))

            ttk.Label(update_window, text="Новая розничная:").grid(row=idx*2+1, column=2, padx=5, pady=2)
            retail_entry = ttk.Entry(update_window, width=10)
            retail_entry.grid(row=idx*2+1, column=3, padx=5, pady=2)
            retail_entry.insert(0, str(market_data[component]["розничная"]))

            entries[component] = (wholesale_entry, retail_entry)

        def save_prices():
            for component, (wholesale_entry, retail_entry) in entries.items():
                try:
                    new_wholesale = float(wholesale_entry.get())
                    market_data[component]["оптовая"] = new_wholesale
                except ValueError:
                    pass
                try:
                    new_retail = float(retail_entry.get())
                    market_data[component]["розничная"] = new_retail
                except ValueError:
                    pass
            update_window.destroy()
            messagebox.showinfo("Успех", "Цены обновлены!")
            self.calculate_cost()  # Пересчитать стоимость после обновления

        ttk.Button(update_window, text="Сохранить", command=save_prices).grid(row=len(self.components_list)*2, column=0, columnspan=4, pady=10)

    def calculate_cost(self):
        self.selected_components.clear()
        total_wholesale = 0
        total_retail = 0

        for component, entry in self.entries.items():
            try:
                quantity = int(entry.get())
                if quantity > 0:
                    self.selected_components[component] = quantity
                    total_wholesale += market_data[component]["оптовая"] * quantity
                    total_retail += market_data[component]["розничная"] * quantity
            except ValueError:
                continue

        self.total_wholesale_label.config(text=f"Оптовая: {total_wholesale:.2f} руб.")
        self.total_retail_label.config(text=f"Розничная: {total_retail:.2f} руб.")

        self.ax.clear()
        if self.selected_components:
            components = list(self.selected_components.keys())
            quantities = list(self.selected_components.values())
            self.ax.bar(components, quantities, color="#1E90FF")
            self.ax.set_xlabel("Компоненты")
            self.ax.set_ylabel("Количество")
            self.ax.set_title("Выбранные компоненты")
            self.ax.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()

    def save_to_file(self):
        if not self.selected_components:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один компонент!")
            return
        with open('components.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Компонент", "Количество", "Оптовая цена", "Розничная цена"])
            for component, qty in self.selected_components.items():
                writer.writerow([component, qty, market_data[component]["оптовая"], market_data[component]["розничная"]])
        messagebox.showinfo("Успех", "Данные сохранены в components.csv!")

    def save_plot(self):
        if not self.selected_components:
            messagebox.showwarning("Предупреждение", "Сначала рассчитайте стоимость!")
            return
        self.fig.savefig('plot.png', dpi=300, bbox_inches='tight')
        messagebox.showinfo("Успех", "График сохранён как plot.png!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ElectronicsKitApp(root)
    root.mainloop()
