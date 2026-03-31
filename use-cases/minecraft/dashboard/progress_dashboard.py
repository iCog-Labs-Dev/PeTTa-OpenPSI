import argparse
import json
import os
import queue
import re
import socket
import threading
import tkinter as tk
from typing import Any

import dearpygui.dearpygui as dpg

FIXED_DEMANDS = ["Hunger", "Safety", "Curiosity", "Energy", "Breath"]
FIXED_EMOTIONS = ["Happiness", "Sadness", "Anger", "Fear", "Gratitude"]
METRIC_BAR_WIDTH = 280


def clamp_progress(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def normalize_progress(value: float) -> float:
    # Accept either 0..1 or 0..100.
    if value > 1.0:
        value = value / 100.0
    return clamp_progress(value)


def to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return str(value)


def parse_pairs(values: list[Any]) -> dict[str, float]:
    parsed: dict[str, float] = {}
    if len(values) % 2 != 0:
        return parsed
    for i in range(0, len(values), 2):
        key = values[i]
        raw_value = values[i + 1]
        value = to_float(raw_value)
        if value is None:
            continue
        parsed[to_text(key)] = normalize_progress(value)
    return parsed


def parse_demand_entry(entry: Any) -> tuple[str, float] | None:
    # Supports: [demand, name, min, max, value]
    if isinstance(entry, (list, tuple)) and len(entry) >= 5:
        kind = to_text(entry[0]).strip().lower()
        name = to_text(entry[1]).strip()
        value = to_float(entry[4])
        if (
            kind == "demand"
            and name != ""
            and value is not None
        ):
            return name, normalize_progress(value)

    # Supports: "demand name min max value" textual fallback.
    if isinstance(entry, str):
        match = re.match(
            r"^\(?\s*demand\s+([A-Za-z_][A-Za-z0-9_]*)\s+[-+]?\d*\.?\d+\s+[-+]?\d*\.?\d+\s+([-+]?\d*\.?\d+)\s*\)?$",
            entry.strip(),
            flags=re.IGNORECASE,
        )
        if match:
            name, value = match.group(1), match.group(2)
            return name, normalize_progress(float(value))

    return None


def parse_demand_payload(event_data: Any) -> dict[str, float]:
    demands: dict[str, float] = {}

    if isinstance(event_data, (list, tuple)):
        # Legacy format: [name1, value1, name2, value2, ...]
        pair_demands = parse_pairs(event_data)
        if pair_demands:
            return pair_demands

        # Current format: [demand, name, min, max, value]
        single = parse_demand_entry(event_data)
        if single is not None:
            name, value = single
            demands[name] = value
            return demands

        # Batch format: [[demand, ...], [demand, ...], ...]
        for entry in event_data:
            parsed = parse_demand_entry(entry)
            if parsed is None:
                continue
            name, value = parsed
            demands[name] = value
        return demands

    if isinstance(event_data, str):
        single = parse_demand_entry(event_data)
        if single is not None:
            name, value = single
            demands[name] = value

    return demands


def parse_typed_event(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, list) or len(payload) < 2:
        return None
    event_type = to_text(payload[0]).strip().lower()
    event_data = payload[1]

    if event_type == "demand":
        demands = parse_demand_payload(event_data)
        return {
            "label": "Demand update received",
            "demands": demands,
        }

    if event_type == "emotion" and isinstance(event_data, list):
        emotions = parse_pairs(event_data)
        return {
            "label": "Emotion update received",
            "emotions": emotions,
        }

    if event_type == "action":
        if isinstance(event_data, (list, tuple)):
            action_text = " ".join(str(item) for item in event_data)
        else:
            action_text = to_text(event_data).strip()
        return {
            "label": "Action update received",
            "action": action_text,
        }

    return {"label": str(payload)}


def parse_update(line: str) -> dict[str, Any] | None:
    line = line.strip()
    if not line:
        return None

    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        payload = line

    typed_event = parse_typed_event(payload)
    if typed_event is not None:
        return typed_event

    if isinstance(payload, (int, float)):
        progress = normalize_progress(float(payload))
        return {"progress": progress, "label": f"{int(progress * 100)}%"}

    if isinstance(payload, dict):
        progress_keys = ("progress", "value", "percent", "pct")
        progress = None
        for key in progress_keys:
            if key in payload and isinstance(payload[key], (int, float)):
                progress = normalize_progress(float(payload[key]))
                break

        label = str(payload.get("status") or payload.get("label") or payload)
        if progress is None:
            return {"label": label}
        return {"progress": progress, "label": label}

    if isinstance(payload, str):
        try:
            progress = normalize_progress(float(payload))
            return {"progress": progress, "label": f"{int(progress * 100)}%"}
        except ValueError:
            return {"label": payload}

    return {"label": str(payload)}


def slugify(name: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_")
    return cleaned or "item"


def normalize_demand_name(name: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9_]+", "", name.strip().lower())
    for demand in FIXED_DEMANDS:
        candidate = re.sub(r"[^a-z0-9_]+", "", demand.lower())
        if normalized == candidate:
            return demand
    return None


def normalize_emotion_name(name: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9_]+", "", name.strip().lower())
    if normalized.endswith("value"):
        normalized = normalized[: -len("value")]
    for emotion in FIXED_EMOTIONS:
        candidate = re.sub(r"[^a-z0-9_]+", "", emotion.lower())
        if normalized == candidate:
            return emotion
    return None


def update_metric_section(
    parent_tag: str,
    section_prefix: str,
    values: dict[str, float],
    row_tags: dict[str, tuple[str, str, str]],
    bar_width: int = METRIC_BAR_WIDTH,
) -> None:
    # Remove rows that no longer exist in the newest event.
    stale_keys = [key for key in row_tags if key not in values]
    for key in stale_keys:
        dpg.delete_item(row_tags[key][0])
        del row_tags[key]

    for name, value in values.items():
        clamped_value = clamp_progress(float(value))
        if name not in row_tags:
            safe_name = slugify(name)
            row_tag = f"{section_prefix}_row_{safe_name}"
            bar_tag = f"{section_prefix}_bar_{safe_name}"
            label_tag = f"{section_prefix}_label_{safe_name}"
            # Ensure uniqueness when names normalize to the same slug.
            suffix = 2
            while dpg.does_item_exist(row_tag):
                row_tag = f"{section_prefix}_row_{safe_name}_{suffix}"
                bar_tag = f"{section_prefix}_bar_{safe_name}_{suffix}"
                label_tag = f"{section_prefix}_label_{safe_name}_{suffix}"
                suffix += 1

            with dpg.table_row(parent=parent_tag, tag=row_tag):
                dpg.add_text(default_value=name, tag=label_tag)
                dpg.add_progress_bar(
                    default_value=clamped_value,
                    width=bar_width,
                    overlay=f"{int(clamped_value * 100)}%",
                    tag=bar_tag,
                )
            row_tags[name] = (row_tag, label_tag, bar_tag)
        else:
            _, label_tag, bar_tag = row_tags[name]
            dpg.set_value(label_tag, name)
            dpg.set_value(bar_tag, clamped_value)
            dpg.configure_item(bar_tag, overlay=f"{int(clamped_value * 100)}%")


def tcp_listener(host: str, port: int, updates: queue.Queue, stop_event: threading.Event) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.settimeout(1.0)
    updates.put({"label": f"Listening on {host}:{port}"})

    try:
        while not stop_event.is_set():
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue

            updates.put({"label": f"Connected: {addr[0]}:{addr[1]}"})
            conn.settimeout(1.0)
            buffer = ""

            with conn:
                while not stop_event.is_set():
                    try:
                        chunk = conn.recv(1024)
                    except socket.timeout:
                        continue

                    if not chunk:
                        updates.put({"label": "Listening for updates"})
                        break

                    buffer += chunk.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        update = parse_update(line)
                        if update:
                            updates.put(update)
    finally:
        server.close()


def get_screen_size() -> tuple[int, int]:
    try:
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception:
        return 1280, 720


def run_dashboard(host: str, port: int) -> None:
    updates: queue.Queue = queue.Queue()
    stop_event = threading.Event()

    listener_thread = threading.Thread(
        target=tcp_listener,
        args=(host, port, updates, stop_event),
        daemon=True,
    )
    listener_thread.start()

    viewport_width = 480
    viewport_height = 380
    margin = 20
    screen_width, screen_height = get_screen_size()
    x_pos = max(0, screen_width - viewport_width - margin)
    y_pos = max(0, screen_height - viewport_height - margin)

    dpg.create_context()
    with dpg.window(
        tag="main_window",
        label="State Changes",
        no_resize=True,
        no_move=True,
        no_collapse=True,
    ):
        dpg.add_text(default_value="Starting...", tag="status_text")
        dpg.add_separator()
        dpg.add_text("Demands")
        with dpg.table(
            tag="demands_container",
            header_row=False,
            policy=dpg.mvTable_SizingFixedFit,
            borders_innerH=False,
            borders_outerH=False,
            borders_innerV=False,
            borders_outerV=False,
        ):
            dpg.add_table_column(init_width_or_weight=110, width_fixed=True)
            dpg.add_table_column(init_width_or_weight=METRIC_BAR_WIDTH, width_fixed=True)
        dpg.add_separator()
        dpg.add_text(default_value="Action: (none)", tag="action_text")

    dpg.create_viewport(
        title="OpenPsi Stats",
        width=viewport_width,
        height=viewport_height,
        x_pos=x_pos,
        y_pos=y_pos,
        always_on_top=True,
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    demand_row_tags: dict[str, tuple[str, str, str]] = {}
    initial_demand_value = 1.0 / len(FIXED_DEMANDS)
    demand_state: dict[str, float] = {name: initial_demand_value for name in FIXED_DEMANDS}
    update_metric_section(
        parent_tag="demands_container",
        section_prefix="demand",
        values=demand_state,
        row_tags=demand_row_tags,
    )

    try:
        while dpg.is_dearpygui_running():
            while not updates.empty():
                update = updates.get_nowait()
                if "demands" in update and isinstance(update["demands"], dict):
                    for raw_name, value in update["demands"].items():
                        if not isinstance(raw_name, str):
                            continue
                        normalized_name = normalize_demand_name(raw_name)
                        if normalized_name is None:
                            continue
                        demand_state[normalized_name] = clamp_progress(float(value))
                    update_metric_section(
                        parent_tag="demands_container",
                        section_prefix="demand",
                        values=demand_state,
                        row_tags=demand_row_tags,
                    )
                if "action" in update:
                    dpg.set_value("action_text", f"Action: {update['action']}")
                if "progress" in update:
                    progress = float(update["progress"])
                    demand_state["Energy"] = clamp_progress(progress)
                    update_metric_section(
                        parent_tag="demands_container",
                        section_prefix="demand",
                        values=demand_state,
                        row_tags=demand_row_tags,
                    )
                if "label" in update:
                    dpg.set_value("status_text", str(update["label"]))
            dpg.render_dearpygui_frame()
    finally:
        stop_event.set()
        listener_thread.join(timeout=1.0)
        dpg.destroy_context()


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal TCP state-change dashboard")
    parser.add_argument(
        "--host",
        default=os.getenv("OPENPSI_DASHBOARD_HOST", "127.0.0.1"),
        help="TCP host to listen on",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("OPENPSI_DASHBOARD_PORT", "5001")),
        help="TCP port to listen on",
    )
    args = parser.parse_args()
    run_dashboard(args.host, args.port)


if __name__ == "__main__":
    main()