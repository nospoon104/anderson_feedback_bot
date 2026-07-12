import json

import httpx

from app.core.config import settings


class AICommentService:
    NEGATIVE_TAGS = {
        "hall": "Зал",
        "kitchen_food": "Кухня/блюда",
        "kitchen_speed": "Кухня/скорость",
        "service": "Сервис",
        "bar": "Бар",
        "general": "Общие",
    }

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
    def _limit_text_items(items: list[str], max_items: int) -> list[str]:
        return items[:max_items]

    @staticmethod
    def _limit_comments(comments: list[str], max_comments: int = 100) -> list[str]:
        return comments[:max_comments]

    @staticmethod
    def _chunk_comments(comments: list[str], chunk_size: int = 20) -> list[list[str]]:
        return [
            comments[index : index + chunk_size]
            for index in range(0, len(comments), chunk_size)
        ]

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

    async def analyze_network_executive_report(
        self,
        total_cafes: int,
        total_surveys: int,
        average_percent: float,
        previous_total_surveys: int,
        comments_count: int,
        previous_comments_count: int,
        question_comparisons: list[dict[str, object]],
        weekly_points: list[dict[str, object]],
        monthly_points: list[dict[str, object]],
        negative_tag_summary: list[dict[str, object]],
        previous_negative_tag_summary: list[dict[str, object]],
        cafes: list[dict[str, object]],
        negative_by_cafe: list[dict[str, object]],
        representative_comments: list[str],
    ) -> str:
        if total_surveys == 0 and comments_count == 0:
            return (
                "Глубокий AI-анализ сети\n\n"
                "За выбранный период нет данных для управленческого анализа."
            )

        limited_comments = self._limit_text_items(representative_comments, max_items=20)

        content = await self._request_ai(
            user_prompt=self._build_network_executive_prompt(
                total_cafes=total_cafes,
                total_surveys=total_surveys,
                average_percent=average_percent,
                previous_total_surveys=previous_total_surveys,
                comments_count=comments_count,
                previous_comments_count=previous_comments_count,
                question_comparisons=question_comparisons,
                weekly_points=weekly_points,
                monthly_points=monthly_points,
                negative_tag_summary=negative_tag_summary,
                previous_negative_tag_summary=previous_negative_tag_summary,
                cafes=cafes,
                negative_by_cafe=negative_by_cafe,
                representative_comments=limited_comments,
            ),
            system_prompt=(
                "Ты аккуратный аналитик для управляющей команды сети ресторанов. "
                "Готовишь краткий executive summary. "
                "Отвечай строго по данным, кратко, честно, структурно, на русском языке."
            ),
        )

        return f"Глубокий AI-анализ сети\n\n{content}"

    @staticmethod
    def _build_tagging_prompt(comments: list[str]) -> str:
        comments_block = "\n".join(
            f"{index}. {comment}" for index, comment in enumerate(comments, start=1)
        )

        return f"""
Ты классифицируешь комментарии гостей ресторана.

Для каждого комментария нужно вернуть JSON-объект с полями:
- comment: исходный комментарий без изменений
- sentiment: только "positive" или "negative"
- tag:
  - если sentiment="positive", ставь только "positive"
  - если sentiment="negative", ставь только один из:
    "hall", "kitchen_food", "kitchen_speed", "service", "bar", "general"
- short_reason: короткая суть комментария на русском языке, до 8 слов

Правила:
1. Верни только JSON-массив.
2. Никакого markdown, никаких пояснений, никакого текста вне JSON.
3. Один комментарий = один объект.
4. Если комментарий смешанный, выбери главный смысл.
5. Если комментарий в целом хвалебный — sentiment="positive", tag="positive".
6. Если комментарий негативный — обязательно один негативный tag из списка.
7. Не выдумывай детали, которых нет в комментарии.
8. Сохраняй исходный текст комментария в поле comment.

Комментарии:
{comments_block}
""".strip()

    def _build_network_executive_prompt(
        self,
        total_cafes: int,
        total_surveys: int,
        average_percent: float,
        previous_total_surveys: int,
        comments_count: int,
        previous_comments_count: int,
        question_comparisons: list[dict[str, object]],
        weekly_points: list[dict[str, object]],
        monthly_points: list[dict[str, object]],
        negative_tag_summary: list[dict[str, object]],
        previous_negative_tag_summary: list[dict[str, object]],
        cafes: list[dict[str, object]],
        negative_by_cafe: list[dict[str, object]],
        representative_comments: list[str],
    ) -> str:
        question_block = "\n".join(
            f"- {item['question_label']}: текущий={item['current_yes_percent']}%, "
            f"предыдущий={item['previous_yes_percent']}%, "
            f"дельта={item['delta_percent_points']} п.п."
            for item in question_comparisons
        )

        weekly_block = "\n".join(
            f"- {item['label']}: анкет={item['total_surveys']}, "
            f"средний %={item['average_percent']}, комментариев={item['comments_count']}"
            for item in weekly_points
        )

        monthly_block = "\n".join(
            f"- {item['label']}: анкет={item['total_surveys']}, "
            f"средний %={item['average_percent']}, комментариев={item['comments_count']}"
            for item in monthly_points
        )

        current_tags_block = "\n".join(
            f"- {item['label']}: {item['count']}" for item in negative_tag_summary
        )

        previous_tags_block = "\n".join(
            f"- {item['label']}: {item['count']}"
            for item in previous_negative_tag_summary
        )

        cafes_block = "\n".join(
            f"- {item['cafe_name']}: анкет={item['total_surveys']}, "
            f"средний %={item['average_percent']}, "
            f"предыдущий %={item['previous_average_percent']}, "
            f"дельта={item['delta_percent_points']} п.п., "
            f"комментариев={item['comments_count']}"
            for item in cafes
        )

        negative_by_cafe_block = "\n".join(
            f"- {item['cafe_name']}: зал={item['hall_count']}, "
            f"кухня/блюда={item['kitchen_food_count']}, "
            f"кухня/скорость={item['kitchen_speed_count']}, "
            f"сервис={item['service_count']}, "
            f"бар={item['bar_count']}, "
            f"общие={item['general_count']}, "
            f"всего негативных={item['total_negative_count']}"
            for item in negative_by_cafe
        )

        comments_block = "\n".join(
            f"- {comment}" for comment in representative_comments
        )

        return f"""
Ты готовишь краткий управленческий анализ для суперюзера сети ресторанов.

Опирайся только на данные ниже. Не выдумывай факты и не додумывай причины, которых нет во входных данных.

Данные по сети:
- Кафе в отчёте: {total_cafes}
- Анкет в текущем периоде: {total_surveys}
- Анкет в предыдущем периоде: {previous_total_surveys}
- Средний процент в текущем периоде: {average_percent}%
- Комментариев в текущем периоде: {comments_count}
- Комментариев в предыдущем периоде: {previous_comments_count}

Сравнение по вопросам:
{question_block}

Недельная динамика:
{weekly_block}

Месячная динамика:
{monthly_block}

Негативные теги в текущем периоде:
{current_tags_block}

Негативные теги в предыдущем периоде:
{previous_tags_block}

Показатели по кафе:
{cafes_block}

Негатив по кафе и тегам:
{negative_by_cafe_block}

Показательные комментарии:
{comments_block}

Сделай краткий, честный и полезный управленческий анализ.
Если данных мало, прямо скажи об этом.
Если по отдельному кафе мало данных, не делай жёстких выводов.
Выделяй только те проблемы, которые реально подтверждаются цифрами, тегами или комментариями.

Верни ответ СТРОГО в таком формате:

Ключевые управленческие сигналы:
- ...
- ...

Что ухудшилось относительно предыдущего периода:
- ...
- ...

Какие проблемы повторяются по сети:
- ...
- ...

Какие кафе требуют внимания:
- [Название кафе]: ...
- [Название кафе]: ...

Что проверить территориальным управляющим:
- ...
- ...

Краткий вывод:
- ...
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

    @staticmethod
    def _safe_parse_tagging_response(
        response_text: str,
        source_comments: list[str],
    ) -> list[dict[str, str]]:
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            return [
                {
                    "comment": comment,
                    "sentiment": "negative",
                    "tag": "general",
                    "short_reason": "Не удалось распознать автоматически",
                }
                for comment in source_comments
            ]

        if not isinstance(parsed, list):
            return [
                {
                    "comment": comment,
                    "sentiment": "negative",
                    "tag": "general",
                    "short_reason": "Некорректный формат AI-ответа",
                }
                for comment in source_comments
            ]

        normalized_items: list[dict[str, str]] = []

        for index, comment in enumerate(source_comments):
            if index >= len(parsed) or not isinstance(parsed[index], dict):
                normalized_items.append(
                    {
                        "comment": comment,
                        "sentiment": "negative",
                        "tag": "general",
                        "short_reason": "Комментарий не был классифицирован",
                    }
                )
                continue

            raw_item = parsed[index]

            sentiment = str(raw_item.get("sentiment", "")).strip().lower()
            tag = str(raw_item.get("tag", "")).strip().lower()
            short_reason = str(raw_item.get("short_reason", "")).strip()

            if sentiment not in {"positive", "negative"}:
                sentiment = "negative"

            if sentiment == "positive":
                tag = "positive"
            elif tag not in {
                "hall",
                "kitchen_food",
                "kitchen_speed",
                "service",
                "bar",
                "general",
            }:
                tag = "general"

            if not short_reason:
                short_reason = "Без краткого описания"

            normalized_items.append(
                {
                    "comment": comment,
                    "sentiment": sentiment,
                    "tag": tag,
                    "short_reason": short_reason,
                }
            )

        return normalized_items

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

    async def tag_comments(self, comments: list[str]) -> list[dict[str, str]]:
        normalized_comments = self._normalize_comments(comments)

        if not normalized_comments:
            return []

        chunks = self._chunk_comments(normalized_comments, chunk_size=20)
        result: list[dict[str, str]] = []

        for chunk in chunks:
            response_text = await self._request_ai(
                user_prompt=self._build_tagging_prompt(chunk),
                system_prompt=(
                    "Ты классифицируешь комментарии гостей ресторана. "
                    "Возвращай только корректный JSON-массив без пояснений."
                ),
            )
            result.extend(
                self._safe_parse_tagging_response(
                    response_text=response_text,
                    source_comments=chunk,
                )
            )

        return result

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
