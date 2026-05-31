# Architectural and Product Decisions

## EN

### 1. Telegram bot as the main interface

Decision:
Use Telegram bot as the primary user interface.

Why:
- fast MVP delivery,
- low entry barrier for staff,
- no need to build a web frontend,
- convenient for internal operational usage.

Trade-off:
- UX is more limited than a web interface,
- multi-step input requires FSM,
- reporting presentation is less flexible than dashboards.

---

### 2. Manual digitization of paper forms

Decision:
Managers manually enter paper survey results into the bot.

Why:
- fastest path to MVP,
- preserves existing paper process,
- avoids immediate process disruption,
- allows analytics without building guest-facing UI.

Trade-off:
- manual labor remains,
- risk of partial data entry,
- anti-fraud is not solved in MVP.

---

### 3. PostgreSQL as the main database

Decision:
Use PostgreSQL as the system of record.

Why:
- reliable relational storage,
- easy aggregation and reporting,
- strong fit for structured survey data,
- future-proof enough for production growth.

Trade-off:
- requires environment setup,
- more operational overhead than local file storage.

---

### 4. Async SQLAlchemy and asyncpg

Decision:
Use SQLAlchemy 2 async with asyncpg.

Why:
- consistent modern async Python stack,
- good fit with aiogram async architecture,
- scalable enough for future improvements.

Trade-off:
- slightly more complex than synchronous setup,
- requires discipline in session handling.

---

### 5. Layered architecture

Decision:
Separate code into handlers, services, repositories, and models.

Why:
- keeps business logic reusable,
- avoids SQL in Telegram handlers,
- makes reporting logic easier to evolve,
- improves readability and maintainability.

Trade-off:
- more files and boilerplate,
- slightly slower initial development.

---

### 6. Role model: manager and superuser

Decision:
Use two initial roles:
- manager
- superuser

Why:
- covers MVP operational cases,
- simple access model,
- easy to explain and test.

Trade-off:
- no granular permissions yet,
- no admin self-service in current version.

---

### 7. Previous period comparison

Decision:
Compare selected period with the immediately previous period of the same duration.

Why:
- simple and understandable management metric,
- useful for trend tracking,
- works without complex BI tooling.

Trade-off:
- comparison logic must be clearly documented,
- edge cases with low survey counts may reduce usefulness.

---

### 8. Excel export via openpyxl

Decision:
Generate `.xlsx` files server-side with openpyxl.

Why:
- managers and directors often expect Excel reports,
- easy sharing and offline usage,
- practical for internal operations.

Trade-off:
- formatting requires extra work,
- more output logic to maintain.

---

### 9. Polling mode for MVP

Decision:
Run the Telegram bot in polling mode during MVP phase.

Why:
- easiest development setup,
- no need for public HTTPS endpoint,
- simpler local debugging.

Trade-off:
- not ideal for larger production setups,
- webhook mode may be preferable later.

---

### 10. AI postponed until stable reporting core

Decision:
Implement AI comment analysis after survey and reporting flows are stable.

Why:
- no point analyzing comments before comments are consistently stored,
- reporting core is the real product backbone,
- AI is a value-add, not the data foundation.

Trade-off:
- “wow feature” comes later,
- documentation and deployment work may feel less exciting first.

---

## RU

### 1. Telegram-бот как основной интерфейс

Решение:
Использовать Telegram-бота как основной пользовательский интерфейс.

Почему:
- позволяет быстро сделать MVP,
- низкий порог входа для сотрудников,
- не нужно сразу делать web frontend,
- удобно для внутреннего операционного использования.

Компромисс:
- UX ограничен сильнее, чем в веб-интерфейсе,
- многошаговый ввод требует FSM,
- представление отчётов менее гибкое, чем в dashboard.

---

### 2. Ручная оцифровка бумажных анкет

Решение:
Менеджеры вручную переносят бумажные анкеты в бота.

Почему:
- это самый быстрый путь к MVP,
- сохраняется существующий бумажный процесс,
- не нужно сразу ломать операционные привычки,
- можно получить аналитику без отдельного интерфейса для гостей.

Компромисс:
- ручной труд остаётся,
- есть риск неполного внесения данных,
- проблема anti-fraud в MVP пока не решена.

---

### 3. PostgreSQL как основная база

Решение:
Использовать PostgreSQL как источник истины.

Почему:
- надёжное реляционное хранилище,
- удобно для агрегаций и отчётности,
- хорошо подходит для структурированных анкетных данных,
- достаточно перспективно для роста в production.

Компромисс:
- требует настройки окружения,
- эксплуатационно сложнее, чем хранение в файле.

---

### 4. Async SQLAlchemy и asyncpg

Решение:
Использовать SQLAlchemy 2 async вместе с asyncpg.

Почему:
- это современный согласованный async stack на Python,
- хорошо сочетается с async-архитектурой aiogram,
- подходит для дальнейшего развития проекта.

Компромисс:
- чуть сложнее, чем синхронная схема,
- требует аккуратной работы с сессиями.

---

### 5. Слоистая архитектура

Решение:
Разделить код на handlers, services, repositories и models.

Почему:
- бизнес-логика переиспользуется,
- SQL не смешивается с Telegram-обработчиками,
- отчётную логику проще развивать,
- код легче читать и сопровождать.

Компромисс:
- больше файлов и шаблонного кода,
- старт разработки немного медленнее.

---

### 6. Модель ролей: manager и superuser

Решение:
Использовать две стартовые роли:
- manager
- superuser

Почему:
- этого достаточно для MVP-сценариев,
- простая модель доступа,
- легко объяснять и тестировать.

Компромисс:
- пока нет тонкой настройки прав,
- нет self-service админки в текущей версии.

---

### 7. Сравнение с предыдущим периодом

Решение:
Сравнивать выбранный период с непосредственно предыдущим периодом той же длительности.

Почему:
- это простая и понятная управленческая метрика,
- полезно для отслеживания динамики,
- работает без сложной BI-системы.

Компромисс:
- логику сравнения нужно явно документировать,
- при малом числе анкет метрика может быть менее показательной.

---

### 8. Excel-экспорт через openpyxl

Решение:
Генерировать `.xlsx` файлы на стороне сервера через openpyxl.

Почему:
- менеджеры и директора часто ожидают именно Excel,
- удобно отправлять и использовать офлайн,
- это практичный формат для внутренней операционки.

Компромисс:
- оформление требует отдельной работы,
- становится больше логики вывода.

---

### 9. Polling-режим для MVP

Решение:
На этапе MVP запускать Telegram-бота в polling-режиме.

Почему:
- это самый простой вариант для разработки,
- не нужен публичный HTTPS endpoint,
- легче локально отлаживать.

Компромисс:
- для более крупного production это не идеальный вариант,
- позже может быть полезен webhook-режим.

---

### 10. AI откладывается до стабилизации отчётного ядра

Решение:
Добавлять AI-анализ комментариев только после того, как стабилизированы ввод анкет и отчёты.

Почему:
- нет смысла анализировать комментарии, если они ещё нестабильно сохраняются,
- отчётное ядро — это основа продукта,
- AI — это надстройка, а не фундамент данных.

Компромисс:
- “вау-фича” появляется позже,
- документация и деплой сначала ощущаются менее захватывающими.