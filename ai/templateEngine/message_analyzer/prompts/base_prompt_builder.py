from abc import ABC, abstractmethod

class BasePromptBuilder(ABC):
    def __init__(self, user_text: str):
        self.user_text = user_text
        self.hints: list[dict] = []

    def add_hint(self, description: str, content: str|list):
        """모든 힌트는 system role"""
        self.hints.append({"description": description, "content": content})
        return self

    def _build_hint_messages(self) -> list[dict]:
        messages = []
        for h in self.hints:
            content = h["content"]
            if isinstance(content, list):
                content = ", ".join(content)
            messages.append({
                "role": "system",
                "content": f"[{h['description']}] {content}"
            })
        return messages


    @abstractmethod
    def build(self) -> list[dict]:
        """프롬프트 빌드 로직은 구체 빌더가 구현"""
        pass
