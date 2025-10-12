from __future__ import annotations

import os
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from .agent import create_agent
from .safety import safety_disclaimer
from .tools import add_journal_entry, recent_entries, log_mood, mood_summary, suggest_strategies

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command()
def chat(model: Optional[str] = typer.Option(None, help="Model name for Gemini or ADK")) -> None:
    """Start an interactive chat with the pocket therapist agent."""
    agent = create_agent(model=model)
    console.print(Markdown(f"**Disclaimer:** {safety_disclaimer()}"))
    console.print("Type '/help' for commands. Press Ctrl+C to exit.\n")

    history = []
    while True:
        try:
            user_text = typer.prompt("you")
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye. Take care.")
            raise typer.Exit(0)

        if user_text.strip() == "":
            continue

        if user_text.startswith("/"):
            handled = _handle_slash_command(user_text)
            if handled:
                continue

        reply = agent.reply(user_text, history=history)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})
        console.print(Markdown(reply))


def _handle_slash_command(text: str) -> bool:
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd in {"/help", "/?"}:
        console.print(Markdown(
            """
            Commands:
            - `/journal <text>`: Save a private journal entry
            - `/recent [n]`: Show last n journal entries (default 5)
            - `/mood <label> <1-10>`: Log your mood
            - `/moodsum [n]`: Show average intensity per mood over last n logs (default 20)
            - `/plan <mood>`: Suggest 2-3 coping strategies for a mood
            - `/help`: Show this help
            """
        ))
        return True

    if cmd == "/journal" and len(parts) >= 2:
        entry_text = text[len("/journal"):].strip()
        entry = add_journal_entry(entry_text)
        console.print(f"Saved journal entry at {entry.timestamp_iso}")
        return True

    if cmd == "/recent":
        n = 5
        if len(parts) >= 2 and parts[1].isdigit():
            n = int(parts[1])
        entries = recent_entries(limit=n)
        if not entries:
            console.print("No entries yet.")
            return True
        for e in entries:
            console.print(Markdown(f"- {e.timestamp_iso}: {e.text}"))
        return True

    if cmd == "/mood" and len(parts) >= 3:
        label = parts[1]
        try:
            intensity = int(parts[2])
        except Exception:
            console.print("Intensity must be an integer 1-10.")
            return True
        try:
            entry = log_mood(label, intensity)
            console.print(f"Logged mood '{entry.mood}'={entry.intensity} at {entry.timestamp_iso}")
        except Exception as e:
            console.print(str(e))
        return True

    if cmd == "/moodsum":
        n = 20
        if len(parts) >= 2 and parts[1].isdigit():
            n = int(parts[1])
        summary = mood_summary(limit=n)
        if not summary:
            console.print("No mood logs yet.")
            return True
        console.print(Markdown("\n".join(f"- {m}: {avg:.2f}" for m, avg in summary.items())))
        return True

    if cmd == "/plan" and len(parts) >= 2:
        mood = parts[1]
        strategies = suggest_strategies(mood)
        for s in strategies[:3]:
            console.print(Markdown(f"- {s}"))
        return True

    return False
