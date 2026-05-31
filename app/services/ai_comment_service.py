import json

import httpx

from app.core.config import settings


class AICommentService:
    def __init__(self) -> None:
        self.api_key = settings.ai_api_key
        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.ai_model
        self.timeout = settings.ai_timeout

    @staticmethod
    def _normalize_comments(comments: list[str]) -> list[str]:
        normalized: list[str] = []

        for comment in comments:
            cleaned = comment.strip()
            if cleaned:
                normalized.append(cleaned)

        return normalized

    @staticmethod
    def _limit_comments(comments: list[str], max_comments: int = 100) -> list[str]:
        return comments[:max_comments]

    @staticmethod
    def _build_prompt(comments: list[str]) -> str:
        comments_block = "\n".join(
            f"{index}. {comment}" for index, comment in enumerate(comments, start=1)
        )

        return f"""
Ты анализируешь комментарии гостей ресторана за выбранный период.

Ниже приведён список комментариев гостей.
Сделай короткий, полезный и честный управленческий анализ на русском языке.

Требования:
1. Не выдумывай факты.
2. Не додумывай то, чего нет в комментариях.
3. Опирайся только на комментарии.
4. Если комментариев мало, прямо скажи, что выборка ограничена.
5. Если есть повторяющиеся жалобы, выдели их отдельно.
6. Если есть позитивные сигналы, тоже выдели их.
7. Пиши кратко, структурно и по делу.
8. Не используй слишком общие фразы без опоры на текст комментариев.

Верни ответ СТРОГО в таком формате:

Позитивные сигналы:
- ...
- ...

Проблемы и жалобы:
- ...
- ...

На что обратить внимание:
- ...
- ...

Краткий вывод:
- ...

Комментарии:
{comments_block}
        """.strip()

    async def analyze_comments(self, comments: list[str]) -> str:
        normalized_comments = self._normalize_comments(comments)
        limited_comments = self._limit_comments(normalized_comments)

        if not limited_comments:
            return (
                "AI-анализ комментариев\n\n"
                "За выбранный период нет комментариев для анализа."
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты аккуратный аналитик клиентского опыта в ресторанах. "
                        "Отвечай кратко, структурно и по делу на русском языке."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(limited_comments),
                },
            ],
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        try:
            content = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected AI response format: {json.dumps(data, ensure_ascii=False)}"
            ) from exc

        return f"AI-анализ комментариев\n\n{content}"
