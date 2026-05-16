# Custom Auth & Access Control API

Backend-приложение на Django REST Framework с собственной системой аутентификации и авторизации.
Проект реализует не только login/logout, но и отдельную модель управления доступом к ресурсам: роли, бизнес-элементы и правила действий над ними.

Решение сделано как демонстрационный backend для тестового задания: его можно быстро поднять локально, заполнить демо-данными и проверить сценарии `401 Unauthorized`, `403 Forbidden` и успешного доступа для разных ролей.

## Что Реализовано

- регистрация пользователя по ФИО, email, паролю и повтору пароля;
- login по email/password с выдачей JWT;
- logout с отзывом текущей JWT-сессии;
- получение, обновление и мягкое удаление профиля;
- хранение паролей через `bcrypt`, без plain text;
- собственная таблица активных auth-сессий;
- собственная RBAC-модель доступа: роли, ресурсы, правила;
- admin API для просмотра и изменения ролей, ресурсов и правил доступа;
- mock business endpoints для заказов и продуктов;
- seed-команда для создания демо-пользователей, ролей и правил;
- PostgreSQL через Docker Compose.

## Идея Решения

В проекте разделены две разные задачи:

**Аутентификация** отвечает на вопрос: кто пользователь?

В приложении это решается через:

- `User`;
- `bcrypt` password hash;
- JWT access token;
- `AuthSession` с `token_jti`;
- custom DRF authentication class.

**Авторизация** отвечает на вопрос: что пользователю разрешено делать?

В приложении это решается через:

- `Role`;
- `UserRole`;
- `BusinessElement`;
- `AccessRule`;
- единый сервис проверки доступа.

Такой подход важен для задания: приложение использует Django/DRF как web/API-инструмент, но не строит правила доступа на стандартных Django permissions из коробки.

## Структура Проекта

```text
.
├── apps/
│   ├── access/          # роли, ресурсы приложения, правила доступа
│   ├── resources/       # mock business endpoints
│   └── users/           # пользователи, JWT, login/logout, профиль
├── config/              # настройки Django и корневые urls
├── docker-compose.yml   # PostgreSQL для локального запуска
├── manage.py            # Django management entry point
├── pyproject.toml       # настройки инструментов проекта
├── requirements.txt     # runtime-зависимости
└── requirements-dev.txt # dev-зависимости
```

### `apps/users`

Отвечает за пользовательский контур:

- модель пользователя;
- хеширование паролей;
- выпуск и декодирование JWT;
- проверку JWT в `Authorization: Bearer <token>`;
- регистрацию, login, logout;
- профиль текущего пользователя;
- seed-команду с демо-данными.

### `apps/access`

Отвечает за собственную систему прав:

- роли пользователей;
- бизнес-элементы приложения;
- правила доступа роли к элементу;
- связь пользователей и ролей;
- сервис принятия решения о доступе;
- admin API для управления правилами.

### `apps/resources`

Содержит mock-ресурсы бизнес-приложения.
По ТЗ таблицы для таких объектов создавать не требуется, поэтому заказы и продукты описаны как mock data.
При этом доступ к ним проверяется через настоящую систему ролей и правил.

## Модель Доступа

Основная схема:

```text
User 1---N UserRole N---1 Role 1---N AccessRule N---1 BusinessElement
```

Таблицы:

| Таблица | Назначение |
| --- | --- |
| `users` | Пользователи приложения |
| `auth_sessions` | Активные JWT-сессии и отзыв токенов |
| `roles` | Роли: admin, manager, user |
| `user_roles` | Связь пользователей и ролей |
| `business_elements` | Ресурсы приложения: orders, products, access_rules, users |
| `access_rules` | Правила действий роли над ресурсом |

Поля прав в `access_rules`:

| Поле | Смысл |
| --- | --- |
| `read_permission` | Можно читать свои объекты |
| `read_all_permission` | Можно читать все объекты |
| `create_permission` | Можно создавать объекты |
| `update_permission` | Можно изменять свои объекты |
| `update_all_permission` | Можно изменять все объекты |
| `delete_permission` | Можно удалять свои объекты |
| `delete_all_permission` | Можно удалять все объекты |

Если пользователь не определён, API возвращает `401`.
Если пользователь определён, но правило не разрешает действие, API возвращает `403`.

## Почему JWT + AuthSession

JWT удобен тем, что клиент может отправлять токен в каждом запросе:

```http
Authorization: Bearer <access_token>
```

Но у чистого JWT есть особенность: выданный токен сложно отозвать до истечения срока.
Поэтому в проекте есть таблица `auth_sessions`.

При login:

- создаётся JWT;
- создаётся запись `AuthSession`;
- в JWT кладётся `jti`, связанный с этой сессией.

При logout:

- текущая сессия помечается как `revoked_at`;
- старый токен больше не проходит проверку;
- защищённый endpoint возвращает `401`.

Это делает logout проверяемым и предсказуемым.

## Быстрый Запуск

Требования:

- Python 3.12+;
- Docker Desktop;
- PowerShell или другой терминал.

Создать виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
pip install -r requirements-dev.txt
```

Создать локальный `.env`:

```powershell
Copy-Item .env.example .env
```

Запустить PostgreSQL:

```powershell
docker compose up -d
```

Проверить контейнер:

```powershell
docker compose ps
```

Ожидаемый результат:

```text
db   postgres:16   Up   0.0.0.0:5433->5432/tcp
```

Применить миграции:

```powershell
python manage.py migrate
```

Заполнить базу демо-данными:

```powershell
python manage.py seed_demo_data
```

Запустить сервер:

```powershell
python manage.py runserver
```

API будет доступен по адресу:

```text
http://127.0.0.1:8000/api/
```

## Настройки Окружения

Пример `.env`:

```env
SECRET_KEY=change-me-to-a-long-random-development-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

POSTGRES_DB=auth_demo
POSTGRES_USER=auth_demo
POSTGRES_PASSWORD=auth_demo
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

JWT_SECRET=change-me-to-a-long-random-jwt-development-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_TTL_MINUTES=60
```

По умолчанию PostgreSQL внутри контейнера работает на стандартном порту `5432`, а наружу пробрасывается на `5433`.
Это помогает не конфликтовать с локальным PostgreSQL, который часто уже занимает `5432`.

Если `5433` тоже занят, достаточно поменять `POSTGRES_PORT` в `.env`, например:

```env
POSTGRES_PORT=5434
```

Затем пересоздать контейнер:

```powershell
docker compose down
docker compose up -d
```

## Demo Users

Команда `seed_demo_data` создаёт пользователей:

| Email | Password | Role |
| --- | --- | --- |
| `admin@example.com` | `admin12345` | `admin` |
| `manager@example.com` | `manager12345` | `manager` |
| `user@example.com` | `user12345` | `user` |

## API Endpoints

### Auth & Profile

| Method | URL | Назначение |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Регистрация |
| `POST` | `/api/auth/login/` | Login и получение JWT |
| `POST` | `/api/auth/logout/` | Logout и отзыв текущей сессии |
| `GET` | `/api/users/me/` | Профиль текущего пользователя |
| `PATCH` | `/api/users/me/` | Обновление профиля |
| `DELETE` | `/api/users/me/` | Мягкое удаление аккаунта |

### Mock Business Resources

| Method | URL | Назначение |
| --- | --- | --- |
| `GET` | `/api/resources/orders/` | Список заказов с учётом прав |
| `POST` | `/api/resources/orders/` | Проверка права создания заказа |
| `GET` | `/api/resources/orders/<id>/` | Один заказ с проверкой owner/all access |
| `PATCH` | `/api/resources/orders/<id>/` | Проверка права изменения заказа |
| `DELETE` | `/api/resources/orders/<id>/` | Проверка права удаления заказа |
| `GET` | `/api/resources/products/` | Список продуктов с учётом прав |
| `POST` | `/api/resources/products/` | Проверка права создания продукта |

### Access Admin API

Эти endpoints защищены правилами доступа к `access_rules`.
Демо-admin имеет доступ, обычный user получает `403`.

| Method | URL | Назначение |
| --- | --- | --- |
| `GET/POST` | `/api/access/roles/` | Список и создание ролей |
| `GET/PATCH/DELETE` | `/api/access/roles/<id>/` | Работа с ролью |
| `GET/POST` | `/api/access/elements/` | Список и создание бизнес-элементов |
| `GET/PATCH/DELETE` | `/api/access/elements/<id>/` | Работа с бизнес-элементом |
| `GET/POST` | `/api/access/rules/` | Список и создание правил |
| `GET/PATCH/DELETE` | `/api/access/rules/<id>/` | Работа с правилом |

## Примеры Запросов

### Login

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "user12345"
}
```

Ответ:

```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer"
}
```

Дальше токен передаётся так:

```http
Authorization: Bearer <jwt>
```

### Доступ Без Токена

```http
GET /api/resources/orders/
```

Результат:

```http
401 Unauthorized
```

### Обычный Пользователь

`user@example.com` имеет доступ только к своим заказам.

```http
GET /api/resources/orders/
Authorization: Bearer <user_token>
```

Ответ:

```json
[
  {
    "id": 1,
    "title": "First order",
    "owner_email": "user@example.com"
  }
]
```

Попытка открыть чужой заказ:

```http
GET /api/resources/orders/2/
Authorization: Bearer <user_token>
```

Результат:

```http
403 Forbidden
```

### Manager

`manager@example.com` имеет `read_all_permission` для orders/products.
Он видит все mock-заказы:

```json
[
  {
    "id": 1,
    "title": "First order",
    "owner_email": "user@example.com"
  },
  {
    "id": 2,
    "title": "Manager order",
    "owner_email": "manager@example.com"
  }
]
```

### Admin Access Rules

Admin может читать и изменять правила доступа:

```http
GET /api/access/rules/
Authorization: Bearer <admin_token>
```

Обычный user на этот же endpoint получает:

```http
403 Forbidden
```

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer <token>
```

После logout тот же токен больше не работает:

```http
GET /api/users/me/
Authorization: Bearer <old_token>
```

Результат:

```http
401 Unauthorized
```

## Проверка В Postman

1. Запустить сервер:

```powershell
python manage.py runserver
```

2. Выполнить login:

```text
POST http://127.0.0.1:8000/api/auth/login/
```

Body -> raw -> JSON:

```json
{
  "email": "admin@example.com",
  "password": "admin12345"
}
```

3. Скопировать `access_token`.

4. В следующих запросах открыть вкладку `Authorization`:

```text
Type: Bearer Token
Token: <access_token>
```

Postman сам добавит заголовок `Authorization: Bearer ...`.

## Проверка Качества

Базовые проверки проекта:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Ожидаемый результат:

```text
System check identified no issues
No changes detected
```

Проверка демо-данных:

```powershell
python manage.py seed_demo_data
```

Команда идемпотентная: её можно запускать повторно, она обновит демо-данные без создания дублей по ролям, ресурсам и правилам.

## Архитектурные Решения

### Почему приложения разделены на `users`, `access`, `resources`

Каждая часть отвечает за свою область:

- `users` не знает деталей бизнес-ресурсов;
- `access` хранит универсальные правила;
- `resources` применяет правила к mock-объектам.

Так проще расширять проект: новый ресурс может использовать тот же механизм доступа без переписывания auth-логики.

### Почему mock-ресурсы без таблиц

В ТЗ прямо указано, что таблицы для вымышленных бизнес-объектов создавать не требуется.
Поэтому `orders` и `products` представлены mock-данными, но проходят через полноценную проверку прав.

### Почему не используются стандартные Django permissions

Задача тестового — показать собственную схему доступа к ресурсам.
Поэтому роли, ресурсы и правила описаны отдельными таблицами, а решение о доступе принимает сервис `check_access`.

### Почему soft delete

При удалении аккаунта пользователь не исчезает из БД.
Вместо этого:

- `is_active=False`;
- проставляется `deleted_at`;
- активные сессии отзываются;
- повторный login невозможен.

Так сохраняется история аккаунта и выполняется требование мягкого удаления.

## Полезные Команды

Остановить контейнеры:

```powershell
docker compose down
```

Полностью удалить локальные данные PostgreSQL и начать с чистой базы:

```powershell
docker compose down -v
docker compose up -d
python manage.py migrate
python manage.py seed_demo_data
```

Посмотреть применённые миграции:

```powershell
python manage.py showmigrations
```

Проверить, что Docker видит контейнер:

```powershell
docker compose ps
```
