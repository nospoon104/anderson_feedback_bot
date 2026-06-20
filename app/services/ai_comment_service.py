import json
from collections import defaultdict

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

    @staticmethod
    def _normalize_network_comments(
        comments_by_cafe: list[dict[str, str | int]],
    ) -> list[dict[str, str | int]]:
        normalized: list[dict[str, str | int]] = []

        for item in comments_by_cafe:
            comment = str(item["comment"]).strip()
            if not comment:
                continue

            normalized.append(
                {
                    "cafe_id": item["cafe_id"],
                    "cafe_name": str(item["cafe_name"]).strip(),
                    "comment": comment,
                }
            )

        return normalized

    @staticmethod
    def _limit_network_comments(
        comments_by_cafe: list[dict[str, str | int]],
        max_comments_per_cafe: int = 20,
        max_total_comments: int = 150,
    ) -> list[dict[str, str | int]]:
        grouped: dict[str, list[dict[str, str | int]]] = defaultdict(list)

        for item in comments_by_cafe:
            cafe_key = f'{item["cafe_id"]}:{item["cafe_name"]}'
            if len(grouped[cafe_key]) < max_comments_per_cafe:
                grouped[cafe_key].append(item)

        limited: list[dict[str, str | int]] = []
        for items in grouped.values():
            limited.extend(items)

        return limited[:max_total_comments]

    @staticmethod
    def _build_network_prompt(comments_by_cafe: list[dict[str, str | int]]) -> str:
        grouped: dict[str, list[str]] = defaultdict(list)

        for item in comments_by_cafe:
            cafe_name = str(item["cafe_name"])
            comment = str(item["comment"])
            grouped[cafe_name].append(comment)

        blocks: list[str] = []
        for cafe_name, comments in grouped.items():
            comment_lines = "\n".join(f"- {comment}" for comment in comments)
            blocks.append(f"Кафе: {cafe_name}\nКомментарии:\n{comment_lines}")

        comments_block = "\n\n".join(blocks)

        return f"""
Ты анализируешь комментарии гостей по всей сети ресторанов за выбранный период.

Тебе переданы комментарии с разбивкой по кафе.
Нужно подготовить краткий, честный и полезный управленческий анализ для суперюзера сети.

Требования:
1. Не выдумывай факты.
2. Не додумывай то, чего нет в комментариях.
3. Опирайся только на комментарии из входных данных.
4. Если комментариев мало, прямо скажи, что выборка ограничена.
5. Отделяй общесетевые сигналы от локальных проблем конкретных кафе.
6. Упоминай конкретные кафе только если в комментариях действительно есть основания обратить на них внимание.
7. Если по кафе мало данных, не делай сильных выводов.
8. Выдели повторяющиеся позитивные сигналы по сети.
9. Выдели повторяющиеся проблемы по сети.
10. Отдельно укажи кафе, которые требуют внимания руководителя, и объясни почему.
11. Пиши кратко, структурно, по делу и на русском языке.
12. Не используй расплывчатые формулировки без опоры на текст комментариев.

Верни ответ СТРОГО в таком формате:

Общая картина по сети:
- ...
- ...

Сильные стороны по сети:
- ...
- ...

Системные проблемы по сети:
- ...
- ...

Кафе, требующие внимания:
- [Название кафе]: ...
- [Название кафе]: ...

На что обратить внимание руководителю:
- ...
- ...

Краткий вывод:
- ...

Комментарии по кафе:
{comments_block}
        """.strip()

    async def _request_ai(self, user_prompt: str, system_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
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
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected AI response format: {json.dumps(data, ensure_ascii=False)}"
            ) from exc

    async def analyze_comments(self, comments: list[str]) -> str:
        normalized_comments = self._normalize_comments(comments)
        limited_comments = self._limit_comments(normalized_comments)

        if not limited_comments:
            return (
                "AI-анализ комментариев\n\n"
                "За выбранный период нет комментариев для анализа."
            )

        content = await self._request_ai(
            user_prompt=self._build_prompt(limited_comments),
            system_prompt=(
                "Ты аккуратный аналитик клиентского опыта в ресторанах. "
                "Отвечай кратко, структурно и по делу на русском языке."
            ),
        )

        return f"AI-анализ комментариев\n\n{content}"

    async def analyze_network_comments(
        self,
        comments_by_cafe: list[dict[str, str | int]],
    ) -> str:
        normalized_comments = self._normalize_network_comments(comments_by_cafe)
        limited_comments = self._limit_network_comments(normalized_comments)

        if not limited_comments:
            return (
                "AI-анализ комментариев по сети\n\n"
                "За выбранный период нет комментариев для анализа по сети."
            )

        content = await self._request_ai(
            user_prompt=self._build_network_prompt(limited_comments),
            system_prompt=(
                "Ты аккуратный аналитик клиентского опыта для сети ресторанов. "
                "Готовишь управленческие выводы для суперюзера. "
                "Отвечай кратко, структурно, честно и строго по входным комментариям на русском языке."
            ),
        )

        return f"AI-анализ комментариев по сети\n\n{content}"
