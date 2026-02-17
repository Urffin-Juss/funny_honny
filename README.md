# Run With Love CRM

Кастомная CRM для бегового сообщества Run With Love: управление клиентами, забегами, заказами, складом и задачами.

## Stack
- Backend: Django + DRF
- DB: PostgreSQL
- Async: Celery + Redis
- Docs: drf-spectacular (Swagger)
- Infra: Docker + docker-compose

## Что уже есть
- Роли: `owner`, `admin`, `packer`
- Сущности MVP: Event, Client, Product, Stock, Order, OrderItem, Task, ImportBatch, RawExcelRow
- API + фильтры + ролевой доступ
- Dashboard API (`owner` only)
- Telegram регистрация/авторизация:
  - вход через Telegram Login Widget
  - серверная проверка подписи (`hash`)
  - авто-создание пользователя при первом входе
- Веб-интерфейс в стилистике RWL (черный/белый/красный + логотип)
  - `/` главная с автопереходом в магазин
  - `/shop/` redirect на магазин
  - `/login/` вход через Telegram
  - `/workspace/` внутренняя рабочая страница

## Запуск
1. Создайте `.env`:
```bash
cp .env.example .env
```
2. Заполните Telegram-параметры в `.env`:
```env
TELEGRAM_BOT_TOKEN=<bot_token>
TELEGRAM_BOT_USERNAME=<bot_username_without_@>
SHOP_URL=https://ваш-магазин
```
3. Поднимите сервисы:
```bash
docker-compose up --build
```
4. Примените миграции:
```bash
docker-compose exec web python manage.py migrate
```
5. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

## URLs
- Landing: `http://localhost:8000/`
- Login: `http://localhost:8000/login/`
- Workspace: `http://localhost:8000/workspace/`
- Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`

## Примечания
- Новые Telegram-пользователи создаются с ролью `packer`.
- Повышение роли (`admin`/`owner`) выполняется в админке.
- Импорт Excel реализован как MVP-контур с сохранением raw-строк.
- `xlsx` поддерживается из коробки. Для `xls` требуется пакет `xlrd`; без него импорт отметится как `FAILED` с понятной ошибкой.
