import tkinter as tk
from tkinter import ttk, messagebox
from style import init_style
from lib.functions import center_window
from datetime import datetime
from questions import questions
import json, random


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Python Quiz")
        self.width = 600
        self.height = 400

        init_style()

        self.create_questions()

        # Originalfrage
        self.questions_original = self.load_questions("questions.json")
        if not self.questions_original:
            messagebox.showerror(
                "Fehler",
                "Fragen konnten nicht geladen werden. Bitte 'questions.json' prüfen.",
            )
            self.destroy()
            return

        self.create_widgets()
        self.start_new_quiz()  # Startet das Quiz initial und mischt die Fragen

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
        """Erzeugt die initialen GUI-Widgets."""
        self.question_label = ttk.Label(
            self, text="", wraplength=550, font=("Arial", 14), justify="left"
        )
        self.question_label.pack(pady=20)

        self.radio_var = tk.IntVar()
        self.radio_var.set(-1)

        self.radio_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(
                self,
                text="",
                variable=self.radio_var,
                value=i,
            )
            rb.pack(anchor="w", padx=50, pady=5)
            self.radio_buttons.append(rb)

        self.weiter_button = ttk.Button(
            self,
            text="Weiter",
            command=self.next_question_handler,
        )
        self.weiter_button.pack(pady=20)

        self.punkte_label = ttk.Label(self, text="Punkte: 0")
        self.punkte_label.pack(side="bottom", pady=10)

        self.beenden_button = ttk.Button(
            self, text="Quiz beenden", command=self.destroy
        )
        self.wiederholen_button = ttk.Button(
            self,
            text="Quiz wiederholen",
            command=self.start_new_quiz,
        )

    def start_new_quiz(self):
        """Setzt das Quiz zurück, mischt die Fragen und beginnt von vorne."""
        self.aktuelle_frage_index = 0
        self.punkte = 0
        self.nutzer_antworten = []

        # Shuffle questions
        self.questions = list(self.questions_original)
        random.shuffle(self.questions)

        self.question_label.pack(pady=20)
        for rb in self.radio_buttons:
            rb.pack(anchor="w", padx=50, pady=5)
            rb.config(state="normal")
        self.weiter_button.pack(pady=20)
        self.punkte_label.pack(side="bottom", pady=10)

        self.beenden_button.pack_forget()
        self.wiederholen_button.pack_forget()

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
        """Verarbeitet die Antwort des Benutzers und geht zur nächsten Frage."""
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
        """Zeigt das Endergebnis des Quiz an und bietet Optionen zur Wiederholung/Beenden."""
        gesamtfragen = len(self.questions)
        prozent = (self.punkte / gesamtfragen) * 100 if gesamtfragen > 0 else 0

        ergebnis_text = (
            f"Quiz beendet!\n"
            f"Sie haben {self.punkte} von {gesamtfragen} Fragen richtig beantwortet.\n"
            f"Das entspricht {prozent:.2f}%."
        )
        messagebox.showinfo("Quiz Ergebnis", ergebnis_text)

        ergebnis_data = {
            "datum": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "punkte": self.punkte,
            "gesamtfragen": gesamtfragen,
            "nutzer_antworten": self.nutzer_antworten,
        }
        try:
            with open("quiz_results.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(ergebnis_data, indent=4) + ",\n")
            print("Ergebnis gespeichert: quiz_results.json")
        except Exception as e:
            print(f"Fehler beim Speichern des Ergebnisses: {e}")

        self.question_label.pack_forget()
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.weiter_button.pack_forget()
        self.punkte_label.pack_forget()

        self.wiederholen_button.pack(pady=10)
        self.beenden_button.pack(pady=5)

    def run(self):
        center_window(self, self.width, self.height)
        self.mainloop()
