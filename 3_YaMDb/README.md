# Групповой проект по курсу 'API: интерфейс взаимодействия программ'
![Python](https://img.shields.io/badge/Python-3.9.10-blue)
![Django](https://img.shields.io/badge/Django-3.2.16-blue)
![Django_REST_framework](https://img.shields.io/badge/Django_REST_framework-3.12.4-blue)



## Описание проекта
Проект **YaMDb** собирает **отзывы** пользователей на **произведения**. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на **категории**, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен **жанр** из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
    Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые **отзывы** и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — **рейтинг** (целое число). На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять **комментарии** к отзывам.

## Ресурсы

* Ресурс **auth**: аутентификация.
* Ресурс **users**: пользователи.
* Ресурс **titles**: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
* Ресурс **categories**: категории (типы) произведений («Фильмы», «Книги», «Музыка»). Одно произведение может быть привязано только к одной категории.
* Ресурс **genre**: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
* Ресурс **reviews**: отзывы на произведения. Отзыв привязан к определённому произведению.
* Ресурс **comments**: комментарии к отзывам. Комментарий привязан к определённому отзыву.

## Пользовательские роли и права доступа

* **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
* **Аутентифицированный пользователь** (user) — может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
* **Модератор** (moderator) — те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
* **Администратор** (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
* **Суперюзер Django** должен всегда обладать правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.




## Запуск проекта на локальном сервере
### Необходимое ПО

* python **3.9.10**
* pip

### Установка

> Для MacOs и Linux вместо python использовать python3

1. Клонировать репозиторий.
   ```
   $ git clone https://github.com/Timofey-G/Practicum.Yandex
   ```
2. Cоздать и активировать виртуальное окружение:
    ```
      $ cd Practicum.Yandex/3_YaMDb
      $ python -m venv venv
    ```
    Для Windows:
    ```
      $ source venv/Scripts/activate
    ```
    Для MacOs/Linux:
    ```
      $ source venv/bin/activate
    ```
3. Установить зависимости из файла requirements.txt:
    ```
    (venv) $ python -m pip install --upgrade pip
    (venv) $ pip install -r requirements.txt
    ```

4. Выполнить миграции:
    ```
    (venv) $ python api_yamdb/manage.py migrate
    ```
5. Заполнить БД тестовыми данными
    ```
    (venv) $ python api_yamdb/manage.py load_data
    ```
6. Запустить сервер
    ```
    (venv) $ python api_yamdb/manage.py runserver
    ```
После выполнения вышеперечисленных инструкций проект доступен по адресу http://127.0.0.1:8000/
> Подробная документация API доступна после запуска сервера по адресу http://127.0.0.1:8000/redoc/

## Контакты

**Тимофей Григоренко**  

[![Telegram Badge](https://img.shields.io/badge/-yo_tima-blue?style=social&logo=telegram&link=https://t.me/yo_tima)](https://t.me/yo_tima) [![Gmail Badge](https://img.shields.io/badge/yo.tgrig@yandex.ru-FFCC00?style=flat&logo=ycombinator&logoColor=red&link=mailto:yo.tgrig@yandex.ru)](mailto:yo.tgrig@yandex.ru)

**Данила Кушлевич** 

[![Telegram Badge](https://img.shields.io/badge/-dkushlevich-blue?style=social&logo=telegram&link=https://t.me/dkushlevich)](https://t.me/dkushlevich) [![Gmail Badge](https://img.shields.io/badge/-dkushlevich@gmail.com-c14438?style=flat&logo=Gmail&logoColor=white&link=mailto:dkushlevich@gmail.com)](mailto:dkushlevich@gmail.com)

**Кирилл Чебодаев** 

[![Telegram Badge](https://img.shields.io/badge/-codingtv-blue?style=social&logo=telegram&link=https://t.me/codingtvar)](https://t.me/codingtvar) [![Gmail Badge](https://img.shields.io/badge/-kchebodaevdu125@gmail.com-c14438?style=flat&logo=Gmail&logoColor=white&link=mailto:kchebodaevdu125@gmail.com)](mailto:kchebodaevdu125@gmail.com)
