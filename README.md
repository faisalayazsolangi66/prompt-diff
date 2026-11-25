# prompt-diff

Run two prompts against the OpenAI API and show both outputs side by
side — useful for comparing prompt phrasings, system messages, or
models.

## Requirements

- Python 3.8+
- No third-party packages (standard library only; API calls use `urllib`)
- An OpenAI account with API access

## API key

The API key is read **only** from the `OPENAI_API_KEY` environment
variable. Never hardcode a key in a file, and never share it.

```bash
export OPENAI_API_KEY='sk-...'
```

If the variable is not set, the tool exits with a clear error and does
not call the API.

## Usage

```bash
python3 main.py "Explain recursion simply." "Explain recursion like a professor."
python3 main.py --file-a a.txt --file-b b.txt -o diff.txt
python3 main.py "Write a tagline." "Write a tagline." --system-b "You are a witty copywriter."
python3 main.py "Hello" "Hello" --model-b gpt-4o
```

Options:

- `prompt_a`, `prompt_b` — the two prompts to compare
- `--file-a`, `--file-b` — read a prompt from a file instead
- `-m, --model` — model for both prompts (default: gpt-4o-mini)
- `--model-b` — different model for prompt B
- `-s, --system` — system message for both
- `--system-b` — different system message for prompt B
- `-t, --temperature` — sampling temperature 0–2 (default: 0.7)
- `--max-tokens` — maximum tokens per reply (default: 500)
- `-o, --output` — save both outputs to a file
- `--label-a`, `--label-b` — column labels (default: Prompt A / Prompt B)

## Example

```bash
$ export OPENAI_API_KEY='sk-...'
$ python3 main.py "Explain recursion in one sentence." "Explain recursion in one sentence, as a joke."
```

Sample output (side by side in a wide terminal):

```
Prompt A                                           | Prompt B
----------------------------------------------------------------------------------------------------
Recursion is when a function calls itself to solve  | Why did the function call itself? Because it
a smaller piece of the same problem.                 | had a recursion problem — it just kept calling
                                                     | itself until it hit the base case.
```

## License

MIT — see [LICENSE](LICENSE).
