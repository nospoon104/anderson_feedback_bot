### Anderson feedback analizer 

# Restaurant Feedback Bot / Бот для оцифровки анкет гостей

## EN

### Overview
Restaurant Feedback Bot is a Telegram bot for digitizing paper-based guest feedback forms in a restaurant chain.

The system allows managers to enter survey results into PostgreSQL and generate analytical reports for a selected period. Superusers can view reports for a specific cafe or for the entire network. The bot also exports reports to Excel. 

This project was built as an MVP focused on:
- fast manual digitization of paper forms,
- simple analytics for operational management,
- a clear service-oriented architecture,
- practical production-oriented backend development.

### Key features
- Telegram bot based on `aiogram 3`
- PostgreSQL database
- Async SQLAlchemy 2.0
- Alembic migrations
- Role-based access:
  - `manager`
  - `superuser`
- FSM flow for entering surveys
- Cafe report for managers
- Cafe report for superusers
- Network-wide report for superusers
- Excel export for reports
- Test data seed scripts

### Business logic
Each guest survey contains:
- visit date and time
- table number
- 4 yes/no questions
- optional comment

Scoring logic:
- `Yes = 1`
- `No = 0`
- total survey score = sum of 4 answers
- converted to percentage:
  - `4/4 = 100%`
  - `3/4 = 75%`
  - `2/4 = 50%`
  - `1/4 = 25%`
  - `0/4 = 0%`

Reports include:
- total surveys
- average score
- average percentage
- score distribution
- yes/no stats for each question
- comparison with the previous period of the same length

### User roles
#### Manager
Can:
- start the bot
- enter surveys
- generate a report for their own cafe for a selected period
- receive an Excel file for the report

#### Superuser
Can:
- start the bot
- generate a report for any selected cafe
- generate a report for the entire network
- receive Excel files for reports

### Tech stack
- Python 3.12
- aiogram 3
- PostgreSQL
- SQLAlchemy 2.0 async
- asyncpg
- Alembic
- Pydantic 2
- openpyxl
- Docker Compose

### Architecture
The project follows a layered architecture:

- `handlers` — Telegram bot interaction layer
- `services` — business logic
- `repositories` — database access layer
- `db/models` — SQLAlchemy ORM models

Flow:
`Telegram update -> handler -> service -> repository -> PostgreSQL`

### Project structure
```text
├── alembic
├── alembic.ini
├── app
│   ├── bot
│   │   ├── bot.py
│   │   ├── handlers
│   │   │   ├── network_report.py
│   │   │   ├── report.py
│   │   │   ├── start.py
│   │   │   ├── superuser_report.py
│   │   │   └── survey.py
│   │   ├── keyboards
│   │   │   ├── common.py
│   │   │   ├── report.py
│   │   │   └── survey.py
│   │   └── states
│   │       ├── network_report.py
│   │       ├── report.py
│   │       ├── superuser_report.py
│   │       └── survey.py
│   ├── check_cafes.py
│   ├── check_data.py
│   ├── check_report.py
│   ├── check_surveys.py
│   ├── check_users.py
│   ├── cleanup_test_cafe.py
│   ├── core
│   │   ├── config.py
│   │   └── constants.py
│   ├── db
│   │   ├── base.py
│   │   ├── models
│   │   │   ├── cafe.py
│   │   │   ├── survey.py
│   │   │   └── user.py
│   │   ├── repositories
│   │   │   ├── cafe_repository.py
│   │   │   ├── survey_repository.py
│   │   │   └── user_repository.py
│   │   └── session.py
│   ├── main.py
│   ├── manage_user.py
│   ├── reset_surveys.py
│   ├── schemas
│   │   ├── cafe.py
│   │   ├── report.py
│   │   ├── survey.py
│   │   └── user.py
│   ├── seed_cafes.py
│   ├── seed_data.py
│   ├── seed_test_managers.py
│   ├── seed_test_surveys.py
│   ├── services
│   │   ├── auth_service.py
│   │   ├── excel_report_service.py
│   │   ├── report_service.py
│   │   └── survey_service.py
│   ├── test_db_connection.py
│   └── utils
├── docker-compose.yml
├── docs
│   ├── architecture.md
│   ├── bot_flows.md
│   ├── db_schema.md
│   ├── decisions.md
│   └── product_requirements.md
├── pyproject.toml
├── README.md

```
### Environment variables:


``` 
Example .env:

    BOT_TOKEN=your_bot_token_here
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=restaurant_feedback
    DB_USER=postgres
    DB_PASSWORD=postgres
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/restaurant_feedback 
```

# Local development setup
## 1. Start PostgreSQL

` docker compose up -d`

## 2. Create and activate virtual environment
` python -m venv .venv
`

`source .venv/bin/activate`

## 3. Install project

` pip install -e .`

## 4. Apply migrations

`alembic upgrade head`

## 5. Run the bot

`python -m app.main`

___
___

# Database migrations
Alembic is configured to read the database URL from application settings.

## Generate migration:

`alembic revision --autogenerate -m "message"`

## Apply migrations:


`alembic upgrade head`

# Service scripts
The project includes helper scripts for local development and testing:
- seeding cafes
- seeding managers
- seeding surveys
- checking inserted data
- cleaning test data

These scripts are intended mainly for development and debugging.

# Current MVP status
## Implemented:
- survey input flow
- database persistence
- role-based access
- cafe reports
- network reports
- Excel exports
- previous-period comparison

## Planned:
- AI analysis of comments
- deployment packaging
- operational hardening
- UX improvements
- user management via Telegram bot
- Portfolio value

## This project demonstrates:
- async Python backend development
- Telegram bot development with FSM
- relational database design
- SQLAlchemy and Alembic usage
- layered architecture
- reporting logic
- Excel generation
- production-oriented thinking