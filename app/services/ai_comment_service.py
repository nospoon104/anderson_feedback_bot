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

    @staticmethod
    def _prepare_network_cafes(
        comments_by_cafe: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        prepared: list[dict[str, object]] = []

        for item in comments_by_cafe:
            cafe_name = str(item["cafe_name"]).strip()
            total_surveys = int(item["total_surveys"])
            average_percent = float(item["average_percent"])
            comments_count = int(item["comments_count"])
            raw_comments = item.get("comments", [])

            comments: list[str] = []
            if isinstance(raw_comments, list):
                for comment in raw_comments:
                    cleaned = str(comment).strip()
                    if cleaned:
                        comments.append(cleaned)

            prepared.append(
                {
                    "cafe_id": int(item["cafe_id"]),
                    "cafe_name": cafe_name,
                    "total_surveys": total_surveys,
                    "average_percent": average_percent,
                    "comments_count": comments_count,
                    "comments": comments,
                }
            )

        return prepared

    @staticmethod
    def _build_network_prompt(
        cafes: list[dict[str, object]],
        network_average_percent: float,
        total_cafes: int,
        total_surveys: int,
    ) -> str:
        cafe_blocks: list[str] = []

        for cafe in cafes:
            comments = cafe["comments"]
            comments_block = (
                "\n".join(f"- {comment}" for comment in comments)
                if comments
                else "- Комментариев нет"
            )

            cafe_blocks.append(
                f"""Кафе: {cafe["cafe_name"]}
- Количество анкет: {cafe["total_surveys"]}
- Средний процент: {float(cafe["average_percent"]):.2f}%
- Количество комментариев: {cafe["comments_count"]}
Комментарии:
{comments_block}"""
            )

        cafes_block = "\n\n".join(cafe_blocks)

        return f"""
Ты анализируешь отчёт по сети ресторанов за выбранный период.

Ниже приведены данные по всей сети:
- Количество кафе в отчёте: {total_cafes}
- Общее количество анкет по сети: {total_surveys}
- Средний процент по сети: {network_average_percent:.2f}%

Также ниже приведены данные по каждому кафе:
- количество анкет,
- средний процент,
- количество комментариев,
- сами комментарии гостей.

Твоя задача — сделать честный, полезный и краткий управленческий анализ для суперюзера сети.

Требования:
1. Не выдумывай факты.
2. Не додумывай то, чего нет во входных данных.
3. Опирайся только на показатели и комментарии, которые переданы ниже.
4. Если данных мало, прямо скажи, что выборка ограничена.
5. Разделяй общесетевые сигналы и локальные проблемы конкретных кафе.
6. Указывай кафе, требующие внимания, только если на это есть основания:
   - низкий средний процент относительно сети,
   - повторяющиеся жалобы,
   - сочетание слабых метрик и негативных комментариев.
7. Не делай жёстких выводов по кафе, если данных слишком мало.
8. Если по кафе нет комментариев, не придумывай причины проблем.
9. Выдели сильные стороны по сети.
10. Выдели системные проблемы по сети.
11. Отдельно укажи кафе, требующие внимания руководителя.
12. Если кафе требует внимания, кратко объясни почему.
13. Пиши по делу, кратко, структурно и на русском языке.

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

Данные по кафе:
{cafes_block}
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
        comments_by_cafe: list[dict[str, object]],
        network_average_percent: float,
        total_cafes: int,
        total_surveys: int,
    ) -> str:
        cafes = self._prepare_network_cafes(comments_by_cafe)

        cafes_with_signal = [
            cafe
            for cafe in cafes
            if cafe["total_surveys"] > 0 or cafe["comments_count"] > 0
        ]

        if not cafes_with_signal:
            return (
                "AI-анализ комментариев по сети\n\n"
                "За выбранный период нет данных для анализа по сети."
            )

        content = await self._request_ai(
            user_prompt=self._build_network_prompt(
                cafes=cafes_with_signal,
                network_average_percent=network_average_percent,
                total_cafes=total_cafes,
                total_surveys=total_surveys,
            ),
            system_prompt=(
                "Ты аккуратный аналитик клиентского опыта для сети ресторанов. "
                "Готовишь управленческие выводы для суперюзера. "
                "Отвечай кратко, структурно, честно и строго по входным данным "
                "на русском языке."
            ),
        )

        return f"AI-анализ комментариев по сети\n\n{content}"
