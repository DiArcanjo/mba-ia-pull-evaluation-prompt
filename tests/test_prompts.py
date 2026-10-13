"""
Testes automatizados para validação de prompts.
"""
import re
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    return load_prompts(PROMPT_FILE)["bug_to_user_story_v2"]


@pytest.fixture(scope="module")
def system_prompt(prompt):
    return prompt.get("system_prompt", "")


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(r"Você é um[a]? ", system_prompt)
        assert "Product Manager" in system_prompt

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "Como um" in system_prompt
        assert "eu quero" in system_prompt
        assert "para que" in system_prompt
        assert "Critérios de Aceitação" in system_prompt
        assert all(word in system_prompt for word in ["Dado que", "Quando", "Então"])

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        examples = re.findall(r"Exemplo \d", system_prompt)
        assert len(examples) >= 2
        assert system_prompt.count("Relato:") >= len(examples)
        assert system_prompt.count("Resposta:") >= len(examples)

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        content = PROMPT_FILE.read_text(encoding="utf-8")
        assert "[TODO]" not in content
        assert "TODO" not in prompt["system_prompt"]
        assert "TODO" not in prompt["user_prompt"]

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2
        assert "Few-shot Learning" in techniques

    def test_user_prompt_has_bug_report_variable(self, prompt):
        assert "{bug_report}" in prompt["user_prompt"]
        assert "{bug_report}" not in prompt["system_prompt"]

    def test_prompt_structure_is_valid(self, prompt):
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
