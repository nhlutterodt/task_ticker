"""
Task Ticker v1 - Beginner To-Do List App using Tkinter
Author: Your Name
Purpose: Learn Python GUI, structure, and basic scalable patterns
"""

import tkinter as tk
from tkinter import messagebox

# -------------------------------
# Class-Based App for Scalability
# -------------------------------

class TaskTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Ticker 📝")
        self.root.geometry("400x500")
        self.root.resizable(False, False)  # Fixed window size for simplicity

        # Store tasks in a Python list
        self.tasks = []

        # GUI setup
        self.create_widgets()

    def create_widgets(self):
        """Initialise and layout all UI components"""
        
        # ---------- Entry Frame ----------
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.task_input = tk.Entry(entry_frame, width=30, font=('Arial', 12))
        self.task_input.pack(side=tk.LEFT, padx=(10, 5))

        add_btn = tk.Button(entry_frame, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white")
        add_btn.pack(side=tk.LEFT)

        # ---------- Listbox Frame ----------
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.task_listbox = tk.Listbox(list_frame, height=15, width=45, font=('Arial', 11))
        self.task_listbox.pack(side=tk.LEFT)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Attach scrollbar to Listbox
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        # ---------- Button Frame ----------
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        delete_btn = tk.Button(btn_frame, text="Delete Task", command=self.delete_task, bg="#f44336", fg="white")
        delete_btn.grid(row=0, column=0, padx=10)

        done_btn = tk.Button(btn_frame, text="Mark Done", command=self.mark_done, bg="#2196F3", fg="white")
        done_btn.grid(row=0, column=1, padx=10)

    def add_task(self):
        """Add a task from Entry box to Listbox and internal list"""
        task_text = self.task_input.get().strip()

        if not task_text:
            messagebox.showwarning("Empty Input", "Please enter a task.")
            return

        # Basic sanitization (though tkinter doesn't interpret code)
        task_text = task_text.replace("<", "").replace(">", "").replace(";", "")

        self.tasks.append(task_text)
        self.task_listbox.insert(tk.END, task_text)
        self.task_input.delete(0, tk.END)

    def delete_task(self):
        """Delete the selected task from Listbox and internal list"""
        try:
            selected_index = self.task_listbox.curselection()[0]
            selected_task = self.task_listbox.get(selected_index)

            confirm = messagebox.askyesno("Confirm Delete", f"Delete task: '{selected_task}'?")
            if confirm:
                self.task_listbox.delete(selected_index)
                self.tasks.pop(selected_index)
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to delete.")

    def mark_done(self):
        """Mark the selected task as complete by prepending a check"""
        try:
            selected_index = self.task_listbox.curselection()[0]
            current_text = self.task_listbox.get(selected_index)

            # Check if already marked
            if current_text.startswith("✔"):
                messagebox.showinfo("Already Done", "This task is already marked as done.")
                return

            # Mark it done
            new_text = f"✔ {current_text}"
            self.task_listbox.delete(selected_index)
            self.task_listbox.insert(selected_index, new_text)
            self.tasks[selected_index] = new_text
        except IndexError:
            messagebox.showerror("No Selection", "Please select a task to mark as done.")

# -------------------------------
# App Entry Point (Safe Importing)
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTickerApp(root)
    root.mainloop()
