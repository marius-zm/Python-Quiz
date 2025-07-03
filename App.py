import tkinter as tk
from tkinter import ttk, messagebox
from style import init_style
from lib.functions import center_window
from datetime import datetime
from questions import questions
import json, random


class App(tk.Tk):
    def __init__(self, login_instance):
        super().__init__()

        self.title("Python Quiz")
        self.width = 600
        self.height = 400

        init_style()

        self.create_questions()

        # Originalquestions
        self.questions_original = self.load_questions("questions.json")
        if not self.questions_original:
            messagebox.showerror(
                "Fehler",
                "Fragen konnten nicht geladen werden. Bitte 'questions.json' prüfen.",
            )
            self.destroy()
            return

        # Startmenu
        self.start_menu = ttk.Frame(self)
        self.start_menu.pack(expand=True, fill="both")
        self.heading_label = ttk.Label(self.start_menu, text="Das Python-Quiz")
        self.heading_label.pack()

        self.welcome_label = ttk.Label(
            self.start_menu, text=f"Willkommen, {login_instance.current_user["name"]}!"
        )
        self.welcome_label.pack()

        self.selected_difficulty = tk.StringVar(self.start_menu)
        self.selected_difficulty.set("einfach")  # default

        self.difficulty_options = ["einfach", "mittel", "schwer"]

        self.difficulty_label = ttk.Label(
            self.start_menu, text="Wählen Sie den Schwierigkeitsgrad:"
        )
        self.difficulty_label.pack(pady=10)

        self.difficulty_menu = ttk.OptionMenu(
            self.start_menu,
            self.selected_difficulty,
            self.selected_difficulty.get(),
            *self.difficulty_options,
            command=self.on_difficulty_selected,
        )
        self.difficulty_menu.pack(pady=5)

        self.status_label = ttk.Label(self.start_menu, text="")
        self.status_label.pack(pady=5)

        self.start_button = ttk.Button(
            self.start_menu, text="Start Quiz", command=self.start_new_quiz
        )
        self.start_button.pack()

        self.beenden_button = ttk.Button(
            self.start_menu, text="Quiz beenden", command=self.destroy
        )
        self.beenden_button.pack()

        self.create_widgets()

    # METHODS
    def on_difficulty_selected(self, difficulty):

        self.status_label.config(text=f"Ausgewählter Schwierigkeitsgrad: {difficulty}")

    def create_questions(self):
        try:
            with open("questions.json", "x", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        questions,
                        indent=4,
                    )
                )
        except FileExistsError:
            pass  # Datei existiert bereits

    def load_questions(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError:
            print(f"Fehler: Die Datei '{path}' wurde nicht gefunden.")
            return None

        except json.JSONDecodeError:
            print(f"Fehler: Ungültiges JSON-Format in '{path}'.")
            return None

    def create_widgets(self):
        self.questions_frame = ttk.Frame(self)
        self.question_label = ttk.Label(
            self.questions_frame,
            text="",
            wraplength=550,
            font=("Arial", 14),
            justify="left",
        )
        self.question_label.pack(pady=20)

        self.radio_var = tk.IntVar()
        self.radio_var.set(-1)

        self.radio_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(
                self.questions_frame,
                text="",
                variable=self.radio_var,
                value=i,
            )
            rb.pack(anchor="w", padx=50, pady=5)
            self.radio_buttons.append(rb)

        self.weiter_button = ttk.Button(
            self.questions_frame,
            text="Weiter",
            command=self.next_question_handler,
        )
        self.weiter_button.pack(pady=20)

        self.punkte_label = ttk.Label(self.questions_frame, text="Punkte: 0")
        self.punkte_label.pack(side="bottom", pady=10)

    def start_new_quiz(self):
        difficulty = self.selected_difficulty.get()

        # Filtere die Fragen basierend auf der Auswahl.
        if difficulty == "Alle":
            self.questions = list(self.questions_original)
        else:
            self.questions = [
                q
                for q in self.questions_original
                if q["schwierigkeitsgrad"] == difficulty
            ]

        # Prüfen, ob für die Auswahl überhaupt Fragen vorhanden sind.
        if not self.questions:
            messagebox.showinfo(
                "Keine Fragen",
                f"Es gibt keine Fragen mit dem Schwierigkeitsgrad '{difficulty}'.",
            )
            return

        self.aktuelle_frage_index = 0
        self.punkte = 0
        self.nutzer_antworten = []
        random.shuffle(self.questions)

        self.start_menu.pack_forget()
        self.questions_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.show_questions()

    def show_questions(self):
        if self.aktuelle_frage_index < len(self.questions):
            frage_obj = self.questions[self.aktuelle_frage_index]
            self.question_label.config(
                text=f"Frage {self.aktuelle_frage_index + 1}: {frage_obj['frage']}"
            )

            self.radio_var.set(-1)

            for i, rb in enumerate(self.radio_buttons):
                if i < len(frage_obj["antworten"]):
                    rb.config(text=frage_obj["antworten"][i], state="normal")
                    rb.pack(anchor="w", padx=50, pady=5)
                else:
                    rb.pack_forget()

            self.punkte_label.config(text=f"Punkte: {self.punkte}")
        else:
            self.show_results()

    def next_question_handler(self):
        ausgewaehlter_index = self.radio_var.get()

        if ausgewaehlter_index == -1:
            messagebox.showwarning(
                "Keine Auswahl",
                "Bitte wählen Sie eine Antwort aus, bevor Sie fortfahren.",
            )
            return

        aktuelle_frage = self.questions[self.aktuelle_frage_index]
        self.nutzer_antworten.append(ausgewaehlter_index)

        if ausgewaehlter_index == aktuelle_frage["richtige_antwort_index"]:
            self.punkte += 1

        self.aktuelle_frage_index += 1
        self.show_questions()

    def show_results(self):
        """Zeigt das Endergebnis in einem neuen Fenster an."""
        self.questions_frame.pack_forget()
        self.create_results_window()
        self.save_result()
        self.start_menu.pack(expand=True, fill="both")

    def create_results_window(self):
        """Erstellt ein neues Fenster mit der detaillierten Quiz-Auswertung."""
        results_window = tk.Toplevel(self)
        results_window.title("Quiz-Ergebnisse")
        results_window.geometry("700x550")

        main_frame = ttk.Frame(results_window)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        gesamtfragen = len(self.questions)
        prozent = (self.punkte / gesamtfragen) * 100 if gesamtfragen > 0 else 0
        summary_text = f"Ergebnis: {self.punkte} von {gesamtfragen} richtig ({prozent:.2f}%)"
        summary_label = ttk.Label(scrollable_frame, text=summary_text, font=("Helvetica", 14, "bold"))
        summary_label.pack(pady=10, padx=10)

        for i, question_obj in enumerate(self.questions):
            q_frame = ttk.Frame(scrollable_frame, padding=10, relief="groove", borderwidth=1)
            q_frame.pack(pady=5, padx=10, fill="x")

            q_text = f"{i+1}. {question_obj['frage']}"
            q_label = ttk.Label(q_frame, text=q_text, wraplength=600, font=("Helvetica", 11, "bold"))
            q_label.pack(anchor="w")

            user_answer_index = self.nutzer_antworten[i]
            user_answer_text = question_obj['antworten'][user_answer_index]
            correct_answer_index = question_obj['richtige_antwort_index']

            color = "green" if user_answer_index == correct_answer_index else "red"
            
            user_answer_label = ttk.Label(q_frame, text=f"Deine Antwort: {user_answer_text}", foreground=color, wraplength=600)
            user_answer_label.pack(anchor="w", pady=(5,0))

            if user_answer_index != correct_answer_index:
                correct_answer_text = question_obj['antworten'][correct_answer_index]
                correct_answer_label = ttk.Label(q_frame, text=f"Richtige Antwort: {correct_answer_text}", foreground="green", wraplength=600)
                correct_answer_label.pack(anchor="w")

        close_button = ttk.Button(results_window, text="Schließen", command=results_window.destroy)
        close_button.pack(pady=10)
        
        results_window.transient(self)
        results_window.grab_set()
        self.wait_window(results_window)
    
    def save_result(self):
        """Speichert das Quizergebnis in einer JSON-Datei."""
        ergebnis_data = {
            "datum": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "schwierigkeit": self.selected_difficulty.get(),
            "punkte": self.punkte,
            "gesamtfragen": len(self.questions),
        }
        try:
            try:
                with open("quiz_results.json", "r", encoding="utf-8") as f:
                    results = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                results = []
            
            results.append(ergebnis_data)
            with open("quiz_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Fehler beim Speichern des Ergebnisses: {e}")

    def run(self):
        center_window(self, self.width, self.height)
        self.mainloop()
