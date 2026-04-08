# Синхронізація курсів на проді (Render)

## Автоматично під час деплою ([`build.sh`](../../build.sh))

Після `migrate` скрипт білда:

1. Якщо існує [`courses/data/production_courses.json`](data/production_courses.json), виконується `python manage.py sync_courses --file …`. Наповніть цей файл курсами (формат як у [`sync_courses.example.json`](data/sync_courses.example.json)) і закомітьте; порожні `"courses": []` допустимі — синхронізація просто нічого не додасть.
2. Якщо в середовищі Render задані **обидва** `DJANGO_SUPERUSER_EMAIL` і `DJANGO_SUPERUSER_PASSWORD`, і користува з `DJANGO_SUPERUSER_USERNAME` (за замовчуванням `admin`) ще **немає** в БД, виконується `createsuperuser --noinput`.

**Паролі та email суперюзера не повинні бути в git.** Задайте їх у Render → Environment (ключі перелічені в [`render.yaml`](../../render.yaml) з `sync: false`). Після першого деплою можна змінити пароль у адмінці або прибрати пароль з env — повторне створення того самого користувача не виконується.

## Поля для копіювання з локальної адмінки

Порівняйте записи в `/admin/` локально та заповніть так само на проді (або використайте команду нижче).

### Category

- `name`, `slug` (унікальний)

### Course

- `title`, `slug` (унікальний, важливо збігати з локалом для URL)
- `category` — опційно, за slug категорії
- `description`, `price`, `duration_hours`, `level` (`beginner` | `intermediate` | `advanced`)
- `is_active`, `is_popular`, `requires_membership`
- `what_you_learn` — JSON-масив рядків
- `bunny_library_id`, `instructor` — опційно
- `cover` — завантажте файл окремо (між БД не копіюється)

### Lesson

- `course`, `title`, `slug` — у парі (курс, slug уроку) унікальні
- `description`, `bunny_video_id`, `duration_seconds`, `order`, `is_preview`

### Enrollment (доступ у кабінеті)

- `user`, `course` — унікальна пара; достатньо для «Продовжити перегляд» без Stripe `Order`.

## Варіант A: Django Admin на проді

1. Render Dashboard → Shell для сервісу → за потреби `python manage.py createsuperuser`.
2. Відкрити `https://ucvn.onrender.com/admin/`.
3. Створити Category → Course → Lessons → Enrollment для потрібного користувача.

## Варіант B: Команда `sync_courses`

1. Підготуйте JSON за зразком [`courses/data/sync_courses.example.json`](data/sync_courses.example.json) (скопіюйте в окремий файл або розширте приклад).
2. Закомітьте файл **без секретів** або завантажте на сервер і вкажіть шлях (секрети лише в env, не в JSON для відео якщо не хочете світити id — можна лишити порожніми й дозаповнити в адмінці).

```bash
python manage.py sync_courses --file path/to/courses.json
```

Запис на курс для користувача за email:

```bash
python manage.py sync_courses --file path/to/courses.json \
  --enroll-email anna@example.com \
  --course-slug your-course-slug
```

На Render: дані з `production_courses.json` підтягуються під час білда автоматично; додатково в **Shell** команди корисні для разових правок або `--enroll-email`.

## Перевірка після деплою

1. `/courses/` — курс у списку, фільтри не приховують запис (`is_active`, `requires_membership`).
2. `/accounts/cabinet/?tab=courses` під користувачем з `Enrollment` — картка курсу та «Продовжити».
3. `/courses/<slug>/learn/` — сторінка ознайомлення для записаного користувача.
