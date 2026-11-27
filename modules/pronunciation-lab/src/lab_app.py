"""Windows desktop interface for the local EOI Pronunciation Lab."""

from __future__ import annotations

from itertools import islice
from pathlib import Path
from queue import Empty, SimpleQueue
import re
from threading import Thread
from time import monotonic
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk
from typing import Callable

import numpy as np
import sounddevice as sd

from lab import (
    MAX_AUDIO_SECONDS,
    analyze_attempt,
    brief_report,
    delete_recording,
    export_report,
    list_attempts,
    load_audio,
    save_attempt,
    validate_metadata,
)
from phonetics import MAX_SECONDS, MAX_WORDS


STUDENTS = ("alumno-01", "alumno-02")
LEVELS = ("A1", "A2", "B1", "B2", "C1")
MODES = {
    "Lectura guiada": ("guided_reading", "Pega el texto facilitado por el profesor y léelo en voz alta."),
    "Repetición": ("repetition", "Escucha el modelo del profesor y repite. Puedes cargar un modelo de audio local."),
    "Pares mínimos": ("minimal_pairs", "Escribe las palabras o frases en el orden en que las vas a decir."),
    "Speaking espontáneo": ("spontaneous", "Responde a la consigna del profesor con palabras propias."),
    "Inglés turístico": ("tourism", "Practica la situación del profesor. Puedes usar un texto de referencia."),
}
AUDIO_TYPES = (("Audio WAV, MP3 o M4A", "*.wav *.mp3 *.m4a"),)
NO_COMPARISON = "Sin comparación"
PHONETIC_STATES = {
    "analyzed": "Evidencia técnica disponible",
    "no_deviation_detected": "Sin desviación detectada",
    "possible_deviation": "Posible desviación",
    "insufficient_evidence": "Evidencia insuficiente",
    "not_evaluated": "No evaluado",
}
FINDING_LABELS = {
    "substitution": "Posible sustitución",
    "possible_omission": "Posible omisión",
    "insertion": "Posible inserción",
}
READING_SIZES = (12, 14, 16, 18, 20, 22, 24, 28)
FRAGMENT_WORDS = min(45, MAX_WORDS)
TEXT_CHARACTERS = 4_000


def split_passage(text: str) -> list[str]:
    """Prefer complete sentences while keeping each fragment within the engine limits."""
    remaining = text.strip()
    fragments = []
    while remaining:
        words = list(islice(re.finditer(r"\b\w+\b", remaining), FRAGMENT_WORDS + 1))
        end = words[-1].start() if len(words) > FRAGMENT_WORDS else len(remaining)
        end = min(end, TEXT_CHARACTERS)
        if end < len(remaining):
            prefix = remaining[:end]
            breaks = list(re.finditer(r"(?<=[.!?])\s+|\n[ \t]*\n", prefix))
            if breaks and breaks[-1].start() > end // 2:
                end = breaks[-1].start()
            elif not remaining[end - 1].isspace() and not remaining[end].isspace():
                spaces = list(re.finditer(r"\s+", prefix))
                if spaces and spaces[-1].start() > end // 2:
                    end = spaces[-1].start()
        fragments.append(remaining[:end].strip())
        remaining = remaining[end:].lstrip()
    return fragments


class Recorder:
    def __init__(self, device: int, rate: int) -> None:
        self.rate = rate
        self.frames = 0
        self.interrupted = False
        self.started_at = 0.0
        self._chunks: list[np.ndarray] = []
        self._stream = sd.InputStream(
            device=device, samplerate=rate, channels=1, dtype="float32", callback=self._receive
        )

    def _receive(self, data: np.ndarray, frames: int, _time: object, status: object) -> None:
        self.interrupted |= bool(status)
        accepted = min(frames, self.rate * MAX_AUDIO_SECONDS - self.frames)
        if accepted > 0:
            self._chunks.append(data[:accepted, 0].copy())
            self.frames += accepted

    def start(self) -> None:
        self.started_at = monotonic()
        self._stream.start()

    def finish(self) -> np.ndarray:
        try:
            self._stream.stop()
        finally:
            self._stream.close()
        if self._chunks:
            return np.concatenate(self._chunks)
        return np.empty(0, dtype=np.float32)

    def cancel(self) -> None:
        try:
            self._stream.abort()
        finally:
            self._stream.close()


class LabApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.student = tk.StringVar(root)
        self.unit = tk.StringVar(root)
        self.level = tk.StringVar(root)
        self.activity = tk.StringVar(root)
        self.mode = tk.StringVar(root, "Lectura guiada")
        self.mode_hint = tk.StringVar(root, MODES[self.mode.get()][1])
        self.device = tk.StringVar(root)
        self.device_state = tk.StringVar(root)
        self.comparison = tk.StringVar(root, NO_COMPARISON)
        self.status = tk.StringVar(root, "Selecciona tu alumno e indica la unidad, el nivel y la actividad.")
        self.capture_state = tk.StringVar(root, "En espera")
        self.elapsed = tk.StringVar(root, "00:00")
        self.reading_size = tk.StringVar(root, "18")
        self.reading_font = tkfont.Font(root=root, family="Segoe UI", size=18)
        self.fragment_label = tk.StringVar(root)
        self.fragments: list[str] = []
        self.fragment_index = 0
        self.full_passage = ""
        self.reading_fullscreen = False
        self.previous_window_state = "normal"
        self.return_tab = ""

        self.devices: dict[str, tuple[int, int]] = {}
        self.comparisons: dict[str, dict] = {}
        self.inputs: list[tuple[tk.Widget, str]] = []
        self.recorder: Recorder | None = None
        self.recording_metadata: dict | None = None
        self.audio: tuple[np.ndarray, int] | None = None
        self.reference: tuple[np.ndarray, int] | None = None
        self.report: dict | None = None
        self.copied_text: str | None = None
        self.results: SimpleQueue = SimpleQueue()
        self.busy = False
        self.closed = False

        self._build()
        self._detect_devices()
        self._sync_buttons()
        root.protocol("WM_DELETE_WINDOW", self._close)
        root.bind("<F11>", self._toggle_reading)
        root.bind("<Escape>", self._exit_reading)

    def _build(self) -> None:
        root = self.root
        root.title("EOI Pronunciation Lab")
        root.geometry(f"{min(1120, root.winfo_screenwidth() - 36)}x{min(780, root.winfo_screenheight() - 86)}")
        root.minsize(640, 470)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        if root.tk.call("tk", "windowingsystem") == "win32":
            root.state("zoomed")

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f8")
        style.configure("TLabel", background="#f3f5f8", foreground="#142b45", font=("Segoe UI", 10))
        style.configure("Masthead.TFrame", background="#142b45")
        style.configure("Title.TLabel", background="#142b45", foreground="white", font=("Segoe UI", 17, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Hint.TLabel", foreground="#43556c", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 10), padding=(8, 4), background="#e8eef5",
                        foreground="#142b45", bordercolor="#aebfd2", lightcolor="#f3f6fa", darkcolor="#aebfd2")
        style.map("TButton", background=[("active", "#d8e5f2"), ("disabled", "#edf1f5")],
                  foreground=[("disabled", "#657386")])
        style.configure("Primary.TButton", background="#1a4778", foreground="white", bordercolor="#14385f")
        style.map("Primary.TButton", background=[("disabled", "#dce3ec"), ("active", "#14385f")],
                  foreground=[("disabled", "#4c5a6d")])
        style.configure("Capture.Primary.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 7))
        style.configure("Stop.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 7))
        style.configure("Capture.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Recording.TLabel", foreground="#9e2525", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook", background="#f3f5f8", bordercolor="#b8c5d4", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 5), font=("Segoe UI", 10, "bold"),
                        background="#e8eef5", foreground="#142b45")
        style.map("TNotebook.Tab", background=[("selected", "#1a4778")], foreground=[("selected", "white")])
        style.configure("TCombobox", background="#e8eef5", bordercolor="#aebfd2")
        style.map("TCombobox", fieldbackground=[("readonly", "white"), ("disabled", "#edf1f5")])
        style.layout("Reader.TNotebook.Tab", [])

        body = self.body = ttk.Frame(root)
        body.grid(sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)
        body.bind("<Configure>", self._adapt_shell)

        self.header = ttk.Frame(body, style="Masthead.TFrame", padding=(16, 5))
        self.header.grid(row=0, column=0, sticky="ew")
        ttk.Label(self.header, text="EOI Pronunciation Lab", style="Title.TLabel").pack(anchor="w")

        self.tabs = ttk.Notebook(body)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6, 0))
        self.practice_tab = ttk.Frame(self.tabs, padding=(8, 4))
        self.results_tab = ttk.Frame(self.tabs, padding=(8, 5))
        self.tabs.add(self.practice_tab, text="Práctica")
        self.tabs.add(self.results_tab, text="Resultados")
        self.practice_tab.columnconfigure(0, weight=1)
        self.practice_tab.rowconfigure(3, weight=1)
        self.results_tab.columnconfigure(0, weight=1)
        self.results_tab.rowconfigure(1, weight=1)

        form = self.form = ttk.Frame(self.practice_tab)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        for column in range(5):
            form.columnconfigure(column, weight=int(column in (3, 4)))
        student_box = self._field(form, 0, "Alumno", self.student, STUDENTS)
        student_box.bind("<<ComboboxSelected>>", self._student_changed)
        self._field(form, 1, "Unidad", self.unit)
        self._field(form, 2, "Nivel MCER", self.level, LEVELS)
        self._field(form, 3, "Actividad", self.activity)
        mode_box = self._field(form, 4, "Modo", self.mode, tuple(MODES))
        mode_box.bind("<<ComboboxSelected>>", self._mode_changed)

        self.mode_hint_label = ttk.Label(self.practice_tab, textvariable=self.mode_hint, style="Hint.TLabel")
        self.mode_hint_label.grid(row=1, column=0, sticky="w", pady=(0, 3))
        self.practice_tab.bind("<Configure>", lambda event: self.mode_hint_label.configure(wraplength=event.width - 16))

        reading_header = ttk.Frame(self.practice_tab)
        reading_header.grid(row=2, column=0, sticky="ew", pady=(0, 3))
        ttk.Label(reading_header, text="Texto de práctica", style="Section.TLabel").pack(side="left")
        self.reading_button = ttk.Button(reading_header, text="Pantalla completa (F11)", command=self._toggle_reading)
        self.reading_button.pack(side="right")
        font_choice = ttk.Combobox(reading_header, textvariable=self.reading_size, values=READING_SIZES,
                                   width=3, state="readonly")
        font_choice.pack(side="right", padx=(3, 8))
        font_choice.bind("<<ComboboxSelected>>", self._set_reading_size)
        ttk.Label(reading_header, text="Letra (pt)").pack(side="right")

        exercise = ttk.Frame(self.practice_tab)
        exercise.grid(row=3, column=0, sticky="nsew")
        exercise.columnconfigure(0, weight=1)
        exercise.rowconfigure(0, weight=1)
        self.expected = tk.Text(exercise, height=5, width=1, wrap="word", font=self.reading_font, padx=14, pady=9,
                                undo=True, relief="solid", borderwidth=1, foreground="#142b45", spacing3=6)
        self.expected.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(exercise, command=self.expected.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.expected.configure(yscrollcommand=scrollbar.set)

        reader_tools = self.reader_tools = ttk.Frame(self.practice_tab)
        reader_tools.grid(row=4, column=0, sticky="ew", pady=(4, 0))
        reader_tools.columnconfigure(1, weight=1)
        reader_tools.bind("<Configure>", self._arrange_reader_tools)
        self.source_tools = ttk.Frame(reader_tools)
        self.source_tools.grid(row=0, column=0, sticky="w")
        self.open_text_button = self._button(self.source_tools, "Abrir texto .txt…", self._open_text)
        self.split_button = self._button(self.source_tools, "Dividir en fragmentos", self._split_text)
        self.fragment_tools = ttk.Frame(reader_tools)
        self.fragment_tools.grid(row=0, column=0, sticky="w")
        self.complete_button = self._button(self.fragment_tools, "Texto completo", self._restore_passage)
        self.previous_fragment_button = self._button(self.fragment_tools, "Anterior", lambda: self._move_fragment(-1))
        ttk.Label(self.fragment_tools, textvariable=self.fragment_label).pack(side="left", padx=(1, 7))
        self.next_fragment_button = self._button(self.fragment_tools, "Siguiente", lambda: self._move_fragment(1))
        self.fragment_tools.grid_remove()

        reference_row = self.reference_row = ttk.Frame(reader_tools)
        reference_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 0))
        self.reference_button = self._button(reference_row, "Cargar audio modelo…", self._import_reference)
        self.play_reference_button = self._button(reference_row, "Oír modelo", self._play_reference)
        self.clear_reference_button = self._button(reference_row, "Quitar modelo", self._clear_reference)

        controls = ttk.Frame(body, padding=(20, 4, 20, 5))
        controls.grid(row=2, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Micrófono", style="Section.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 7))
        self.device_box = ttk.Combobox(controls, textvariable=self.device, state="readonly")
        self.device_box.grid(row=0, column=1, sticky="ew")
        self.device_box.bind("<<ComboboxSelected>>", self._device_changed)
        self.detect_button = ttk.Button(controls, text="Detectar", command=self._detect_devices)
        self.detect_button.grid(row=0, column=2, sticky="e", padx=(6, 0))
        ttk.Label(controls, textvariable=self.device_state, style="Hint.TLabel").grid(
            row=0, column=3, sticky="e", padx=(9, 0)
        )

        recording_row = ttk.Frame(controls)
        recording_row.grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 0))
        self.record_button = self._button(recording_row, "Iniciar grabación", self._record, primary=True)
        self.record_button.configure(style="Capture.Primary.TButton")
        self.stop_button = self._button(recording_row, "Detener y analizar", self._finish_recording)
        self.stop_button.configure(style="Stop.TButton")
        self.import_button = self._button(recording_row, "Importar grabación…", self._import_attempt)
        self.play_button = self._button(recording_row, "Oír grabación", self._play_attempt)

        capture_information = ttk.Frame(controls)
        capture_information.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(4, 0))
        self.capture_label = ttk.Label(capture_information, textvariable=self.capture_state, style="Capture.TLabel")
        self.capture_label.pack(side="left", padx=(0, 7))
        ttk.Label(capture_information, textvariable=self.elapsed, font=("Consolas", 11, "bold"), width=5).pack(side="left")
        self.stop_playback_button = ttk.Button(capture_information, text="Detener reproducción", command=self._stop_audio)
        self.stop_playback_button.pack(side="right")
        status = ttk.Label(capture_information, textvariable=self.status, style="Hint.TLabel", justify="left")
        status.pack(side="left", padx=9, fill="x", expand=True)
        status.bind("<Configure>", lambda event: status.configure(wraplength=max(event.width, 1)))

        actions = ttk.Frame(self.results_tab)
        actions.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        self.copy_button = self._button(actions, "Copiar informe", self._copy, primary=True)
        self.export_button = self._button(actions, "Exportar JSON privado", self._export)
        self.evidence_button = self._button(actions, "Ver evidencia fonética…", self._open_evidence)

        self.output = tk.Text(self.results_tab, height=5, width=1, wrap="word", font=("Segoe UI", 11), padx=9, pady=6,
                              borderwidth=1, relief="solid", foreground="#142b45", state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.results_tab, command=self.output.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        history = ttk.Frame(self.results_tab)
        history.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        history.columnconfigure(1, weight=1)
        ttk.Label(history, text="Comparar con").grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.comparison_box = ttk.Combobox(history, textvariable=self.comparison, values=(NO_COMPARISON,))
        self.comparison_box.grid(row=0, column=1, sticky="ew")
        self.comparison_box.bind("<<ComboboxSelected>>", self._comparison_changed)
        self.history_button = ttk.Button(history, text="Historial de grabaciones…", command=self._open_history)
        self.history_button.grid(row=0, column=2, padx=(6, 0))
        self.delete_button = ttk.Button(history, text="Eliminar esta grabación…", command=self._delete_current)
        self.delete_button.grid(row=0, column=3, padx=(6, 0))
        self._show_report()

    def _field(self, parent: ttk.Frame, column: int, title: str, variable: tk.StringVar,
               values: tuple[str, ...] = ()) -> ttk.Combobox | ttk.Entry:
        ttk.Label(parent, text=title).grid(row=0, column=column, sticky="w")
        if values:
            field = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", width=12)
            state = "readonly"
        else:
            field = ttk.Entry(parent, textvariable=variable, width=12)
            state = "normal"
        field.grid(row=1, column=column, sticky="ew", padx=(0, 7 if column < 4 else 0))
        self.inputs.append((field, state))
        return field

    @staticmethod
    def _button(parent: ttk.Frame, text: str, command: Callable, *, primary: bool = False) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command, style="Primary.TButton" if primary else "TButton")
        button.pack(side="left", padx=(0, 6))
        return button

    def _sync_buttons(self) -> None:
        idle = not self.busy and self.recorder is None
        text_ready = idle and self.mode.get() != "Speaking espontáneo"
        for field, normal_state in self.inputs:
            field.configure(state=normal_state if idle else "disabled")
        editable = text_ready and not self.reading_fullscreen and not self.fragments
        self.expected.configure(state="normal" if editable else "disabled")
        self.device_box.configure(state="readonly" if idle and self.devices else "disabled")
        self.comparison_box.configure(state="readonly" if idle and self.comparisons else "disabled")
        recording = self.recorder is not None
        self.capture_state.set("Grabando" if recording else "Procesando" if self.busy else "En espera")
        self.capture_label.configure(style="Recording.TLabel" if recording else "Capture.TLabel")

        states = {
            self.detect_button: idle,
            self.record_button: idle and self.device.get() in self.devices,
            self.stop_button: self.recorder is not None,
            self.import_button: idle,
            self.play_button: idle and self.audio is not None,
            self.reference_button: idle,
            self.play_reference_button: idle and self.reference is not None,
            self.clear_reference_button: idle and self.reference is not None,
            self.stop_playback_button: idle,
            self.copy_button: idle and self.report is not None,
            self.export_button: idle and self.report is not None,
            self.evidence_button: idle and self.report is not None,
            self.delete_button: idle and self.audio is not None,
            self.history_button: idle and self.student.get() in STUDENTS,
            self.open_text_button: editable,
            self.split_button: text_ready,
            self.complete_button: text_ready,
            self.previous_fragment_button: text_ready and self.fragment_index > 0,
            self.next_fragment_button: text_ready and self.fragment_index + 1 < len(self.fragments),
        }
        for button, enabled in states.items():
            button.configure(state="normal" if enabled else "disabled")

    def _set_reading_size(self, _event=None) -> None:
        self.reading_font.configure(size=int(self.reading_size.get()))

    def _adapt_shell(self, _event=None) -> None:
        scale = float(self.root.tk.call("tk", "scaling"))
        compact = self.body.winfo_height() < 690 and scale >= 2.5
        if self.reading_fullscreen or compact:
            self.header.grid_remove()
        elif not self.header.grid_info():
            self.header.grid()

    def _arrange_reader_tools(self, _event=None) -> None:
        if self.reading_fullscreen:
            self.reference_row.grid_remove()
            return
        text_tools = self.fragment_tools if self.fragments else self.source_tools
        required = text_tools.winfo_reqwidth() + self.reference_row.winfo_reqwidth() + 8
        if self.reader_tools.winfo_width() >= required:
            self.reference_row.grid(row=0, column=1, columnspan=1, sticky="e", pady=0)
        else:
            self.reference_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 0))

    def _toggle_reading(self, _event=None) -> str:
        if self.reading_fullscreen:
            self._exit_reading()
            return "break"
        self.reading_fullscreen = True
        self.previous_window_state = self.root.state()
        self.return_tab = self.tabs.select()
        self.tabs.select(self.practice_tab)
        self.tabs.tab(self.results_tab, state="hidden")
        self.tabs.configure(style="Reader.TNotebook")
        for widget in (self.form, self.mode_hint_label):
            widget.grid_remove()
        self._adapt_shell()
        self._arrange_reader_tools()
        self.reading_button.configure(text="Salir de pantalla completa (Esc)")
        self.root.attributes("-fullscreen", True)
        self._sync_buttons()
        self.expected.focus_set()
        return "break"

    def _exit_reading(self, _event=None) -> str | None:
        if not self.reading_fullscreen:
            return None
        self.reading_fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.state(self.previous_window_state)
        for widget in (self.form, self.mode_hint_label):
            widget.grid()
        self._adapt_shell()
        self._arrange_reader_tools()
        self.tabs.configure(style="TNotebook")
        self.tabs.tab(self.results_tab, state="normal")
        self.tabs.select(self.return_tab)
        self.reading_button.configure(text="Pantalla completa (F11)")
        self._sync_buttons()
        return "break"

    def _set_passage(self, text: str) -> None:
        self.expected.configure(state="normal")
        self.expected.delete("1.0", "end")
        self.expected.insert("1.0", text)
        self.expected.edit_reset()
        self.expected.yview_moveto(0)
        self._sync_buttons()

    def _open_text(self) -> None:
        path = filedialog.askopenfilename(parent=self.root, title="Selecciona el texto de práctica",
                                          filetypes=(("Texto plano UTF-8", "*.txt"),))
        if not path:
            return
        try:
            with Path(path).open(encoding="utf-8-sig") as source:
                text = source.read(64_001)
            if len(text) > 64_000:
                raise ValueError("Abre un texto de hasta 64 000 caracteres o pega un extracto.")
        except (OSError, ValueError) as exc:
            self._error("No se pudo abrir el texto UTF-8", exc)
            return
        self._set_passage(text)
        self.status.set("Texto cargado en memoria.")

    def _split_text(self) -> None:
        passage = self.expected.get("1.0", "end-1c")
        parts = split_passage(passage)
        if len(parts) < 2:
            self.status.set("El texto cabe en un fragmento." if parts else "Pega o abre el texto para dividirlo.")
            return
        self.full_passage = passage
        self.fragments = parts
        self.fragment_index = 0
        self.source_tools.grid_remove()
        self.fragment_tools.grid()
        self._arrange_reader_tools()
        self._move_fragment(0)
        self.status.set(f"Graba cada fragmento por separado. El cotejo fonético admite tomas de hasta {MAX_SECONDS} s.")

    def _move_fragment(self, amount: int) -> None:
        self.fragment_index += amount
        self.fragment_label.set(f"Fragmento {self.fragment_index + 1} de {len(self.fragments)}")
        self._set_passage(self.fragments[self.fragment_index])

    def _restore_passage(self) -> None:
        passage = self.full_passage
        self.fragments.clear()
        self.full_passage = ""
        self.fragment_index = 0
        self.fragment_label.set("")
        self.fragment_tools.grid_remove()
        self.source_tools.grid()
        self._arrange_reader_tools()
        self._set_passage(passage)

    def _detect_devices(self) -> None:
        selected = self.device.get()
        self.devices = {}
        failure = None
        try:
            host_apis = sd.query_hostapis()
            default = sd.default.device[0]
            for index, info in enumerate(sd.query_devices()):
                if info["max_input_channels"] > 0:
                    label = f"{info['name']} ({host_apis[info['hostapi']]['name']}, {index})"
                    self.devices[label] = (index, round(info["default_samplerate"]))
        except sd.PortAudioError as exc:
            failure = str(exc)
            self.devices.clear()
        if self.devices:
            default_name = next((name for name, details in self.devices.items() if details[0] == default),
                                next(iter(self.devices)))
            self.device.set(selected if selected in self.devices else default_name)
            self._device_changed()
        else:
            self.device.set("")
            self.device_state.set("Sin entrada · Puedes importar audio")
            if failure is not None:
                self.status.set(f"Detección del micrófono no disponible. {failure}")
        self.device_box.configure(values=tuple(self.devices))
        self._sync_buttons()

    def _device_changed(self, _event=None) -> None:
        selected = self.devices.get(self.device.get())
        if selected:
            self.device_state.set(f"Entrada detectada · {selected[1]:,} Hz".replace(",", " "))
        self._sync_buttons()

    def _student_changed(self, _event=None) -> None:
        self._stop_playback()
        self._clear_previous_clipboard()
        self.audio = None
        self.reference = None
        self.report = None
        self.unit.set("")
        self.level.set("")
        self.activity.set("")
        self.mode.set("Lectura guiada")
        self._mode_changed()
        self.full_passage = ""
        self._restore_passage()
        self.elapsed.set("00:00")
        self._refresh_comparisons()
        self._show_report()
        self.status.set(f"Perfil local activo · {self.student.get()}")

    def _mode_changed(self, _event=None) -> None:
        self.mode_hint.set(MODES[self.mode.get()][1])
        self._sync_buttons()

    def _metadata(self, source: str) -> dict | None:
        mode = MODES[self.mode.get()][0]
        expected = self.expected.get("1.0", "end-1c").strip() if mode != "spontaneous" else None
        if expected and len(expected) > TEXT_CHARACTERS:
            self._error("El texto supera el límite", "Usa «Dividir en fragmentos» antes de grabar o importar.")
            return None
        try:
            metadata = validate_metadata({
                "student_id": self.student.get(),
                "unit_id": self.unit.get().strip().upper(),
                "cefr": self.level.get(),
                "activity_id": self.activity.get().strip(),
                "mode": mode,
                "expected_text": expected,
            })
        except ValueError as exc:
            self._error("Comprueba los datos de la actividad", exc)
            return None
        return {**metadata, "source": source}

    def _record(self) -> None:
        metadata = self._metadata("recording")
        if metadata is None:
            return
        self.tabs.select(self.practice_tab)
        self._stop_playback()
        device, rate = self.devices[self.device.get()]
        recorder = None
        try:
            recorder = Recorder(device, rate)
            recorder.start()
        except (sd.PortAudioError, ValueError) as exc:
            if recorder is not None:
                try:
                    recorder.cancel()
                except sd.PortAudioError:
                    pass
            self._error("No se pudo abrir el micrófono",
                        f"Cierra otras aplicaciones que lo estén usando o importa una grabación.\n\n{exc}")
            return
        self.recorder = recorder
        self.recording_metadata = metadata
        self.status.set("Micrófono activo. Pulsa «Detener y analizar» al terminar.")
        self._sync_buttons()
        self._recording_clock(recorder)

    def _recording_clock(self, recorder: Recorder) -> None:
        if recorder is not self.recorder or self.closed:
            return
        elapsed = int(monotonic() - recorder.started_at)
        self.elapsed.set(f"{elapsed // 60:02d}:{elapsed % 60:02d}")
        if elapsed >= MAX_AUDIO_SECONDS:
            self._finish_recording()
            return
        self.root.after(150, self._recording_clock, recorder)

    def _finish_recording(self) -> None:
        recorder = self.recorder
        metadata = self.recording_metadata
        if recorder is None or metadata is None:
            return
        self.recorder = None
        self.recording_metadata = None
        try:
            samples = recorder.finish()
        except sd.PortAudioError as exc:
            self._sync_buttons()
            self._error("No se pudo finalizar la grabación", exc)
            return
        if recorder.interrupted:
            self._sync_buttons()
            self._error("El micrófono perdió datos",
                        "Repite la grabación o importa un archivo. El intento interrumpido no se ha guardado.")
            return
        self._start_job("Analizando la grabación…", self._analyze, (samples, recorder.rate), metadata)

    def _import_attempt(self) -> None:
        metadata = self._metadata("import")
        if metadata is None:
            return
        path = filedialog.askopenfilename(parent=self.root, title="Selecciona tu grabación", filetypes=AUDIO_TYPES)
        if path:
            self._start_job("Importando y analizando la grabación…", self._load_attempt, Path(path), metadata)

    def _import_reference(self) -> None:
        path = filedialog.askopenfilename(parent=self.root, title="Selecciona un audio modelo autorizado",
                                          filetypes=AUDIO_TYPES)
        if path:
            self._start_job("Preparando el modelo de audio…", self._load_reference, Path(path))

    @staticmethod
    def _load_reference(path: Path) -> tuple:
        return "reference", load_audio(path), path.name

    def _load_attempt(self, path: Path, metadata: dict) -> tuple:
        return self._analyze(load_audio(path), metadata)

    @staticmethod
    def _analyze(audio: tuple[np.ndarray, int], metadata: dict) -> tuple:
        samples, rate = audio
        report = analyze_attempt(samples, rate, metadata)
        save_error = None
        try:
            save_attempt(report, samples, rate)
        except (OSError, ValueError) as exc:
            save_error = str(exc)
        return "attempt", audio, report, save_error

    def _start_job(self, label: str, action: Callable, *args) -> None:
        self._stop_playback()
        self.busy = True
        self.status.set(label)
        self._sync_buttons()

        def work() -> None:
            try:
                self.results.put(action(*args))
            except Exception as exc:
                self.results.put(("error", str(exc)))

        Thread(target=work, name="eoi-lab-analysis", daemon=True).start()
        self.root.after(75, self._receive_job)

    def _receive_job(self) -> None:
        if self.closed:
            return
        try:
            kind, *result = self.results.get_nowait()
        except Empty:
            self.root.after(75, self._receive_job)
            return
        self.busy = False
        if kind == "attempt":
            self.audio, self.report, save_error = result
            self._refresh_comparisons()
            self._show_report()
            if self.reading_fullscreen:
                self.return_tab = str(self.results_tab)
            else:
                self.tabs.select(self.results_tab)
            if save_error is None:
                message = "Intento privado guardado."
                if self.reading_fullscreen:
                    message += " Pulsa Esc para ver Resultados."
                self.status.set(message)
            else:
                self._error("El análisis se completó, pero no se guardó el intento", save_error)
        elif kind == "reference":
            self.reference, filename = result
            self.status.set(f"Modelo listo para reproducir · {filename}")
        else:
            self._error("No se pudo procesar el audio", result[0])
        self._sync_buttons()

    def _refresh_comparisons(self) -> None:
        self.comparisons.clear()
        self.comparison.set(NO_COMPARISON)
        if self.report:
            report = self.report
            try:
                history = list_attempts(report["student_id"], report["activity_id"])
            except (OSError, ValueError) as exc:
                self._error("No se pudo leer el historial local", exc)
                history = []
            keys = ("student_id", "unit_id", "cefr", "activity_id", "mode", "expected_text")
            for attempt in history:
                if attempt["attempt_id"] == report["attempt_id"] or any(attempt.get(key) != report.get(key) for key in keys):
                    continue
                date = attempt["created_at"].replace("T", " ")[:16]
                number = attempt["attempt_number"]
                self.comparisons[f"Intento {number} · {date}"] = attempt
        self.comparison_box.configure(values=(NO_COMPARISON, *self.comparisons))
        self._sync_buttons()

    def _comparison_changed(self, _event=None) -> None:
        self._show_report()
        self._sync_buttons()

    def _report_text(self) -> str:
        if self.report is None:
            return "Graba o importa tu primer intento para obtener un informe."
        return brief_report(self.report, self.comparisons.get(self.comparison.get()))

    def _show_report(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", self._report_text())
        self.output.configure(state="disabled")

    @staticmethod
    def _word_interval(word: dict) -> tuple[float, float] | None:
        start, end = word.get("start_seconds"), word.get("end_seconds")
        if type(start) in (int, float) and type(end) in (int, float) and 0 <= start < end < float("inf"):
            return start, end
        return None

    def _word_audio(self, word: dict) -> tuple[np.ndarray, int] | None:
        interval = self._word_interval(word)
        supported = word.get("alignment_supported")
        if supported is None:
            supported = word.get("status") in {"no_deviation_detected", "possible_deviation"}
        if self.audio is None or interval is None or not supported:
            return None
        samples, rate = self.audio
        if interval[1] > len(samples) / rate + 0.0005:
            return None
        first = round(interval[0] * rate)
        last = min(round(interval[1] * rate), len(samples))
        if first < last:
            return samples[first:last], rate
        return None

    @staticmethod
    def _word_details(word: dict) -> str:
        lines = [f"{word.get('expected', '—')} · {PHONETIC_STATES.get(word.get('status'), 'No evaluado')}"]
        if word.get("recognized"):
            lines.append(f"Palabra reconocida · {word['recognized']}")
        if word.get("expected_ipa"):
            lines.append(f"IPA británica de referencia · {word['expected_ipa']}")
        elif word.get("reference_phones"):
            lines.append("Secuencia de referencia del modelo · " + " ".join(word["reference_phones"]))
        if word.get("reference_ipa_variants"):
            lines.append("Variantes británicas · " + ", ".join(word["reference_ipa_variants"]))
        if word.get("observed_phones"):
            lines.append("Hipótesis fonética · " + " ".join(word["observed_phones"]))
        if word.get("reason"):
            lines.append(word["reason"])
        for finding in word.get("findings", []):
            label = FINDING_LABELS.get(finding.get("kind"), "Indicio fonético")
            expected, observed = finding.get("expected") or "—", finding.get("observed") or "—"
            confidence = finding.get("confidence")
            signal = f" · confianza técnica {confidence:.2f}" if confidence is not None else ""
            lines.append(f"{label} · esperado {expected} → hipótesis {observed}{signal}")
            if finding.get("recommendation"):
                lines.append(finding["recommendation"])
        if free := word.get("free_ctc"):
            phones = " ".join(item["phone"] for item in free["phones"])
            lines.append(f"CTC libre, exploratorio (sin confianza calibrada) · {phones}")
            if candidate := free.get("review_candidate"):
                expected = candidate.get("expected") or "—"
                observed = candidate.get("observed") or "—"
                label = FINDING_LABELS.get(candidate.get("kind"), "Indicio fonético")
                lines.append(f"Pista para revisar por escucha · {label.lower()} · {expected} → {observed}")
        return "\n".join(lines)

    def _open_evidence(self) -> None:
        report = self.report
        if report is None:
            return
        phonetics = report.get("phonetics") or {}
        words = phonetics.get("words") or []
        window = tk.Toplevel(self.root)
        window.title("Evidencia fonética del intento")
        window.transient(self.root)
        scale = float(window.tk.call("tk", "scaling")) / (96 / 72)
        width = min(round(810 * scale), window.winfo_screenwidth() - 70)
        window.geometry(f"{width}x{min(round(460 * scale), window.winfo_screenheight() - 100)}")
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        content = ttk.Frame(window, padding=12)
        content.grid(sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)

        heading = f"{report['student_id']} · {report['unit_id']} · {report['activity_id']}"
        ttk.Label(content, text=heading, style="Section.TLabel").grid(row=0, column=0, sticky="w")
        labels = [PHONETIC_STATES.get(phonetics.get("status"), "No evaluado")]
        if phonetics.get("model"):
            labels.append(f"Modelo · {phonetics['model']}")
        if phonetics.get("reason"):
            labels.append(phonetics["reason"])
        if words:
            labels.append("La confianza técnica usa una escala sin calibrar. «Sin desviación detectada» se limita "
                          "a la evidencia observada por el motor.")
        elif not phonetics:
            labels.append("Este informe se generó antes de incorporar el análisis fonético.")
        limits = phonetics.get("limitations") or []
        summary = ttk.Label(content, text="\n".join(labels), style="Hint.TLabel", wraplength=width - 35, justify="left")
        summary.grid(row=1, column=0, sticky="w", pady=(4, 7))

        actions = ttk.Frame(content)
        actions.grid(row=4, column=0, sticky="w", pady=(7, 0))
        fragment_started = False

        def close() -> None:
            if fragment_started:
                self._stop_playback()
            window.destroy()

        if words:
            table = ttk.Frame(content)
            table.grid(row=2, column=0, sticky="nsew")
            table.columnconfigure(0, weight=1)
            table.rowconfigure(0, weight=1)
            columns = (
                ("word", "Palabra", 105), ("status", "Estado", 160), ("ipa", "Referencia", 118),
                ("hypothesis", "Hipótesis", 118), ("confidence", "Confianza", 80), ("time", "Intervalo (s)", 100),
            )
            tree = ttk.Treeview(table, columns=[key for key, _, _ in columns], show="headings",
                                height=min(9, len(words)), selectmode="browse")
            tree.grid(row=0, column=0, sticky="nsew")
            scrollbar = ttk.Scrollbar(table, orient="vertical", command=tree.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            across = ttk.Scrollbar(table, orient="horizontal", command=tree.xview)
            across.grid(row=1, column=0, sticky="ew")
            tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=across.set)
            for key, label, column_width in columns:
                tree.heading(key, text=label)
                pixels = round(column_width * scale)
                tree.column(key, width=pixels, minwidth=pixels, anchor="w")
            for number, word in enumerate(words):
                interval = self._word_interval(word)
                time_text = f"{interval[0]:.2f}–{interval[1]:.2f}" if interval else "—"
                confidence = word.get("confidence")
                reference = word.get("expected_ipa") or " ".join(word.get("reference_phones") or []) or "—"
                tree.insert("", "end", iid=str(number), values=(
                    word.get("expected", "—"), PHONETIC_STATES.get(word.get("status"), "No evaluado"),
                    reference, " ".join(word.get("observed_phones") or []) or "—",
                    f"{confidence:.2f}" if confidence is not None else "—", time_text,
                ))

            panel = ttk.Frame(content)
            panel.grid(row=3, column=0, sticky="ew", pady=(7, 0))
            panel.columnconfigure(0, weight=1)
            detail = tk.Text(panel, height=6, wrap="word", font=("Segoe UI", 10), padx=6, pady=4,
                             width=1, relief="solid", borderwidth=1, state="disabled")
            detail.grid(row=0, column=0, sticky="ew")
            detail_scroll = ttk.Scrollbar(panel, command=detail.yview)
            detail_scroll.grid(row=0, column=1, sticky="ns")
            detail.configure(yscrollcommand=detail_scroll.set)

            def selected_word() -> dict | None:
                selection = tree.selection()
                return words[int(selection[0])] if selection else None

            def play_word() -> None:
                nonlocal fragment_started
                word = selected_word()
                audio = self._word_audio(word) if word and self.report is report else None
                if audio is not None:
                    fragment_started = True
                    self._play(audio, f"Reproduciendo el fragmento de «{word['expected']}».", parent=window)

            play_button = self._button(actions, "Oír fragmento", play_word)

            def show_word(_event=None) -> None:
                word = selected_word()
                audio = self._word_audio(word) if word and self.report is report else None
                play_button.configure(state="normal" if audio is not None else "disabled")
                if word:
                    description = self._word_details(word)
                    if audio is None:
                        description += "\nEl fragmento requiere audio local y un intervalo utilizable."
                    detail.configure(state="normal")
                    detail.delete("1.0", "end")
                    detail.insert("1.0", description)
                    detail.configure(state="disabled")

            tree.bind("<<TreeviewSelect>>", show_word)
            tree.selection_set("0")
            tree.focus("0")
            tree.focus_set()
            show_word()

        if limits:
            self._button(actions, "Alcance y límites…", lambda: messagebox.showinfo(
                "Alcance de la evidencia fonética", "\n\n".join(limits), parent=window))
        self._button(actions, "Cerrar", close)
        window.protocol("WM_DELETE_WINDOW", close)
        window.bind("<Escape>", lambda _event: close())
        window.grab_set()

    def _play_attempt(self) -> None:
        self._play(self.audio, "Reproduciendo tu grabación.")

    def _play_reference(self) -> None:
        self._play(self.reference, "Reproduciendo el modelo de audio.")

    def _play(self, audio: tuple[np.ndarray, int] | None, status: str, *, parent: tk.Misc | None = None) -> None:
        if audio is None:
            return
        try:
            sd.play(*audio, blocking=False)
        except (sd.PortAudioError, ValueError) as exc:
            self._error("No se pudo reproducir el audio", exc, parent=parent)
        else:
            self.status.set(status)

    def _stop_playback(self) -> None:
        try:
            sd.stop()
        except sd.PortAudioError as exc:
            self.status.set(f"La salida de audio no se pudo detener: {exc}")

    def _stop_audio(self) -> None:
        self.status.set("Reproducción detenida.")
        self._stop_playback()

    def _clear_reference(self) -> None:
        self._stop_playback()
        self.reference = None
        self.status.set("Modelo retirado de la memoria. El archivo original se conserva.")
        self._sync_buttons()

    def _copy(self) -> None:
        contents = self._report_text()
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(contents)
        except tk.TclError as exc:
            self._error("El portapapeles no está disponible", exc)
        else:
            self.copied_text = contents
            self.status.set("Informe copiado. Pégalo en el chat privado de tu clase.")

    def _clear_previous_clipboard(self) -> None:
        if self.copied_text is None:
            return
        try:
            if self.root.clipboard_get() == self.copied_text:
                self.root.clipboard_clear()
        except tk.TclError:
            pass
        self.copied_text = None

    def _export(self) -> None:
        if self.report is None:
            return
        try:
            path = export_report(self.report)
        except (OSError, ValueError) as exc:
            self._error("No se pudo exportar el informe", exc)
        else:
            self.status.set(f"JSON exportado · {path}")

    def _delete_audio(self, report: dict, parent: tk.Misc) -> str | None:
        number = report["attempt_number"] or "sin guardar"
        selected = messagebox.askyesno(
            "Eliminar grabación local",
            f"¿Eliminar la grabación del intento {number} de {report['student_id']}?\n"
            "Se conservan el informe privado, sus exportaciones y el archivo original importado.",
            parent=parent,
            default=messagebox.NO,
        )
        if not selected:
            return None
        self._stop_playback()
        try:
            removed = delete_recording(report["student_id"], report["attempt_id"])
        except (OSError, ValueError) as exc:
            self._error("No se pudo eliminar la grabación", exc)
            return None
        current_id = self.report["attempt_id"] if self.report else None
        had_current_audio = report["attempt_id"] == current_id and self.audio is not None
        if had_current_audio:
            self.audio = None
        result = ("Grabación local eliminada." if removed or had_current_audio else
                  "Este intento ya no tenía un audio local guardado.")
        self.status.set(result)
        self._sync_buttons()
        return result

    def _delete_current(self) -> None:
        if self.report is not None:
            self._delete_audio(self.report, self.root)

    def _open_history(self) -> None:
        student = self.student.get()
        try:
            attempts = list_attempts(student)
        except (OSError, ValueError) as exc:
            self._error("No se pudo leer el historial local", exc)
            return
        if not attempts:
            self.status.set(f"{student} todavía no tiene intentos locales guardados.")
            return

        window = tk.Toplevel(self.root)
        window.title(f"Historial de grabaciones · {student}")
        window.transient(self.root)
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        frame = ttk.Frame(window, padding=12)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(frame, text=f"Intentos privados de {student}", style="Section.TLabel").grid(sticky="w")
        entries = tk.Listbox(frame, width=69, height=8, exportselection=False, font=("Segoe UI", 10))
        entries.grid(row=1, column=0, sticky="nsew", pady=5)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=entries.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        entries.configure(yscrollcommand=scrollbar.set)
        for attempt in attempts:
            date = attempt["created_at"].replace("T", " ")[:16]
            activity = f"{attempt['unit_id']} · {attempt['activity_id']}"
            entries.insert("end", f"{date} · {activity} · Intento {attempt['attempt_number']}")
        result_text = tk.StringVar(window, "Selecciona un intento para eliminar solo su audio local.")

        def remove_selected() -> None:
            selection = entries.curselection()
            if selection:
                result = self._delete_audio(attempts[selection[0]], window)
                if result:
                    result_text.set(result)

        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, sticky="w")
        self._button(actions, "Eliminar el audio seleccionado…", remove_selected)
        self._button(actions, "Cerrar", window.destroy)
        ttk.Label(frame, textvariable=result_text, style="Hint.TLabel").grid(row=3, column=0, sticky="w", pady=(5, 0))
        entries.focus_set()
        window.grab_set()

    def _error(self, title: str, error: object, *, parent: tk.Misc | None = None) -> None:
        self.status.set(title)
        messagebox.showerror(title, str(error), parent=parent or self.root)

    def _close(self) -> None:
        if self.busy:
            self.status.set("Espera a que termine el procesamiento para cerrar.")
            return
        if self.recorder is not None:
            close = messagebox.askyesno("Grabación en curso", "¿Descartar la grabación en curso y cerrar?",
                                        default=messagebox.NO, parent=self.root)
            if not close:
                return
            if self.busy:
                self.status.set("Espera a que termine el procesamiento para cerrar.")
                return
            if self.recorder is not None:
                try:
                    self.recorder.cancel()
                except sd.PortAudioError as exc:
                    self._error("No se pudo cerrar la entrada de audio", exc)
        self._stop_playback()
        self.closed = True
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    LabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
