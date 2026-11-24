"""Windows desktop interface for the local EOI Pronunciation Lab."""

from __future__ import annotations

from pathlib import Path
from queue import Empty, SimpleQueue
from threading import Thread
from time import monotonic
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

    def _build(self) -> None:
        root = self.root
        root.title("EOI Pronunciation Lab")
        root.geometry(f"{min(900, root.winfo_screenwidth() - 36)}x{min(750, root.winfo_screenheight() - 86)}")
        root.minsize(680, 610)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f6f6")
        style.configure("TLabel", background="#f3f6f6", foreground="#21343c", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground="#153a45")
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Hint.TLabel", foreground="#405760", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9), padding=(8, 5))
        style.configure("Primary.TButton", background="#146375", foreground="white")
        style.map("Primary.TButton", background=[("disabled", "#d6e1e3"), ("active", "#0b4b5b")],
                  foreground=[("disabled", "#50626b")])

        body = ttk.Frame(root, padding=(18, 12))
        body.grid(sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)

        header = ttk.Frame(body)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="EOI Pronunciation Lab", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Práctica oral con análisis acústico local", style="Hint.TLabel").pack(anchor="w")

        form = ttk.Frame(body)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        for column in range(5):
            form.columnconfigure(column, weight=2 if column in (3, 4) else 1)
        student_box = self._field(form, 0, "Alumno", self.student, STUDENTS)
        student_box.bind("<<ComboboxSelected>>", self._student_changed)
        self._field(form, 1, "Unidad", self.unit)
        self._field(form, 2, "Nivel MCER", self.level, LEVELS)
        self._field(form, 3, "Actividad", self.activity)
        mode_box = self._field(form, 4, "Modo", self.mode, tuple(MODES))
        mode_box.bind("<<ComboboxSelected>>", self._mode_changed)

        exercise = ttk.Frame(body)
        exercise.grid(row=2, column=0, sticky="ew", pady=(1, 7))
        exercise.columnconfigure(0, weight=1)
        ttk.Label(exercise, textvariable=self.mode_hint, style="Hint.TLabel").grid(sticky="w")
        ttk.Label(exercise, text="Texto esperado", style="Section.TLabel").grid(sticky="w", pady=(3, 1))
        self.expected = tk.Text(exercise, height=3, wrap="word", font=("Segoe UI", 10), padx=6, pady=4,
                                undo=True, relief="solid", borderwidth=1, foreground="#21343c")
        self.expected.grid(sticky="ew")

        controls = ttk.Frame(body)
        controls.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Micrófono").grid(row=0, column=0, sticky="w", padx=(0, 7))
        self.device_box = ttk.Combobox(controls, textvariable=self.device, state="readonly")
        self.device_box.grid(row=0, column=1, sticky="ew")
        self.device_box.bind("<<ComboboxSelected>>", self._device_changed)
        self.detect_button = ttk.Button(controls, text="Detectar", command=self._detect_devices)
        self.detect_button.grid(row=0, column=2, sticky="e", padx=(6, 0))
        ttk.Label(controls, textvariable=self.device_state, style="Hint.TLabel").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(1, 3)
        )

        recording_row = ttk.Frame(controls)
        recording_row.grid(row=2, column=0, columnspan=3, sticky="w")
        self.record_button = self._button(recording_row, "Iniciar grabación", self._record, primary=True)
        self.stop_button = self._button(recording_row, "Detener y analizar", self._finish_recording)
        self.import_button = self._button(recording_row, "Importar grabación…", self._import_attempt)
        self.play_button = self._button(recording_row, "Oír grabación", self._play_attempt)

        reference_row = ttk.Frame(controls)
        reference_row.grid(row=3, column=0, columnspan=3, sticky="w", pady=(3, 0))
        self.reference_button = self._button(reference_row, "Cargar audio modelo…", self._import_reference)
        self.play_reference_button = self._button(reference_row, "Oír modelo", self._play_reference)
        self.clear_reference_button = self._button(reference_row, "Quitar modelo", self._clear_reference)
        self.stop_playback_button = self._button(reference_row, "Detener reproducción", self._stop_audio)

        output = ttk.Frame(body)
        output.grid(row=4, column=0, sticky="nsew")
        output.columnconfigure(0, weight=1)
        output.rowconfigure(1, weight=1)
        output_header = ttk.Frame(output)
        output_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(4, 2))
        ttk.Label(output_header, text="Informe para ChatGPT", style="Section.TLabel").pack(side="left")
        self.evidence_button = ttk.Button(output_header, text="Ver evidencia fonética…", command=self._open_evidence)
        self.evidence_button.pack(side="right")
        self.output = tk.Text(output, height=5, wrap="word", font=("Segoe UI", 10), padx=7, pady=5,
                              borderwidth=1, relief="solid", foreground="#21343c", state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(output, command=self.output.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(body)
        actions.grid(row=5, column=0, sticky="ew", pady=(5, 0))
        self.copy_button = self._button(actions, "Copiar informe", self._copy, primary=True)
        self.export_button = self._button(actions, "Exportar JSON privado", self._export)
        self.delete_button = self._button(actions, "Eliminar esta grabación…", self._delete_current)

        history = ttk.Frame(body)
        history.grid(row=6, column=0, sticky="ew", pady=(4, 0))
        history.columnconfigure(1, weight=1)
        ttk.Label(history, text="Comparar con").grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.comparison_box = ttk.Combobox(history, textvariable=self.comparison, values=(NO_COMPARISON,))
        self.comparison_box.grid(row=0, column=1, sticky="ew")
        self.comparison_box.bind("<<ComboboxSelected>>", self._comparison_changed)
        self.history_button = ttk.Button(history, text="Historial de grabaciones…", command=self._open_history)
        self.history_button.grid(row=0, column=2, padx=(6, 0))

        status = ttk.Label(body, textvariable=self.status, style="Hint.TLabel", justify="left", wraplength=820)
        status.grid(row=7, column=0, sticky="w", pady=(5, 0))
        body.bind("<Configure>", lambda event: status.configure(wraplength=event.width - 36))
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
        for field, normal_state in self.inputs:
            field.configure(state=normal_state if idle else "disabled")
        self.expected.configure(state="normal" if idle and self.mode.get() != "Speaking espontáneo" else "disabled")
        self.device_box.configure(state="readonly" if idle and self.devices else "disabled")
        self.comparison_box.configure(state="readonly" if idle and self.comparisons else "disabled")

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
        }
        for button, enabled in states.items():
            button.configure(state="normal" if enabled else "disabled")

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
            self.device_state.set("No se detectó ningún micrófono. Puedes importar un audio." if failure is None else
                                  f"Detección no disponible. Puedes importar un audio. {failure}")
        self.device_box.configure(values=tuple(self.devices))
        self._sync_buttons()

    def _device_changed(self, _event=None) -> None:
        selected = self.devices.get(self.device.get())
        if selected:
            self.device_state.set(f"Entrada detectada · {selected[1]:,} Hz · mono al grabar".replace(",", " "))
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
        self.expected.delete("1.0", "end")
        self.expected.edit_reset()
        self._refresh_comparisons()
        self._show_report()
        self.status.set(f"Perfil local activo · {self.student.get()}")

    def _mode_changed(self, _event=None) -> None:
        self.mode_hint.set(MODES[self.mode.get()][1])
        self._sync_buttons()

    def _metadata(self, source: str) -> dict | None:
        mode = MODES[self.mode.get()][0]
        expected = self.expected.get("1.0", "end-1c").strip() if mode != "spontaneous" else None
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
        self._sync_buttons()
        self._recording_clock(recorder)

    def _recording_clock(self, recorder: Recorder) -> None:
        if recorder is not self.recorder or self.closed:
            return
        elapsed = int(monotonic() - recorder.started_at)
        if elapsed >= MAX_AUDIO_SECONDS:
            self._finish_recording()
            return
        self.status.set(f"Grabando · {elapsed // 60}:{elapsed % 60:02d} · Pulsa «Detener y analizar» al terminar.")
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
            if save_error is None:
                self.status.set(f"Intento privado guardado · {self.report['student_id']} · {self.report['activity_id']}")
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
        if self.audio is None or interval is None or word.get("status") not in {
            "no_deviation_detected", "possible_deviation",
        }:
            return None
        samples, rate = self.audio
        if interval[1] > len(samples) / rate:
            return None
        first, last = (round(bound * rate) for bound in interval)
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
        labels.extend(phonetics.get("limitations") or [])
        summary = ttk.Label(content, text="\n".join(labels), style="Hint.TLabel", wraplength=720, justify="left")
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
            tree.configure(yscrollcommand=scrollbar.set)
            for key, label, width in columns:
                tree.heading(key, text=label)
                tree.column(key, width=width, minwidth=50, anchor="w")
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

            detail = tk.Text(content, height=6, wrap="word", font=("Segoe UI", 10), padx=6, pady=4,
                             relief="solid", borderwidth=1, state="disabled")
            detail.grid(row=3, column=0, sticky="ew", pady=(7, 0))

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
