import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # API configuration
        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        self.base_url = "https://v6.exchangerate-api.com/v6"

        # Available currencies (common ones)
        self.currencies = [
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "RUB",
            "BRL", "ZAR", "NZD", "MXN", "SGD", "HKD", "SEK", "KRW", "TRY", "PLN"
        ]

        # History file
        self.history_file = "history.json"
        self.history = self.load_history()

        # Build GUI
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Currency Converter", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        # From currency
        tk.Label(main_frame, text="From:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.from_currency = ttk.Combobox(main_frame, values=self.currencies, width=10, font=("Arial", 12))
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        self.from_currency.set("USD")

        # To currency
        tk.Label(main_frame, text="To:", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.to_currency = ttk.Combobox(main_frame, values=self.currencies, width=10, font=("Arial", 12))
        self.to_currency.grid(row=0, column=3, padx=5, pady=5)
        self.to_currency.set("EUR")

        # Amount
        tk.Label(main_frame, text="Amount:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = tk.Entry(main_frame, width=20, font=("Arial", 12))
        self.amount_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Convert button
        self.convert_btn = tk.Button(main_frame, text="Convert", command=self.convert, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.convert_btn.grid(row=1, column=3, padx=5, pady=5)

        # Result label
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"), fg="blue")
        self.result_label.pack(pady=10)

        # History section
        tk.Label(self.root, text="Conversion History", font=("Arial", 14, "bold")).pack(pady=(20, 5))

        # Table frame with scrollbar
        table_frame = tk.Frame(self.root)
        table_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_tree = ttk.Treeview(table_frame, columns=("Date", "From", "To", "Amount", "Result"), show="headings", yscrollcommand=scrollbar.set)
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("From", text="From")
        self.history_tree.heading("To", text="To")
        self.history_tree.heading("Amount", text="Amount")
        self.history_tree.heading("Result", text="Result")
        self.history_tree.column("Date", width=140)
        self.history_tree.column("From", width=60)
        self.history_tree.column("To", width=60)
        self.history_tree.column("Amount", width=100)
        self.history_tree.column("Result", width=100)
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)

        # Buttons for history
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.save_btn = tk.Button(btn_frame, text="Save History to File", command=self.save_history_to_file, bg="#2196F3", fg="white")
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.load_btn = tk.Button(btn_frame, text="Load History from File", command=self.load_history_from_file, bg="#FF9800", fg="white")
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear History", command=self.clear_history, bg="#F44336", fg="white")
        self.clear_btn.pack(side=tk.LEFT, padx=5)

    def get_exchange_rate(self, from_curr, to_curr):
        """Fetch exchange rate from API"""
        url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("result") == "success":
                return data.get("conversion_rate")
            else:
                messagebox.showerror("API Error", f"Failed to get rate: {data.get('error-type', 'Unknown error')}")
                return None
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to API: {str(e)}")
            return None

    def convert(self):
        """Perform currency conversion"""
        amount_str = self.amount_entry.get().strip()
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Input Error", "Amount must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if not from_curr or not to_curr:
            messagebox.showerror("Input Error", "Please select both currencies")
            return

        # Get exchange rate
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate is None:
            return

        converted = amount * rate
        self.result_label.config(text=f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}")

        # Save to history
        self.add_to_history(from_curr, to_curr, amount, converted)

    def add_to_history(self, from_curr, to_curr, amount, result):
        """Add conversion to history"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result
        }
        self.history.append(entry)
        self.update_history_table()
        self.save_history_to_file()  # Auto-save after each conversion

    def update_history_table(self):
        """Refresh the history table view"""
        # Clear existing rows
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        
        # Add history entries
        for entry in self.history:
            self.history_tree.insert("", tk.END, values=(
                entry["date"],
                entry["from"],
                entry["to"],
                f"{entry['amount']:.2f}",
                f"{entry['result']:.2f}"
            ))

    def save_history_to_file(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"History saved to {self.history_file}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save history: {str(e)}")

    def load_history_from_file(self):
        """Load history from JSON file"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            self.update_history_table()
            messagebox.showinfo("Success", f"History loaded from {self.history_file}")
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "No history file found. Starting empty.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load history: {str(e)}")

    def load_history(self):
        """Load initial history from file if exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm", "Clear all conversion history?"):
            self.history = []
            self.update_history_table()
            self.save_history_to_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
