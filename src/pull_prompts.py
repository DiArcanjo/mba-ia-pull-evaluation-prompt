"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import sys
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def extract_messages(prompt) -> dict:
    messages = {"system_prompt": "", "user_prompt": ""}

    for message in prompt.messages:
        template = message.prompt.template
        message_type = type(message).__name__

        if message_type.startswith("System"):
            messages["system_prompt"] = template
        elif message_type.startswith("Human"):
            messages["user_prompt"] = template

    return messages


def pull_prompts_from_langsmith() -> bool:
    print(f"Fazendo pull de: {SOURCE_PROMPT}")

    try:
        client = Client()
        prompt = client.pull_prompt(SOURCE_PROMPT, dangerously_pull_public_prompt=True)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    messages = extract_messages(prompt)
    if not messages["system_prompt"]:
        print("❌ O prompt retornado não possui mensagem de sistema")
        return False

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": messages["system_prompt"],
            "user_prompt": messages["user_prompt"],
            "version": "v1",
            "source": SOURCE_PROMPT,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(data, OUTPUT_PATH):
        return False

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
