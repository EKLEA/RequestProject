Описание проекта

Веб-приложение с использованием фреймворка FLASK и базы данных MongoDB для централизованного хранения данных о пользователях wi-fi сети.

Функционал проекта

1.  Создание администраторов веб-приложения:
Веб-приложение предоставляет возможность создания двух видов администраторов: те, которые управляют только заявками и те, которые помимо этого могут создавать новых администраторов.
Для этого существует форма со следующими полями:
  - Фамилия.
  - Имя.
  - Отчество.
  - Тип админа.
  - Логин: поле для ввода логина администратора.
  - Пароль: поле для отображения и генерации пароля для администратора.

2.  Создание пользователя:
Веб-приложение предоставляет возможность администратору системы добавлять новых пользователей wi-fi.
Для этого существует форма со следующими полями:
  - Номер заявки: уникальный идентификатор заявки пользователя.
  - Фамилия.
  - Имя.
  - Отчество.
  - Телефон: поле для ввода номера телефона пользователя.
  - Почта: поле для ввода электронной почты
  - SSID: поле для ввода идентификатора пользователя.
  - Логин: поле для ввода логина пользователя.
  - Пароль: поле для отображения и генерации пароля для пользователя.
  - Текст для отправки пользователю: поле для ввода текста, который будет отправлен пользователю.
  
Вывод данных в виде таблицы.
3.  Поиск по ФИО.
4.  Отправка пароля по e-mail и SMS.
5.  Удаление пользователей сети / администраторов.
