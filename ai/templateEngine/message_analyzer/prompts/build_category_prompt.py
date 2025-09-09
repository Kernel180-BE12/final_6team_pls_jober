from ai.templateEngine.message_analyzer.prompts.base_prompt_builder import BasePromptBuilder

class CategoryPromptBuilder(BasePromptBuilder):
    def __init__(self, user_text: str, category_main: str, category_sub_list: list):
        super().__init__(user_text)
        self.hints: list[dict] = []
        self.category_main = category_main
        self.category_sub_list = category_sub_list
    
    def build(self) -> list:
        prompt = [
            {
                "role": "system",
                "content": """
        너는 카카오 알림톡의 서브 카테고리를 판정하는 분류기다.
        [서브 카테고리 판정 규칙] 
        - 입력된 본문을 읽고, 아래 제공된 서브 카테고리 리스트 중 가장 유사한 하나를 반드시 선택한다. 
        - 리스트에 없는 임의의 값을 생성하지 않는다.  
        [서브 카테고리 판정 원칙]
        1) 먼저 사용자 본문 내용과 가장 적절한 서브 카테고리를 고른다.
        2) 애매하면 가장 합리적인 단일 유형을 고르고 이유를 간단히 남긴다.  
        [출력 형식(JSON만 출력)]
        {
        "category_sub": "리스트 중 하나",
        "explain_category_sub": "한 줄 이유"
        }
        """
            },
            {
                "role": "user",
                "content": f"""
        [입력]: 
        본문: {self.user_text}
        카테고리(대분류): {self.category_main} 
        카테고리(소분류 후보): {self.category_sub_list}          
        """
            },
            *self._build_hint_messages()
        ]
        return prompt