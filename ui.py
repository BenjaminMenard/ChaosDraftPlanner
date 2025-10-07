from time import sleep
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import packPoolSimulator
import csv

class PackManagerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chaos Draft Planner")
        self.geometry("700x500")


        # Entry Fee
        tk.Label(self, text="Entry Fee:").grid(row=0, column=0, sticky="w")
        self.entry_fee_var = tk.DoubleVar(value=25)
        tk.Entry(self, textvariable=self.entry_fee_var).grid(row=0, column=1)

        # Number of Players
        tk.Label(self, text="Number of Players:").grid(row=1, column=0, sticky="w")
        self.num_players_var = tk.IntVar(value=10)
        tk.Entry(self, textvariable=self.num_players_var).grid(row=1, column=1)

        # Packs per Player
        tk.Label(self, text="Packs per Player:").grid(row=2, column=0, sticky="w")
        self.packs_per_player_var = tk.IntVar(value=3)
        tk.Entry(self, textvariable=self.packs_per_player_var).grid(row=2, column=1)

        # Packs List
        self.pack_tree = ttk.Treeview(self, columns=("Name", "Price", "Quantity"), show="headings", height=10)
        self.pack_tree.heading("Name", text="Name")
        self.pack_tree.heading("Price", text="Price")
        self.pack_tree.heading("Quantity", text="Quantity")
        self.pack_tree.grid(row=3, columnspan=3, sticky="nsew", padx=5)

        # Add Pack
        self.pack_name_var = tk.StringVar()
        self.pack_price_var = tk.DoubleVar()
        self.pack_quantity_var = tk.IntVar()
        tk.Label(self, text="Pack Name:").grid(row=4, column=0, sticky="w", padx=5)
        tk.Label(self, text="Pack Price:").grid(row=4, column=1, sticky="w", padx=5)
        
        # Use a single frame for labels and entries
        pack_input_frame = tk.Frame(self)
        pack_input_frame.grid(row=4, column=0, columnspan=3, sticky="ew")
        pack_input_frame.grid_columnconfigure(0, weight=3)
        pack_input_frame.grid_columnconfigure(1, weight=1)
        pack_input_frame.grid_columnconfigure(2, weight=1)

        tk.Label(pack_input_frame, text="Pack Name:").grid(row=0, column=0, sticky="w", padx=5)
        tk.Label(pack_input_frame, text="Pack Price:").grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(pack_input_frame, text="Pack Quantity:").grid(row=0, column=2, sticky="w", padx=5)

        tk.Entry(pack_input_frame, textvariable=self.pack_name_var, width=15).grid(row=1, column=0, sticky="ew", padx=5)
        tk.Entry(pack_input_frame, textvariable=self.pack_price_var, width=10).grid(row=1, column=1, sticky="ew", padx=5)
        tk.Entry(pack_input_frame, textvariable=self.pack_quantity_var, width=10).grid(row=1, column=2, sticky="ew", padx=5)
    
        tk.Button(self, text="Import Packs", command=self.import_packs).grid(row=6, column=0, sticky="ew", pady=5)
        tk.Button(self, text="Add Pack", command=self.add_pack).grid(row=6, column=1, sticky="ew", padx=5)
        tk.Button(self, text="Export Packs", command=self.export_packs).grid(row=6, column=2, sticky="ew", pady=5)

        # Simulate Button
        tk.Button(self, text="Simulate Best Pack Pool", command=self.simulate_best_pool).grid(row=7, columnspan=5, sticky="ew", pady=10)

        # Configure grid weights
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def show_pack_simulation_results_window(self, result, top_n):
        result_window = tk.Toplevel(self)
        result_window.title("Pack Simulation Results")
        result_window.geometry("1200x800")

        columns = ("Diversity", "Dispersion", "Price/Player", "Total Price", "Pack List")
        # Set smaller width for the first four columns
        column_widths = {
            "Diversity": 30,
            "Dispersion": 30,
            "Price/Player": 30,
            "Total Price": 30,
            "Pack List": 700
        }
        tree = ttk.Treeview(result_window, columns=columns, show="headings", height=top_n)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=column_widths[col])  # Set the width here

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for entry in result[:top_n]:
            pack_list = ", ".join([f"{pack['name']} (x{pack['quantity']})" for pack in entry['distribution']])
            price_per_player = f"{entry.get('price_per_player', 0):.2f}"
            total_price = f"{entry.get('total_price', 0):.2f}"
            diversity = f"{entry.get('diversity_score', 0):.2f}"
            dispersion = f"{entry.get('dispersion_score', 0):.2f}"
            tree.insert("", "end", values=(diversity, dispersion, price_per_player, total_price, pack_list))

        tk.Button(result_window, text="Close", command=result_window.destroy).pack(pady=5)
    
    def add_pack(self):
        name = self.pack_name_var.get()
        price = self.pack_price_var.get()
        quantity = self.pack_quantity_var.get()
        if name and price >= 0 and quantity > 0:
            self.pack_tree.insert("", "end", values=(name, price, quantity))
            self.pack_name_var.set("")
            self.pack_price_var.set(0.0)
            self.pack_quantity_var.set(0)
        else:
            messagebox.showerror("Error", "Please enter valid pack details.")

    def import_packs(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                self.pack_tree.delete(*self.pack_tree.get_children())
                for row in reader:
                    if len(row) == 3:
                        self.pack_tree.insert("", "end", values=row)

    def export_packs(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='') as csvfile:
                writer = csv.writer(csvfile)
                for item in self.pack_tree.get_children():
                    writer.writerow(self.pack_tree.item(item)["values"])

    def simulate_best_pool(self):
        packs = []
        for item in self.pack_tree.get_children():
            values = self.pack_tree.item(item)["values"]
            name, price, quantity = values
            packs.append({'name': name, 'price': float(price), 'quantity': int(quantity)})
        num_players = self.num_players_var.get()
        packs_per_player = self.packs_per_player_var.get()
        entry_fee = self.entry_fee_var.get()

        print("Simulation Started.")
        try:
            result = packPoolSimulator.simulate_pack_distribution(packs, 
                                                                  entry_fee, 
                                                                  num_players, 
                                                                  packs_per_player)
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))
            return    
        print("Simulation complete.")
        print("Showing results...") 
        for element in result[:5]:
            print(element)
        self.show_pack_simulation_results_window(result, 10)
        

if __name__ == "__main__":
    app = PackManagerUI()
    app.mainloop()