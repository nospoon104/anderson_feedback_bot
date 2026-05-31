# Architecture

## EN

### Architectural style
The project uses a layered backend architecture with explicit separation of responsibilities.

Main layers:
- Telegram handlers
- Services
- Repositories
- Database models

This structure helps keep business rules out of Telegram-specific code and keeps database access isolated from application logic.

### Layer responsibilities

#### 1. Handlers
Location:
- `app/bot/handlers/`

Responsibilities:
- receive Telegram updates,
- validate interaction context,
- control FSM flows,
- call services,
- format messages for users,
- send replies and files.

Handlers should not contain heavy business logic or raw SQL queries.

Examples:
- `start.py`
- `survey.py`
- `report.py`
- `superuser_report.py`
- `network_report.py`

#### 2. Services
Location:
- `app/services/`

Responsibilities:
- implement business rules,
- validate domain-specific conditions,
- aggregate data from repositories,
- calculate analytical metrics,
- prepare report objects.

Examples:
- `AuthService`
- `SurveyService`
- `ReportService`
- `ExcelReportService`

Examples of business logic:
- a manager must be assigned to a cafe before creating a survey,
- visit date cannot be in the future,
- table number must be within allowed range,
- a report compares the selected period with the previous period of equal duration.

#### 3. Repositories
Location:
- `app/db/repositories/`

Responsibilities:
- perform database queries,
- save and retrieve ORM entities,
- isolate persistence details from business logic.

Repositories use SQLAlchemy async session and return database entities or value lists.

Examples:
- `CafeRepository`
- `UserRepository`
- `SurveyRepository`

#### 4. Database models
Location:
- `app/db/models/`

Responsibilities:
- define relational structure,
- define ORM mapping,
- define relationships between entities.

Models:
- `Cafe`
- `User`
- `Survey`

### Request flow
A typical request flow looks like this:

1. User sends a command or presses a Telegram button.
2. Handler receives the update.
3. Handler resolves current user and validates access.
4. Handler collects user input via FSM if needed.
5. Handler calls a service.
6. Service applies business logic.
7. Service uses one or more repositories.
8. Repository communicates with PostgreSQL.
9. Result returns back through service to handler.
10. Handler formats text or file output and sends it to Telegram.

### Example: survey creation flow
1. Manager presses `Добавить анкету`.
2. `survey.py` starts FSM.
3. Handler sequentially collects:
   - visit datetime,
   - table number,
   - q1,
   - q2,
   - q3,
   - q4,
   - comment.
4. Handler loads current user by Telegram ID.
5. Handler calls `SurveyService.create_survey(...)`.
6. `SurveyService` validates business rules.
7. `SurveyRepository.create(...)` inserts data into PostgreSQL.
8. Handler sends confirmation message.

### Example: report generation flow
1. User selects a report type.
2. Handler collects period boundaries.
3. Handler resolves access and role.
4. Handler creates `ReportService`.
5. `ReportService` loads surveys from repository.
6. `ReportService` computes:
   - summary,
   - distribution,
   - question stats,
   - previous-period comparison.
7. Handler formats report text.
8. Handler optionally uses `ExcelReportService`.
9. Telegram user receives text and Excel file.

### FSM usage
Finite State Machine is used in user input scenarios where multiple sequential fields are required.

FSM is currently used for:
- survey creation,
- manager report period selection,
- superuser cafe report period selection,
- network report period selection.

This allows the bot to preserve intermediate input between messages.

### Why this architecture works well for MVP
Advantages:
- easy to read,
- easy to test manually,
- business logic is reusable,
- database logic is centralized,
- bot interaction logic is not mixed with SQL queries.

### Current limitations
- no dependency injection container,
- sessions are created directly inside handlers,
- no centralized error middleware yet,
- no background tasks,
- no production monitoring layer,
- no API layer besides Telegram.

These limitations are acceptable for the current MVP stage.

### Future architectural improvements
- centralized service/repository factories,
- error handling middleware,
- logging and observability improvements,
- AI comment analysis service,
- admin flows for user management,
- deployment packaging with app container.

---

## RU

### Архитектурный стиль
Проект использует слоистую backend-архитектуру с явным разделением ответственности.

Основные слои:
- Telegram handlers
- services
- repositories
- database models

Такая структура помогает не смешивать бизнес-правила с Telegram-кодом и держать доступ к базе изолированным от прикладной логики.

### Ответственность слоёв

#### 1. Handlers
Расположение:
- `app/bot/handlers/`

Что делают:
- принимают обновления из Telegram,
- проверяют контекст взаимодействия,
- управляют FSM-сценариями,
- вызывают сервисы,
- форматируют сообщения для пользователей,
- отправляют ответы и файлы.

Handlers не должны содержать тяжёлую бизнес-логику и сырой SQL.

Примеры:
- `start.py`
- `survey.py`
- `report.py`
- `superuser_report.py`
- `network_report.py`

#### 2. Services
Расположение:
- `app/services/`

Что делают:
- реализуют бизнес-правила,
- валидируют предметные ограничения,
- агрегируют данные из репозиториев,
- рассчитывают аналитические метрики,
- подготавливают объекты отчётов.

Примеры:
- `AuthService`
- `SurveyService`
- `ReportService`
- `ExcelReportService`

Примеры бизнес-логики:
- менеджер должен быть привязан к кафе перед созданием анкеты,
- дата визита не может быть в будущем,
- номер стола должен быть в допустимом диапазоне,
- отчёт должен сравнивать выбранный период с предыдущим периодом такой же длины.

#### 3. Repositories
Расположение:
- `app/db/repositories/`

Что делают:
- выполняют запросы к базе,
- сохраняют и извлекают ORM-сущности,
- изолируют детали хранения данных от бизнес-логики.

Репозитории используют асинхронную сессию SQLAlchemy и возвращают сущности базы или списки значений.

Примеры:
- `CafeRepository`
- `UserRepository`
- `SurveyRepository`

#### 4. Database models
Расположение:
- `app/db/models/`

Что делают:
- задают реляционную структуру,
- описывают ORM-маппинг,
- определяют связи между сущностями.

Модели:
- `Cafe`
- `User`
- `Survey`

### Поток запроса
Типичный поток запроса выглядит так:

1. Пользователь отправляет команду или нажимает кнопку в Telegram.
2. Handler получает update.
3. Handler определяет текущего пользователя и проверяет доступ.
4. Handler собирает пользовательский ввод через FSM, если это нужно.
5. Handler вызывает service.
6. Service применяет бизнес-логику.
7. Service использует один или несколько repositories.
8. Repository общается с PostgreSQL.
9. Результат возвращается обратно через service в handler.
10. Handler форматирует текст или файл и отправляет ответ в Telegram.

### Пример: сценарий создания анкеты
1. Менеджер нажимает `Добавить анкету`.
2. `survey.py` запускает FSM.
3. Handler по шагам собирает:
   - дату и время визита,
   - номер стола,
   - q1,
   - q2,
   - q3,
   - q4,
   - комментарий.
4. Handler загружает текущего пользователя по Telegram ID.
5. Handler вызывает `SurveyService.create_survey(...)`.
6. `SurveyService` валидирует бизнес-правила.
7. `SurveyRepository.create(...)` вставляет запись в PostgreSQL.
8. Handler отправляет подтверждение.

### Пример: сценарий формирования отчёта
1. Пользователь выбирает тип отчёта.
2. Handler собирает границы периода.
3. Handler проверяет доступ и роль.
4. Handler создаёт `ReportService`.
5. `ReportService` загружает анкеты из репозитория.
6. `ReportService` рассчитывает:
   - summary,
   - distribution,
   - статистику по вопросам,
   - сравнение с предыдущим периодом.
7. Handler форматирует текст отчёта.
8. Handler при необходимости использует `ExcelReportService`.
9. Пользователь в Telegram получает текст и Excel-файл.

### Использование FSM
Finite State Machine используется в сценариях, где нужен последовательный ввод нескольких полей.

Сейчас FSM применяется для:
- создания анкеты,
- выбора периода для отчёта менеджера,
- выбора периода для отчёта по кафе у суперюзера,
- выбора периода для сетевого отчёта.

Это позволяет сохранять промежуточный ввод между сообщениями.

### Почему эта архитектура подходит для MVP
Плюсы:
- код легко читать,
- удобно тестировать вручную,
- бизнес-логика переиспользуется,
- логика работы с БД централизована,
- Telegram-слой не смешан с SQL-запросами.

### Текущие ограничения
- нет DI-контейнера,
- сессии создаются прямо в handlers,
- пока нет централизованного error middleware,
- нет фоновых задач,
- нет production-мониторинга,
- нет отдельного API, кроме Telegram.

Для текущего этапа MVP это нормально.

### Возможные архитектурные улучшения
- централизованные фабрики сервисов и репозиториев,
- middleware для обработки ошибок,
- улучшение логирования и наблюдаемости,
- сервис AI-анализа комментариев,
- админские сценарии управления пользователями,
- упаковка приложения в отдельный app-контейнер для деплоя.