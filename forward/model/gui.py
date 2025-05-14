import os
import csv
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from model import preprocess_text, process_input

# --- Utility Functions ---
def add_training_record(text, label):
    text_processed = preprocess_text(text)
    df_new = pd.DataFrame({'text': [text_processed], 'result': [label]})
    df_new.to_csv('data.csv', mode='a', header=not os.path.exists('data.csv'),
                  index=False, quoting=csv.QUOTE_ALL)

def load_csv_data(limit=50):
    if not os.path.exists('data.csv'):
        return pd.DataFrame(columns=['text', 'result'])
    df = pd.read_csv('data.csv', quoting=csv.QUOTE_ALL)
    return df.tail(limit)

def update_csv(updated_df):
    updated_df.to_csv('data.csv', index=False, quoting=csv.QUOTE_ALL)

# --- GUI Application ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Model Trainer and Predictor")
        self.geometry("1200x700")
        
        # Create paned window for left-right split
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel
        left_frame = ttk.Frame(self.paned_window, width=600)
        self.create_left_panel(left_frame)
        self.paned_window.add(left_frame)
        
        # Right panel
        right_frame = ttk.Frame(self.paned_window, width=600)
        self.create_right_panel(right_frame)
        self.paned_window.add(right_frame)
        
        # Load initial data
        self.load_data_to_table()

    def create_left_panel(self, parent):
        # Training Section
        training_frame = ttk.LabelFrame(parent, text="Direct Input Training", padding=10)
        training_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(training_frame, text="Enter Text:").grid(row=0, column=0, sticky="w")
        self.train_entry = ttk.Entry(training_frame, width=65)
        self.train_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.train_label_var = tk.IntVar(value=0)
        radio_frame = ttk.Frame(training_frame)
        radio_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(radio_frame, text="Allowed (0)", variable=self.train_label_var, value=0).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Banned (1)", variable=self.train_label_var, value=1).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Duplicate (2)", variable=self.train_label_var, value=2).pack(side="left", padx=5)
        
        ttk.Button(training_frame, text="Train", command=self.train_text).grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        
        # Prediction Section
        prediction_frame = ttk.LabelFrame(parent, text="Prediction", padding=10)
        prediction_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(prediction_frame, text="Input Text:").pack(anchor="w")
        self.predict_text_area = scrolledtext.ScrolledText(prediction_frame, width=70, height=5)
        self.predict_text_area.pack(padx=5, pady=5)
        
        ttk.Button(prediction_frame, text="Predict", command=self.predict_text).pack(pady=5)
        self.prediction_result = ttk.Label(prediction_frame, text="Prediction: ")
        self.prediction_result.pack()
        
        # Analysis Graph
        analysis_frame = ttk.LabelFrame(parent, text="Analysis Graph", padding=10)
        analysis_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.figure, self.ax = plt.subplots(figsize=(6,3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=analysis_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_right_panel(self, parent):
        # Table Section
        table_frame = ttk.LabelFrame(parent, text="Training Data (Last 50 Entries)", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(table_frame, columns=('text', 'result'), show='headings')
        self.tree.heading('text', text='Text')
        self.tree.heading('result', text='Label')
        self.tree.column('text', width=400)
        self.tree.column('result', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Double-1>', self.on_double_click)

    def load_data_to_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        df = load_csv_data()
        for index, row in df[::-1].iterrows():
            self.tree.insert('', tk.END, values=(row['text'], row['result']))

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        old_values = self.tree.item(item, 'values')

        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Entry")
        
        # Text Editor
        tk.Label(edit_win, text="Text:").grid(row=0, column=0, padx=5, pady=5)
        text_entry = tk.Text(edit_win, width=50, height=4)
        text_entry.insert(tk.END, old_values[0])
        text_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Label Selector
        tk.Label(edit_win, text="Label:").grid(row=1, column=0, padx=5, pady=5)
        label_var = tk.IntVar(value=int(old_values[1]))
        ttk.Combobox(edit_win, textvariable=label_var, values=[0, 1, 2], state='readonly').grid(row=1, column=1, padx=5, pady=5)

        # Save Handler
        def save_changes():
            new_text = text_entry.get("1.0", tk.END).strip()
            new_label = label_var.get()
            
            df = load_csv_data(limit=1000)
            mask = (df['text'] == old_values[0]) & (df['result'] == int(old_values[1]))
            df.loc[mask, 'text'] = new_text
            df.loc[mask, 'result'] = new_label
            update_csv(df)
            
            self.load_data_to_table()
            edit_win.destroy()
            messagebox.showinfo("Success", "Entry updated successfully")

        ttk.Button(edit_win, text="Save", command=save_changes).grid(row=2, columnspan=2, pady=10)

    def train_text(self):
        text = self.train_entry.get().strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text to train.")
            return
        
        label = self.train_label_var.get()
        add_training_record(text, label)
        self.load_data_to_table()
        messagebox.showinfo("Training", f"Text trained with label {label}.")
        self.train_entry.delete(0, tk.END)

    def predict_text(self):
        text = self.predict_text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text to predict.")
            return
        
        prediction = process_input(text)
        mapping = {0: "Allowed (0)", 1: "Banned (1)", 2: "Duplicate (2)"}
        self.prediction_result.config(text=f"Prediction: {mapping.get(prediction, 'Unknown')}")
        update_graph(self.canvas, self.ax, prediction)

def update_graph(canvas, ax, prediction):
    ax.clear()
    labels = ["Allowed (0)", "Banned (1)", "Duplicate (2)"]
    colors = ["green", "red", "blue"]
    bar_values = [0, 0, 0]
    if prediction in [0, 1, 2]:
        bar_values[prediction] = 1
    ax.bar(labels, bar_values, color=colors)
    ax.set_title("Prediction Result")
    ax.set_ylabel("Predicted Label = 1")
    canvas.draw()

if __name__ == "__main__":
    app = Application()
    app.mainloop()