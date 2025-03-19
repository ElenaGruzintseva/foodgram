![Workflow Status](https://github.com/ElenaGruzintseva/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram

Foodgram - кулинарная веб-площадка с обширной базой ингредиентов, где зарегистрированный пользователь может:

 - Создавать и делиться своими уникальными рецептами
 - Сохранять понравившиеся блюда в избранное
 - Формировать удобные списки покупок
 - Подписываться на любимых авторов


## Стек технологий
 - Django
 - DRF
 - djoser
 - PyYAML
 - Nginx
 - Docker Compose
 - GitHub Actions

### Как развернуть проект не используя workflow

Убедитесь, что на вашем компьютере установлены Docker и Docker Compose.

Клонируйте репозиторий:

```
git clone https://github.com/ElenaGruzintseva/foodgram.git
cd foodgram
```

Выполните шаги в backend/Dockerfile, чтобы использовать локально docker-compose.yml.

Создайте файл .env в директориях проекта backend и infra и добавьте необходимые переменные окружения. Пример:

```
POSTGRES_DB=foodgram_db_1
POSTGRES_USER=foodgram_user_1
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY='default-secret-key'
DEBUG=True
ALLOWED_HOSTS='127.0.0.1, localhost'
SUPERUSER_USERNAME = superuser_username
SUPERUSER_EMAIL = superuser@mail.ru
SUPERUSER_PASSWORD = superuser_password
```

Запустите Docker Compose для создания и запуска контейнеров:

```
sudo docker-compose up -d
```

Проект будет доступен здесь http://localhost:7000

### Для автоматизации развертывания проекта можно использовать GitHub Actions

Ознакомьтесь с файлом конфигурации GitHub Actions (foodgram_main.yml), который содержит шаги для сборки.

Добавьте секреты в репозиторий:

```
DOCKER_PASSWORD - пароль от Docker Hub
DOCKER_USERNAME - имя пользователя Docker Hub
HOST - ip сервера
USER - имя пользователя сервера
SSH_KEY - ключ ssh для доступа к удаленному серверу
SSH_PASSPHRASE - пароль ssh
TELEGRAM_TO - id пользователя TELEGRAM
TELEGRAM_TOKEN - TELEGRAM токен для отправки сообщений
```

В файле docker-compose.production.yml замените username для всех образов на нужный вам, например:

```
image: vasiapupkin/foodgram_backend
image: vasiapupkin/foodgram_frontend
image: vasiapupkin/foodgram_gateway
```

При каждом пуше в ветку main сработает main.yml.

После успешного выполнения workflow, образы будут опубликованы на DockerHub,
в Telegram будут отправлены сообщения об успешном деплое,
проект будет доступен по вашему ip, указанному в секретах.


### [ElenaGruzintseva](https://github.com/ElenaGruzintseva)

