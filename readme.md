Для создания бинарного исполняемого файла и `.exe` для Windows из Python проекта, можно использовать инструменты, такие как `PyInstaller`. `PyInstaller` позволяет упаковать Python приложение вместе со всеми его зависимостями в один исполняемый файл.

### Установка PyInstaller

Установите `PyInstaller` с помощью pip:

```sh
pip install pyinstaller
```

### Создание исполняемого файла

1. **Создайте исполняемый файл для Windows (.exe):**

   Выполните следующую команду в терминале или командной строке в каталоге вашего проекта:

   ```sh
   pyinstaller --onefile --windowed dvizhapp.py
   ```

   Параметры:
   - `--onefile`: Упаковать всё в один исполняемый файл.
   - `--windowed`: Для GUI приложений, чтобы не показывать консольное окно.

2. **Создайте исполняемый файл для macOS:**

   Выполните следующую команду в терминале:

   ```sh
   pyinstaller --onefile dvizhapp.py
   ```

   Параметры:
   - `--onefile`: Упаковать всё в один исполняемый файл.

### Структура проекта

Убедитесь, что у вас есть следующая структура проекта:

```
│
├── dvizhapp.py
└── other_files_and_folders
```

### Пример команды для вашего проекта

Предположим, ваш скрипт называется `dvizhapp.py`. Выполните следующую команду:

```sh
pyinstaller --onefile --windowed dvizhapp.py
```

### После выполнения команды

После выполнения команды `PyInstaller` создаст несколько новых папок:

- `build`: Временные файлы, созданные при сборке.
- `dist`: Здесь будет находиться ваш исполняемый файл.
- `.spec` файл: Файл спецификации, который можно использовать для настройки сборки.

Ваш исполняемый файл будет находиться в папке `dist`. Например, для Windows это будет `gui.exe`, а для macOS — `gui`.

### Дополнительные настройки

Если вам нужно внести дополнительные настройки, вы можете отредактировать `.spec` файл, который создается `PyInstaller`. Затем используйте его для сборки:

```sh
pyinstaller gui.spec
```

Теперь у вас есть исполняемый файл для вашего приложения, который можно запускать на Windows или macOS без необходимости установки Python и зависимостей.


Хотя технически возможно создать исполняемый файл для Windows на macOS с помощью `PyInstaller`, это не является простой задачей и требует дополнительных шагов. Основная проблема заключается в том, что `PyInstaller` по умолчанию создает исполняемые файлы для той операционной системы, на которой он запускается.

Для создания исполняемых файлов для Windows на macOS можно воспользоваться подходом кросс-компиляции. Вот несколько способов, как это можно сделать:
