# Сервис управления рассылками(курсовой проект по Django)

Django-приложение для создания и управления рассылками электронных писем.

Сервис позволяет пользователям создавать сообщения, добавлять получателей, формировать рассылки и просматривать статистику отправок. Для менеджеров предусмотрены дополнительные возможности контроля пользователей и рассылок.

## Основные возможности

### Обычный пользователь

* регистрация и авторизация;
* создание, просмотр, редактирование и удаление собственных получателей;
* создание и управление собственными сообщениями;
* создание собственных рассылок;
* выбор получателей для рассылки;
* просмотр статистики собственных рассылок;
* отправка сообщений в заданный временной период.

### Менеджер

Менеджер имеет дополнительные возможности:

* просмотр всех получателей;
* просмотр всех рассылок;
* просмотр списка пользователей сервиса;
* блокировка пользователей;
* отключение рассылок;
* просмотр общей информации о рассылках.

Менеджер не может редактировать или удалять чужие данные.

---

## Технологии

Проект разработан с использованием:

* Python
* Django
* Django ORM
* SQLite 
* Redis-compatible cache server (Memurai)
* HTML / CSS
* Bootstrap

---

## Структура проекта

Основные приложения проекта:

```text
project/
├── mailing_service/
│   ├── migrations/
│   ├── templates/
│   │   └── mailing_service/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── mixins.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── ...
│
├── users/
│   ├── migrations/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
└── README.md
```

Названия каталогов проекта (`config` и т. п.) при необходимости следует заменить на фактическое название проекта.

---

## Модели

### CustomUser

Используется собственная модель пользователя.

Основные поля:

* `email` — уникальный email пользователя;
* `phone_number` — номер телефона;
* `avatar` — аватар;
* `is_manager` — признак менеджера;
* `is_active` — активен ли пользователь.

Для авторизации используется email вместо стандартного username.

---

### Recipient

Получатель рассылки.

Основные поля:

* `owner` — владелец записи;
* `name` — имя получателя;
* `email` — email получателя;
* `comment` — дополнительный комментарий.

Email получателя является уникальным во всей системе.

---

### Message

Сообщение, которое используется в рассылке.

Основные поля:

* `owner` — владелец сообщения;
* `message_topic` — тема сообщения;
* `message_content` — текст сообщения.

---

### Distribution

Рассылка.

Основные поля:

* `start_time` — время начала;
* `end_time` — время окончания;
* `status` — статус рассылки;
* `message` — используемое сообщение;
* `recipients` — получатели;
* `owner` — владелец;
* `is_active` — разрешена ли отправка.

Возможные статусы:

```text
created     — создана
started     — запущена
completed   — завершена
```

Поле `is_active` используется отдельно от статуса и позволяет менеджеру отключить рассылку.

---

### Distribution_Attempt

Хранит информацию о каждой попытке отправки сообщения конкретному получателю.

Основные поля:

* `mailing` — рассылка;
* `recipient` — получатель;
* `attempt_time` — время попытки;
* `status` — результат отправки;
* `server_response` — ответ сервера.

Возможные результаты:

```text
succeeded — успешно
failed    — ошибка
```

На основе этих данных формируется статистика рассылок.

---

# Установка проекта

## 1. Клонирование проекта

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПРОЕКТА>
```

## 2. Создание виртуального окружения

Windows:

```bash
python -m venv venv
```

Активация:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Установка зависимостей

Если в проекте используется `requirements.txt`:

```bash
pip install -r requirements.txt
```

Если файл ещё не создан:

```bash
pip freeze > requirements.txt
```

---

## 4. Настройка переменных окружения

При наличии `.env` необходимо указать необходимые параметры проекта.

Например:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

Не следует добавлять реальные секретные ключи и пароли в Git-репозиторий.

Рекомендуется использовать `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
db.sqlite3
media/
```

---

# Настройка Django

В `settings.py` используется кастомная модель пользователя:

```python
AUTH_USER_MODEL = 'users.CustomUser'
```

Также настроено кеширование через Redis-compatible сервер:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

# Redis / Memurai

Для кеширования проект использует Redis-compatible сервер.

В текущей конфигурации Windows используется **Memurai**, который слушает стандартный Redis-порт:

```text
127.0.0.1:6379
```

Старый Redis 3.0.504 не используется.

## Проверка Memurai

PowerShell необходимо запустить от имени администратора.

Проверка службы:

```powershell
Get-Service Memurai
```

Служба должна иметь статус:

```text
Running
```

Если служба остановлена:

```powershell
Start-Service Memurai
```

Проверка порта:

```powershell
Test-NetConnection 127.0.0.1 -Port 6379
```

Ожидаемый результат:

```text
TcpTestSucceeded : True
```

Проверить старый Redis:

```powershell
Get-Service Redis
```

Он должен оставаться остановленным:

```text
Stopped
```

---

# Миграции

После установки проекта необходимо выполнить:

```bash
python manage.py makemigrations
python manage.py migrate
```

Создание администратора:

```bash
python manage.py createsuperuser
```

Запуск проекта:

```bash
python manage.py runserver
```

После запуска проект доступен по адресу:

```text
http://127.0.0.1:8000/
```

---

# Работа с рассылками

Для создания рассылки необходимо:

1. Создать получателей.
2. Создать сообщение.
3. Создать рассылку.
4. Указать время начала и окончания.
5. Выбрать получателей.
6. Выполнить отправку в разрешённый временной период.

При создании рассылки пользователь видит только:

* собственные сообщения;
* собственных получателей.

Это предотвращает выбор чужих объектов.

---

# Права доступа

Для ограничения доступа используются Django `LoginRequiredMixin` и собственные миксины.

## ManagerRequiredMixin

Менеджерские страницы доступны только пользователям, у которых:

```python
is_manager = True
```

Пример:

```python
class ManagerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_manager:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
```

## Проверка владельца

Обычный пользователь работает только со своими объектами.

Например:

```python
Recipient.objects.filter(
    owner=self.request.user
)
```

А менеджер может просматривать все записи.

---

# Блокировка пользователей

Менеджер может заблокировать пользователя.

Для этого используется стандартное поле Django:

```python
is_active = False
```

Заблокированный пользователь не может использовать сервис как активный пользователь.

---

# Отключение рассылки

Менеджер может отключить рассылку.

Для этого используется:

```python
is_active = False
```

Отключённая рассылка не должна отправляться.

Статус рассылки (`created`, `started`, `completed`) и `is_active` выполняют разные функции:

* `status` показывает жизненный цикл рассылки;
* `is_active` показывает, разрешена ли отправка.

---

# Статистика

Для каждой рассылки сохраняются попытки отправки.

На основании `Distribution_Attempt` рассчитываются:

* количество успешных отправок;
* количество неуспешных отправок;
* общее количество попыток.

Для обычного пользователя статистика ограничивается его собственными рассылками:

```python
Distribution_Attempt.objects.filter(
    mailing__owner=request.user
)
```

---

# Кеширование

В проекте реализованы несколько видов кеширования.

## Низкоуровневое серверное кеширование

Статистика пользователя кешируется с уникальным ключом:

```python
cache_key = f'statistics_user_{self.request.user.id}'
```

Получение данных из кеша:

```python
stats = cache.get(cache_key)
```

Если данных нет, выполняется запрос к базе:

```python
stats = Distribution_Attempt.objects.filter(
    mailing__owner=self.request.user
).aggregate(
    successful=Count(
        'id',
        filter=Q(
            status=Distribution_Attempt.SUCCEEDED
        )
    ),
    failed=Count(
        'id',
        filter=Q(
            status=Distribution_Attempt.FAILED
        )
    ),
)
```

После этого результат сохраняется в Redis:

```python
cache.set(cache_key, stats, timeout=300)
```

Время хранения:

```text
300 секунд = 5 минут
```

---

## Клиентское кеширование

Для статической страницы можно использовать HTTP-заголовок:

```python
@method_decorator(
    cache_control(max_age=300),
    name='dispatch'
)
class AboutView(TemplateView):
    template_name = 'mailing_service/about.html'
```

Браузер получает:

```text
Cache-Control: max-age=300
```

и может использовать сохранённый ответ в течение 5 минут.

---

# Страница «О сервисе»

Для демонстрации кеширования предусмотрена статическая страница:

```text
/about/
```

Она не содержит пользовательских данных и подходит для клиентского кеширования.

---

# Основные команды

Запуск виртуального окружения Windows:

```bash
venv\Scripts\activate
```

Запуск Django:

```bash
python manage.py runserver
```

Создание миграций:

```bash
python manage.py makemigrations
```

Применение миграций:

```bash
python manage.py migrate
```

Создание администратора:

```bash
python manage.py createsuperuser
```

Проверка проекта:

```bash
python manage.py check
```

Запуск тестов:

```bash
python manage.py test
```

---

# Типичный порядок запуска проекта

При работе на Windows рекомендуется:

### 1. Запустить Memurai

PowerShell от имени администратора:

```powershell
Start-Service Memurai
```

### 2. Проверить Redis-порт

```powershell
Test-NetConnection 127.0.0.1 -Port 6379
```

Должно быть:

```text
TcpTestSucceeded : True
```

### 3. Активировать виртуальное окружение

```bash
venv\Scripts\activate
```

### 4. Запустить Django

```bash
python manage.py runserver
```

### 5. Открыть приложение

```text
http://127.0.0.1:8000/
```

---

# Важные замечания

## Не запускать одновременно два Redis-сервера

Старый Redis и Memurai не должны одновременно использовать порт:

```text
6379
```

В текущей конфигурации используется:

```text
Memurai → 127.0.0.1:6379
```

## Не хранить секреты в Git

Не добавляйте в репозиторий:

* `SECRET_KEY`;
* пароли;
* API-ключи;
* данные SMTP;
* `.env`.

## Проверять миграции после изменения моделей

После изменения моделей:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Лицензия

Проект создан в учебных целях.
