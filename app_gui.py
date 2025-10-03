import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import threading
from src.trello_logic import (
    load_env_vars, get_lists, get_cards,
    generate_detailed_report, generate_time_analysis_report,
    generate_movement_report, generate_current_status_report,
    generate_velocity_report, save_report_to_excel,
    save_env_vars, test_trello_connection
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class TrelloApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generador de Reportes de Trello")
        self.geometry("600x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) 

        # --- State Variables ---
        self.api_key, self.token, self.board_id = None, None, None
        self.lists, self.cards, self.list_id_to_name = [], [], {}
        self.is_loading = False

        # --- Title ---
        self.label = ctk.CTkLabel(self, text="Generador de Reportes Trello", font=("Arial", 20))
        self.label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Botón de configuración
        self.settings_button = ctk.CTkButton(self, text="⚙️", width=30, height=30, command=self.open_settings)
        self.settings_button.grid(row=0, column=1, padx=(0, 20), pady=20, sticky='e')

        # --- Load Data Button ---
        self.load_button = ctk.CTkButton(self, text="Cargar Datos del Tablero", command=self.load_trello_data)
        self.load_button.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # --- Report Options Frame ---
        self.report_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.report_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.report_frame.grid_columnconfigure(0, weight=1)
        self.report_frame.grid_columnconfigure(1, weight=1)

        self.report_options = {
            "Reporte Detallado": "1", "Análisis de Tiempos": "2",
            "Reporte de Movimientos": "3", "Estado Actual": "4",
            "Análisis de Velocidad": "5", "Reporte Completo": "6"
        }
        
        row, col = 0, 0
        for name, val in self.report_options.items():
            button = ctk.CTkButton(self.report_frame, text=name, command=lambda v=val: self.generate_report(v))
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 1:
                col = 0
                row += 1

        # --- Status Bar ---
        self.status_frame = ctk.CTkFrame(self, height=50)
        self.status_frame.grid(row=3, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Listo. Cargue los datos para comenzar.")
        self.status_label.pack(side="left", padx=10)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, orientation="horizontal")
        self.progress_bar.set(0)

    def open_settings(self):
        SettingsWindow(self)

    def update_status(self, message, progress=None):
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
            self.progress_bar.pack(side="right", padx=10, pady=10, fill="x", expand=True)
        else:
            self.progress_bar.pack_forget()
        self.update_idletasks()

    def load_trello_data(self):
        if self.is_loading: return
        self.is_loading = True
        self.update_status("Cargando datos...", 0.1)
        self.load_button.configure(state="disabled")

        def task():
            try:
                creds, _ = load_env_vars()
                if not creds:
                    self.show_error("Variables de entorno no encontradas. Asegúrate de que el archivo .env está configurado.")
                    return
                self.api_key, self.token, self.board_id = creds
                self.update_status("Obteniendo listas...", 0.3)
                self.lists = get_lists(self.api_key, self.token, self.board_id)
                self.list_id_to_name = {lst['id']: lst['name'] for lst in self.lists}
                self.update_status("Obteniendo tarjetas...", 0.6)
                self.cards = get_cards(self.api_key, self.token, self.board_id)
                self.update_status(f"Datos cargados: {len(self.lists)} listas, {len(self.cards)} tarjetas.")
            except Exception as e:
                self.show_error(f"Error al cargar datos: {e}")
            finally:
                self.is_loading = False
                self.load_button.configure(state="normal")
        
        threading.Thread(target=task).start()

    def generate_report(self, report_type):
        if not self.cards:
            self.show_error("Por favor, cargue los datos del tablero primero.")
            return
        if self.is_loading: return
        self.is_loading = True

        start_date, end_date = None, None
        if report_type in ["1", "3"]: # Detallado y Movimientos
            date_range_window = DateRangeWindow(self)
            self.wait_window(date_range_window)
            if date_range_window.cancelled:
                self.is_loading = False
                return
            start_date, end_date = date_range_window.get_dates()

        filename = self.ask_save_filename(report_type)
        if not filename:
            self.is_loading = False
            return

        self.update_status("Generando reporte...", 0)

        def task():
            try:
                reports = {}
                if report_type == "1":
                    reports["Detallado"] = generate_detailed_report(self.cards, self.list_id_to_name, self.api_key, self.token, start_date, end_date, self.update_status)
                elif report_type == "2":
                    reports["Tiempos"] = generate_time_analysis_report(self.cards, self.list_id_to_name, self.api_key, self.token, self.update_status)
                elif report_type == "3":
                    reports["Movimientos"] = generate_movement_report(self.cards, self.list_id_to_name, self.api_key, self.token, start_date, end_date, self.update_status)
                elif report_type == "4":
                    df, summary = generate_current_status_report(self.cards, self.list_id_to_name)
                    reports["Estado_Detalle"], reports["Estado_Resumen"] = df, summary
                elif report_type == "5":
                    reports["Velocidad"] = generate_velocity_report(self.cards, self.list_id_to_name, self.api_key, self.token, self.update_status)
                elif report_type == "6":
                    self.update_status("Generando Reporte Detallado...", 0.1)
                    reports["Detallado"] = generate_detailed_report(self.cards, self.list_id_to_name, self.api_key, self.token)
                    self.update_status("Generando Análisis de Tiempos...", 0.3)
                    reports["Tiempos"] = generate_time_analysis_report(self.cards, self.list_id_to_name, self.api_key, self.token)
                    self.update_status("Generando Reporte de Movimientos...", 0.5)
                    reports["Movimientos"] = generate_movement_report(self.cards, self.list_id_to_name, self.api_key, self.token)
                    self.update_status("Generando Estado Actual...", 0.7)
                    df, summary = generate_current_status_report(self.cards, self.list_id_to_name)
                    reports["Estado_Detalle"], reports["Estado_Resumen"] = df, summary
                    self.update_status("Generando Análisis de Velocidad...", 0.9)
                    reports["Velocidad"] = generate_velocity_report(self.cards, self.list_id_to_name, self.api_key, self.token)

                self.update_status("Guardando archivo Excel...", 0.95)
                save_report_to_excel(reports, filename)
                self.update_status(f"¡Reporte guardado en {filename}!")
                messagebox.showinfo("Éxito", f"Reporte generado y guardado exitosamente en:\n{filename}")
            except Exception as e:
                self.show_error(f"Error al generar el reporte: {e}")
            finally:
                self.is_loading = False
                self.update_status("Listo.")

        threading.Thread(target=task).start()

    def ask_save_filename(self, report_type):
        report_names = {"1": "Detallado", "2": "Tiempos", "3": "Movimientos", "4": "Estado", "5": "Velocidad", "6": "Completo"}
        initial_name = f"Reporte_{report_names.get(report_type, 'Trello')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return filedialog.asksaveasfilename(
            initialfile=initial_name,
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.update_status("Error. Por favor, revise la configuración.")

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Configuración")
        self.geometry("500x350")

        self.grid_columnconfigure(1, weight=1)

        # Variables
        self.api_key_var = ctk.StringVar()
        self.token_var = ctk.StringVar()
        self.board_id_var = ctk.StringVar()
        self.theme_var = ctk.StringVar(value="blue") # Tema por defecto

        # Load existing values
        try:
            creds, theme = load_env_vars()
            if creds:
                self.api_key_var.set(creds[0])
                self.token_var.set(creds[1])
                self.board_id_var.set(creds[2])
            self.theme_var.set(theme)
        except Exception:
            pass # Ignore if .env doesn't exist

        # Widgets
        ctk.CTkLabel(self, text="API Key:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_key_entry = ctk.CTkEntry(self, textvariable=self.api_key_var, width=350)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Token:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.token_entry = ctk.CTkEntry(self, textvariable=self.token_var, width=350)
        self.token_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Board ID:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.board_id_entry = ctk.CTkEntry(self, textvariable=self.board_id_var, width=350)
        self.board_id_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Tema:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(self, variable=self.theme_var, values=["blue", "dark-blue", "green"])
        self.theme_menu.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        button_frame.grid_columnconfigure((0,1,2), weight=1)

        self.test_button = ctk.CTkButton(button_frame, text="Probar Conexión", command=self.test_connection)
        self.test_button.grid(row=0, column=0, padx=5)

        self.save_button = ctk.CTkButton(button_frame, text="Guardar", command=self.save_settings)
        self.save_button.grid(row=0, column=1, padx=5)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy)
        self.cancel_button.grid(row=0, column=2, padx=5)

    def test_connection(self):
        api_key = self.api_key_var.get()
        token = self.token_var.get()
        board_id = self.board_id_var.get()

        if not all([api_key, token, board_id]):
            self.status_label.configure(text="Todos los campos son obligatorios.", text_color="orange")
            return

        self.status_label.configure(text="Probando...", text_color="gray")
        
        def task():
            success, message = test_trello_connection(api_key, token, board_id)
            if success:
                self.status_label.configure(text=f"¡Conexión exitosa! {message}", text_color="green")
            else:
                self.status_label.configure(text=f"Error: {message}", text_color="red")
        
        threading.Thread(target=task).start()

    def save_settings(self):
        api_key = self.api_key_var.get()
        token = self.token_var.get()
        board_id = self.board_id_var.get()
        theme = self.theme_var.get()

        if not all([api_key, token, board_id]):
            messagebox.showerror("Error", "Todos los campos son obligatorios para guardar.")
            return
        
        try:
            save_env_vars(api_key, token, board_id, theme)
            messagebox.showinfo("Éxito", "La configuración se ha guardado correctamente.\nReinicia la aplicación para ver los cambios en el tema.")
            self.master.load_trello_data() # Recargar datos en la ventana principal
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo .env: {e}")

class DateRangeWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.title("Seleccionar Rango de Fechas")
        self.cancelled = True

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text="Seleccione un período para el reporte:")
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.period_var = ctk.StringVar(value="todo")
        
        ctk.CTkRadioButton(self, text="Todo el historial", variable=self.period_var, value="todo", command=self.toggle_custom_dates).grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        ctk.CTkRadioButton(self, text="Últimos 7 días", variable=self.period_var, value="7", command=self.toggle_custom_dates).grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        ctk.CTkRadioButton(self, text="Últimos 30 días", variable=self.period_var, value="30", command=self.toggle_custom_dates).grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        ctk.CTkRadioButton(self, text="Personalizado", variable=self.period_var, value="custom", command=self.toggle_custom_dates).grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="w")

        self.start_date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=5, column=0, padx=10, pady=5)
        self.end_date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=5, column=1, padx=10, pady=5)
        
        self.ok_button = ctk.CTkButton(self, text="Aceptar", command=self.on_ok)
        self.ok_button.grid(row=6, column=0, padx=10, pady=20)
        self.cancel_button = ctk.CTkButton(self, text="Cancelar", command=self.on_cancel)
        self.cancel_button.grid(row=6, column=1, padx=10, pady=20)

        self.toggle_custom_dates()
        self.transient(self.master)
        self.grab_set()

    def toggle_custom_dates(self):
        state = "normal" if self.period_var.get() == "custom" else "disabled"
        self.start_date_entry.configure(state=state)
        self.end_date_entry.configure(state=state)

    def on_ok(self):
        self.cancelled = False
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def get_dates(self):
        period = self.period_var.get()
        now = datetime.now()
        if period == "todo":
            return None, None
        if period == "7":
            return now - timedelta(days=7), now
        if period == "30":
            return now - timedelta(days=30), now
        if period == "custom":
            try:
                start = datetime.strptime(self.start_date_entry.get(), '%Y-%m-%d')
                end = datetime.strptime(self.end_date_entry.get(), '%Y-%m-%d')
                return start, end
            except ValueError:
                messagebox.showerror("Error de formato", "Formato de fecha inválido. Use YYYY-MM-DD.")
                return None, None
        return None, None

if __name__ == "__main__":
    _, theme = load_env_vars()
    ctk.set_default_color_theme(theme)
    
    app = TrelloApp()
    app.mainloop()

    # PyInstaller command (uncomment to use)
    # pyinstaller --onefile --noconsole app_gui.py
