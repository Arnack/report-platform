# Report Platform

Асинхронная платформа для генерации и управления отчётами.

## Быстрый старт

### Требования
- Docker и Docker Compose
- Node.js 20+ (для локальной разработки фронтенда)

### Запуск

```bash
# Запустить все сервисы одной командой
docker-compose up --build

# Фронтенд: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
```

### Остановка

```bash
docker-compose down
# С очисткой volumes (удалит данные БД и файлы отчётов)
docker-compose down -v
```

## Архитектура

Платформа состоит из следующих компонентов:

- **Backend (FastAPI)** — REST API для управления отчётами
- **Worker (Celery)** — асинхронная генерация отчётов
- **Redis** — брокер сообщений для Celery
- **PostgreSQL** — хранение метаданных о запусках отчётов
- **Frontend (React)** — веб-интерфейс для работы с платформой

Подробная документация в [ARCHITECTURE.md](./ARCHITECTURE.md)

## API Endpoints

### Отчёты
- `GET /api/reports` — список доступных типов отчётов
- `POST /api/reports/{report_id}/run` — запуск генерации отчёта (async)
- `GET /api/runs` — список всех запусков отчётов (с пагинацией)
- `GET /api/runs/{run_id}` — статус конкретного запуска
- `GET /api/runs/{run_id}/download` — скачивание готового отчёта

### Системные
- `GET /api/health` — проверка здоровья сервиса
- `GET /` — корневой endpoint с информацией об API

## Доступные отчёты

### 1. Sales Report
Комплексный отчёт по продажам с разбивкой:
- По продуктам
- По регионам
- Динамика по дням

**Параметры:**
- `days` — количество дней (1-365, по умолчанию 30)
- `region` — фильтр по региону (North/South/East/West/All)

### 2. API Usage Report
Аналитика использования API с метриками:
- Общее количество запросов
- Распределение по статус-кодам
- Время ответа (avg, p95, p99)
- Топ эндпоинтов

**Параметры:**
- `days` — количество дней (1-90, по умолчанию 7)
- `environment` — окружение (production/staging/both)

## Как добавить новый отчёт

1. Создайте файл `backend/reports/my_new_report.py`
2. Унаследуйтесь от `BaseReportGenerator`
3. Реализуйте методы: `id`, `name`, `description`, `params_schema`, `generate()`
4. Зарегистрируйте отчёт в `backend/reports/registry.py`

Подробная инструкция в [ARCHITECTURE.md](./ARCHITECTURE.md)

## Структура проекта

```
reports/
├── docker-compose.yml          # Оркестрация всех сервисов
├── README.md                   # Этот файл
├── ARCHITECTURE.md             # Архитектурная документация
├── backend/                    # Backend на FastAPI
│   ├── main.py                 # Точка входа приложения
│   ├── api/                    # API роуты
│   ├── models/                 # SQLAlchemy модели
│   ├── schemas/                # Pydantic схемы
│   ├── tasks/                  # Celery задачи
│   ├── reports/                # Генераторы отчётов
│   │   ├── base.py             # Абстрактный базовый класс
│   │   ├── registry.py         # Реестр отчётов
│   │   ├── sales_report.py     # Отчёт по продажам
│   │   └── api_usage_report.py # Отчёт использования API
│   └── storage/                # Хранилище файлов
├── frontend/                   # Frontend на React
│   ├── src/
│   │   ├── api.js              # API клиент
│   │   ├── App.js              # Корневой компонент
│   │   └── pages/              # Страницы
│   └── public/
└── postgres/
    └── init.sql                # Инициализация БД
```

## Технологии

- **Backend:** Python 3.12, FastAPI, Celery, SQLAlchemy, OpenPyXL
- **Frontend:** React 18, React Bootstrap, Axios, date-fns
- **Инфраструктура:** PostgreSQL 16, Redis 7, Docker Compose

## Лицензия

MIT
