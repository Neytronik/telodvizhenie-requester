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
   pyinstaller --onefile --windowed your_script.py
   ```

   Параметры:
   - `--onefile`: Упаковать всё в один исполняемый файл.
   - `--windowed`: Для GUI приложений, чтобы не показывать консольное окно.

2. **Создайте исполняемый файл для macOS:**

   Выполните следующую команду в терминале:

   ```sh
   pyinstaller --onefile your_script.py
   ```

   Параметры:
   - `--onefile`: Упаковать всё в один исполняемый файл.

### Структура проекта

Убедитесь, что у вас есть следующая структура проекта:

```
your_project/
│
├── your_script.py
└── other_files_and_folders
```

### Пример команды для вашего проекта

Предположим, ваш скрипт называется `excel_app.py`. Выполните следующую команду:

```sh
pyinstaller --onefile --windowed gui.py
```

### После выполнения команды

После выполнения команды `PyInstaller` создаст несколько новых папок:

- `build`: Временные файлы, созданные при сборке.
- `dist`: Здесь будет находиться ваш исполняемый файл.
- `.spec` файл: Файл спецификации, который можно использовать для настройки сборки.

Ваш исполняемый файл будет находиться в папке `dist`. Например, для Windows это будет `excel_app.exe`, а для macOS — `excel_app`.

### Дополнительные настройки

Если вам нужно внести дополнительные настройки, вы можете отредактировать `.spec` файл, который создается `PyInstaller`. Затем используйте его для сборки:

```sh
pyinstaller your_script.spec
```

Теперь у вас есть исполняемый файл для вашего приложения, который можно запускать на Windows или macOS без необходимости установки Python и зависимостей.


Хотя технически возможно создать исполняемый файл для Windows на macOS с помощью `PyInstaller`, это не является простой задачей и требует дополнительных шагов. Основная проблема заключается в том, что `PyInstaller` по умолчанию создает исполняемые файлы для той операционной системы, на которой он запускается.

Для создания исполняемых файлов для Windows на macOS можно воспользоваться подходом кросс-компиляции. Вот несколько способов, как это можно сделать:

### 1. Использование Wine и PyInstaller
Wine — это программное обеспечение, позволяющее запускать приложения Windows на Unix-подобных операционных системах. Вы можете установить Wine на macOS и использовать его для запуска PyInstaller в Windows-окружении.

1. **Установите Wine:**
   ```sh
   brew install wine
   ```

2. **Установите PyInstaller в Wine-окружении:**
   ```sh
   wine python -m pip install pyinstaller
   ```

3. **Запустите PyInstaller через Wine:**
   ```sh
   wine python -m PyInstaller your_script.py
   ```

### 2. Использование Docker
Docker позволяет создать контейнер с Windows-окружением, в котором можно запустить PyInstaller.

1. **Установите Docker на macOS:**
   [Инструкции по установке Docker](https://docs.docker.com/docker-for-mac/install/)

2. **Создайте Dockerfile для Windows-контейнера:**
   ```Dockerfile
   FROM mcr.microsoft.com/windows/servercore:ltsc2019
   SHELL ["cmd", "/S", "/C"]

   # Установка Python
   RUN powershell -Command \
       wget https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe -OutFile python-installer.exe; \
       Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait; \
       Remove-Item -Force python-installer.exe

   # Установка PyInstaller
   RUN python -m pip install pyinstaller

   # Копирование скрипта в контейнер
   COPY your_script.py /your_script.py

   # Компиляция скрипта
   CMD ["pyinstaller", "your_script.py"]
   ```

3. **Постройте и запустите Docker-контейнер:**
   ```sh
   docker build -t pyinstaller-windows .
   docker run --rm -v $(pwd):/output pyinstaller-windows
   ```

### 3. Использование виртуальной машины
Вы можете использовать виртуальную машину (например, VirtualBox) с установленной Windows для создания исполняемого файла.

1. **Установите VirtualBox:**
   [Инструкции по установке VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. **Создайте виртуальную машину с Windows.**

3. **Установите Python и PyInstaller в виртуальной машине.**

4. **Запустите PyInstaller в виртуальной машине, чтобы создать исполняемый файл.**

### Заключение
Хотя все эти методы позволяют создать исполняемый файл для Windows на macOS, они требуют дополнительных усилий и настроек. Самый простой и надежный способ — использовать Windows для создания исполняемых файлов с помощью PyInstaller.