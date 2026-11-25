#!/usr/bin/env python3
"""Run two prompts against the OpenAI API and show both outputs side by side.

Useful for comparing prompt phrasings, system messages, or models.
The API key is read ONLY from the OPENAI_API_KEY environment variable.
Never hardcode a key. Uses urllib from the standard library only.
"""
import argparse
import json
import os
import shutil
import sys
import textwrap
import urllib.error
import urllib.request

API_URL = "https://api.openai.com/v1/chat/completions"


def get_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY is not set.", file=sys.stderr)
        print("Set it before running this tool, for example:", file=sys.stderr)
        print("  export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        print("Never paste your key into a file or share it.", file=sys.stderr)
        return None
    return key


def call_openai(api_key, prompt, model, temperature, max_tokens, system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    request = urllib.request.Request(
        API_URL, data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Error: OpenAI API returned HTTP {exc.code}: {body}",
              file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"Error: could not reach the OpenAI API: {exc}", file=sys.stderr)
        return None
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"Error: unexpected API response: {data}", file=sys.stderr)
        return None


def side_by_side(left_title, left_text, right_title, right_text):
    """Render two texts in two columns, falling back to stacked output."""
    width = shutil.get_terminal_size(fallback=(100, 24)).columns
    if width < 80:
        return (f"=== {left_title} ===\n{left_text}\n\n"
                f"=== {right_title} ===\n{right_text}\n")
    col = (width - 3) // 2
    left_lines, right_lines = [], []
    for line in left_text.splitlines() or [""]:
        left_lines.extend(textwrap.wrap(line, col) or [""])
    for line in right_text.splitlines() or [""]:
        right_lines.extend(textwrap.wrap(line, col) or [""])
    header = f"{left_title[:col]:<{col}} | {right_title[:col]}"
    divider = "-" * width
    rows = [header, divider]
    for i in range(max(len(left_lines), len(right_lines))):
        left = left_lines[i] if i < len(left_lines) else ""
        right = right_lines[i] if i < len(right_lines) else ""
        rows.append(f"{left:<{col}} | {right}")
    return "\n".join(rows) + "\n"


def read_prompt(value, file_arg):
    if file_arg:
        with open(file_arg, encoding="utf-8") as f:
            return f.read()
    return value


def main():
    parser = argparse.ArgumentParser(
        description="Run two prompts against the OpenAI API and show both "
                    "outputs side by side. The API key comes from the "
                    "OPENAI_API_KEY environment variable only.")
    parser.add_argument("prompt_a", help="First prompt.")
    parser.add_argument("prompt_b", help="Second prompt.")
    parser.add_argument("--file-a", help="Read prompt A from this file.")
    parser.add_argument("--file-b", help="Read prompt B from this file.")
    parser.add_argument("-m", "--model", default="gpt-4o-mini",
                        help="Model for both prompts (default: gpt-4o-mini).")
    parser.add_argument("--model-b", help="Different model for prompt B.")
    parser.add_argument("-s", "--system", help="System message for both.")
    parser.add_argument("--system-b", help="Different system message for B.")
    parser.add_argument("-t", "--temperature", type=float, default=0.7,
                        help="Sampling temperature 0-2 (default: 0.7).")
    parser.add_argument("--max-tokens", type=int, default=500,
                        help="Maximum tokens per reply (default: 500).")
    parser.add_argument("-o", "--output", help="Save both outputs to this "
                        "file (stacked, with headings).")
    parser.add_argument("--label-a", default="Prompt A",
                        help="Label for the first output (default: Prompt A).")
    parser.add_argument("--label-b", default="Prompt B",
                        help="Label for the second output (default: Prompt B).")
    args = parser.parse_args()

    api_key = get_api_key()
    if api_key is None:
        return 1

    try:
        prompt_a = read_prompt(args.prompt_a, args.file_a)
        prompt_b = read_prompt(args.prompt_b, args.file_b)
    except OSError as exc:
        print(f"Error: cannot read prompt file: {exc}", file=sys.stderr)
        return 1

    print("Running prompt A...", file=sys.stderr)
    out_a = call_openai(api_key, prompt_a, args.model, args.temperature,
                        args.max_tokens, args.system)
    if out_a is None:
        return 1
    print("Running prompt B...", file=sys.stderr)
    out_b = call_openai(api_key, prompt_b, args.model_b or args.model,
                        args.temperature, args.max_tokens,
                        args.system_b or args.system)
    if out_b is None:
        return 1

    rendered = side_by_side(args.label_a, out_a, args.label_b, out_b)
    print(rendered, end="")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"=== {args.label_a} ===\nPrompt: {prompt_a}\n\n"
                    f"{out_a}\n\n=== {args.label_b} ===\n"
                    f"Prompt: {prompt_b}\n\n{out_b}\n")
        print(f"Saved both outputs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
