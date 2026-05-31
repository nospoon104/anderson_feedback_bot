# Anderson Feedback Bot

Telegram-бот для сети ресторанов, который оцифровывает бумажные анкеты гостей, сохраняет данные в PostgreSQL и формирует отчёты по отдельному кафе и по всей сети.

Проект сделан как рабочий коммерческий MVP: бот уже реализован, задеплоен на VPS и используется как внутренний инструмент для сбора и анализа обратной связи.

## О проекте

Во многих заведениях обратная связь от гостей продолжает собираться на бумаге. Это создаёт несколько типовых проблем:

- данные неудобно агрегировать;
- сложно быстро получить аналитику по кафе или по сети;
- комментарии гостей остаются в бумажном архиве;
- сравнение периодов приходится делать вручную или не делать вообще.

Этот бот решает задачу без отдельного web-интерфейса: менеджеры переносят анкеты в Telegram, данные сохраняются в PostgreSQL, а руководители получают структурированные отчёты и Excel-выгрузки.

## Основные возможности

- ввод анкет через Telegram-бота;
- роли `manager` и `superuser`;
- хранение данных в PostgreSQL;
- отчёт менеджера по своему кафе за выбранный период;
- отчёт суперпользователя по любому кафе;
- отчёт по всей сети;
- сравнение периода с предыдущим периодом той же длины;
- Excel-экспорт отчётов;
- AI-анализ комментариев гостей.

## Роли пользователей

### Manager

Может:

- вносить анкеты гостей;
- получать отчёт по своему кафе за период;
- получать Excel-файл с отчётом.

### Superuser

Может:

- получать отчёт по любому кафе;
- получать отчёт по всей сети;
- скачивать Excel-отчёты;
- использовать административные сценарии управления пользователями и данными.

## Бизнес-логика анкеты

Каждая анкета содержит:

- дату и время визита;
- номер стола;
- 4 вопроса с ответами `Да / Нет`;
- необязательный комментарий.

Логика подсчёта:

- `Да = 1`
- `Нет = 0`
- итоговый `score` = сумма 4 ответов
- перевод в проценты:
  - `4/4 = 100%`
  - `3/4 = 75%`
  - `2/4 = 50%`
  - `1/4 = 25%`
  - `0/4 = 0%`

Отчёты рассчитывают:

- общее количество анкет;
- средний балл;
- средний процент;
- статистику `Да / Нет` по каждому вопросу;
- распределение по итоговым оценкам;
- сравнение с предыдущим периодом той же длины.

Для отчёта по кафе дополнительно доступны:

- список комментариев;
- AI summary по комментариям гостей.

## Текущий статус

Сейчас проект находится на стадии рабочего MVP.

Уже реализовано:

- Telegram-бот на `aiogram 3`;
- FSM-сценарий ввода анкет;
- PostgreSQL + SQLAlchemy 2 async;
- Alembic миграции;
- роли `manager / superuser`;
- отчёты по кафе;
- отчёты по сети;
- Excel-экспорт;
- AI-анализ комментариев;
- Docker-сборка и deploy на VPS.

## Стек

- Python 3.12
- aiogram 3
- PostgreSQL
- SQLAlchemy 2 async
- asyncpg
- Alembic
- Pydantic 2
- openpyxl
- httpx
- Docker / Docker Compose

## Архитектура

Проект построен по слоистой схеме:

`handlers -> services -> repositories -> db`

Где:

- `handlers` — Telegram-обработчики и FSM-сценарии;
- `services` — бизнес-логика приложения;
- `repositories` — доступ к данным;
- `db/models` — ORM-модели SQLAlchemy.

Это позволяет держать бизнес-логику отдельно от Telegram-слоя и не смешивать работу с базой с обработкой пользовательских сообщений.

Подробнее:

- [docs/architecture.md](docs/architecture.md)
- [docs/db_schema.md](docs/db_schema.md)
- [docs/decisions.md](docs/decisions.md)
- [docs/product_requirements.md](docs/product_requirements.md)

## Структура проекта
```text
.
├── alembic/
├── app/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── states/
│   ├── core/
│   ├── db/
│   │   ├── models/
│   │   └── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── docs/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Переменные окружения
Проект использует .env файл. Пример есть в .env.example.

Основные переменные:

```
BOT_TOKEN=your_bot_token_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurant_feedback
DB_USER=postgres
DB_PASSWORD=postgres

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/restaurant_feedback

DEBUG=true
SQL_ECHO=false
LOG_LEVEL=INFO

AI_API_KEY=your_api_token_here
AI_BASE_URL=https://ask.chadgpt.ru/api/v1
AI_MODEL=gpt-5.4-mini
AI_TIMEOUT=60
```

## Локальный запуск

### 1. Клонировать репозиторий

`git clone https://github.com/nospoon104/anderson_feedback_bot.git`
`cd anderson_feedback_bot`

### 2. Создать .env на основе примера

`cp .env.example .env`

### 3. Поднять PostgreSQL через Docker Compose

`docker compose up -d db`

### 4. Создать виртуальное окружение и установить проект
Для Linux:

`python -m venv .venv`   
`source .venv/bin/activate`   
`pip install -e .`

### 5. Применить миграции

`alembic upgrade head`

### 6. Запустить бота локально

`python -m app.main`

## Запуск через Docker Compose
Если нужен запуск приложения и БД в контейнерах:

`docker compose up --build`

Контейнер bot запускает приложение командой:

`python -m app.main`

### Миграции
Применить миграции

`alembic upgrade head`

Создать новую миграцию

`alembic revision --autogenerate -m "add some feature"`

---

# Что показывает этот проект
## Как портфолио-проект он демонстрирует:

- умение решать реальную бизнес-задачу, а не только учебный CRUD;
- работу с async Python-стеком;
- проектирование БД и миграций;
- построение слоистой архитектуры;
- реализацию Telegram FSM-сценариев;
- расчёт отчётов и аналитики;
- генерацию Excel-файлов;
- deploy и поддержку рабочего MVP.