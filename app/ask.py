"""第1回: 会話履歴を保持してLLMと対話するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"  # 最初の質問を指定して対話開始
    uv run python -m app.ask                       # 既定の質問から対話開始

会話履歴を保ったまま続けて質問できます。
終了するには 'exit', 'quit', 'q' を入力するか、Ctrl+C を押してください。
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    """単発の質問を行う（互換性のために維持）。"""
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    if response.usage_metadata:
        in_tokens = response.usage_metadata.prompt_token_count
        out_tokens = response.usage_metadata.candidates_token_count
        print(f"[トークン数] 入力: {in_tokens} / 出力: {out_tokens}\n")

    return response.text


def interactive_chat(initial_question: str | None = None) -> None:
    """会話履歴を保持しながら対話的に質問を続ける。"""
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)

    def _send_and_print(prompt: str) -> None:
        try:
            response = chat.send_message(prompt)
            if response.usage_metadata:
                in_tokens = response.usage_metadata.prompt_token_count
                out_tokens = response.usage_metadata.candidates_token_count
                print(f"[トークン数] 入力: {in_tokens} / 出力: {out_tokens}\n")
            print(response.text)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))

    print(f"[model] {MODEL}")
    print("会話モードを開始します。（終了するには 'exit', 'quit', または 'q' と入力してください）\n")

    question = initial_question if initial_question is not None else DEFAULT_QUESTION
    print(f"[質問] {question}\n")
    _send_and_print(question)

    while True:
        try:
            print("-" * 50)
            user_input = input("\n[続けて質問] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n対話を終了します。")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("対話を終了します。")
            break

        print(f"\n[質問] {user_input}\n")
        _send_and_print(user_input)


def main() -> None:
    parser = argparse.ArgumentParser(description="LLMと対話形式で質問する")
    parser.add_argument("question", nargs="?", default=None, help="最初の質問（省略時は講座の既定質問から開始）")
    args = parser.parse_args()

    interactive_chat(args.question)


if __name__ == "__main__":
    main()
