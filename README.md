# Иерархическое получение данных — тестовое задание

Консольная утилита на Python, которая:

1. загружает орг. структуру компании (офисы → отделы → сотрудники) из JSON-файла
   в таблицу PostgreSQL;
2. по id сотрудника выдаёт список всех сотрудников офиса, к которому он относится.

Документ по сложности используемого SQL-запроса и перспективам его оптимизации —
в [`QUERY_ANALYSIS.md`](QUERY_ANALYSIS.md).

## Архитектура

- **Модель данных.** Иерархия хранится в одной таблице `org_units` по схеме
  adjacency list (`id`, `parent_id`, `name`, `type`), как описано в задании. `type`
  различает офис (1), отдел (2) и сотрудника (3).
- **Без ORM.** Работа с БД — через `psycopg` (v3) и «сырой» SQL. DDL и запрос выборки
  вынесены в отдельные `.sql`-файлы (`sql/`), их читают и выполняют `schema.py` и
  `queries.py`.

- **Точка входа — `main.py`.** Запуск одной транзакцией создаёт схему, загружает
  `data/org_structure.json` и печатает сотрудников офиса для id, переданного флагом
  `--employee-id` (по умолчанию `3`, id из примера в задании).
- **Docker Compose** (`docker-compose.yml`): PostgreSQL 10 и утилита (`Dockerfile`,
  сервис `app`). `app` дожидается `healthcheck` у `postgres` и подключается по имени
  сервиса в docker-сети (`PGHOST=postgres`).

```
├── org_structure/            # доменный пакет — только логика org_units
│   ├── schema.py               # читает .sql из sql/ и создаёт таблицу/индекс
│   ├── models.py                 # доменная модель: OrgUnitType, OrgUnit
│   ├── loader.py                  # чтение JSON, валидация (через OrgUnit.from_raw), загрузка в БД
│   ├── queries.py                  # SQL-запрос выборки сотрудников офиса
│   └── repository.py                # OrgUnitsRepository — фасад над connection
├── sql/
│   ├── create_table.sql       # DDL таблицы org_units
│   ├── create_index.sql        # индекс по parent_id
│   ├── upsert_org_unit.sql      # INSERT ... ON CONFLICT DO UPDATE (идемпотентная загрузка)
│   └── employees_by_office.sql   # рекурсивный CTE-запрос
├── data/org_structure.json    # тестовые данные из задания
├── tests/                     # unit-тесты + 1 integration-тест (без реальной БД по умолчанию)
├── db.py                      # подключение к PostgreSQL (инфраструктура, вне домена)
├── main.py                    # точка входа: схема + загрузка + вывод сотрудников офиса
├── Dockerfile                  # образ утилиты (сервис app)
├── docker-compose.yml           # PostgreSQL 10 + сервис app
├── .flake8                      # конфигурация flake8 (max-line-length=99)
├── requirements.txt              # psycopg[binary] + python-dotenv
└── requirements-dev.txt           # + pytest, flake8
```

## Требования

- Docker Desktop (или любой Docker + Compose v2) — единственное, что нужно для запуска.
- Для разработки/тестов вне контейнера — Python 3.12 (проверено на 3.12).

## Установка и запуск

### 0. Скачать репозиторий

В `cmd` на Windows:

```cmd
git clone https://github.com/Grigorijyurginis/tenzor_test_task.git
cd tenzor_test_task
```

### Сценарий 1 — просто запустить и посмотреть (образа ещё нет)

Один прогон — одна команда:

```powershell
docker compose run --rm app
```

`docker compose run` сам собирает образ `app`, если его ещё нет, поднимает PostgreSQL 10 (если ещё не поднят,
дожидаясь `healthcheck`) и запускает утилиту в контейнере: создаёт схему, загружает
`data/org_structure.json` и печатает сотрудников офиса для `employee_id = 3` (id из
примера в задании — значение по умолчанию). `--rm` удаляет
контейнер утилиты после завершения; сам PostgreSQL остаётся поднятым (см.
`docker compose down` ниже).

Ожидаемый вывод для тестовых данных из задания (сотрудник id=3 — Иванов из офиса
в Санкт-Петербурге):

```
Иванов
Сидоров
Петров
```

Чтобы проверить другого сотрудника — передайте id флагом `--employee-id`:

```powershell
docker compose run --rm app --employee-id 13
```

Загрузка идемпотентна (`INSERT ... ON CONFLICT DO UPDATE`), поэтому повторные запуски
не падают на дублировании id — можно вызывать `docker compose run --rm app --employee-id <id>`
сколько угодно раз с разными id без пересоздания БД.

### Сценарий 2 — повторный запуск после изменений в коде (образ уже собран)

`docker compose run` собирает образ, **только если его ещё не существует** — если
образ уже был собран раньше, а `main.py`/`org_structure/`/`db.py` с тех пор изменились,
команда из сценария 1 молча использует старый образ со старым кодом. Чтобы гарантировать
актуальность — добавьте `--build`:

```powershell
docker compose run --rm --build app --employee-id 13
```

### Остановить

Убрать всё, включая том с данными БД:

```powershell
docker compose down -v
```

### Локальный запуск (для разработки на Windows)

Креды в `docker-compose.yml` заданы через `${VAR:-default}`; чтобы переопределить —
скопируйте `.env.example` в `.env` (в `.gitignore`, в репозиторий не попадает).

```powershell
py -3.12 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
docker compose up -d --wait postgres
python main.py --employee-id 3
```

`db.py` подключается к `localhost:5432` (порт публикуется в
`docker-compose.yml`), если переменные `PG*` не заданы — тот же код, что и в
контейнере `app`, просто резолвит DSN иначе.

## Тесты

```powershell
pytest
```

Юнит-тесты — валидация/парсинг JSON и доменная модель (`tests/test_loader.py`),
построение SQL-запроса и передача параметров (`tests/test_queries.py`), делегирование
`OrgUnitsRepository` в `schema`/`loader`/`queries` (`tests/test_repository.py`) — все на
моках, без обращения к реальной БД, Docker/PostgreSQL для их запуска не требуется.

Отдельно — интеграционный тест (`@pytest.mark.integration` в `tests/test_queries.py`),
по умолчанию пропускается (`addopts = "-m 'not integration'"` в `pyproject.toml`).
Прогоняется явно и требует поднятой БД:

```powershell
docker compose up -d --wait postgres
pytest -m integration
```

Схема и данные создаются в одной незакоммиченной транзакции, в конце —
`connection.rollback()` (PostgreSQL поддерживает транзакционный DDL, откатывается и
`CREATE TABLE`, и `INSERT`) — реальная БД после теста не меняется, отдельная тестовая
БД не нужна.

## Проверка стиля (PEP8)

```powershell
python -m flake8
```

Настройка — в `.flake8` (`max-line-length = 99`; PEP8 явно допускает поднимать лимит
до 99 символов, если это сделано конфигом, а не молча).

## Сторонние библиотеки

- **`psycopg[binary]`** (v3) — драйвер PostgreSQL, вся работа с БД — через него.
- **`python-dotenv`** — читает `.env` в переменные окружения для локального запуска
  (`db.py`).
- **`pytest`** — тесты (dev-зависимость).
- **`flake8`** — проверка стиля по PEP8 (dev-зависимость).

ORM не используется — согласно требованию задания вся работа с SQL выполняется
напрямую через `psycopg`.
