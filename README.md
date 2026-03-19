

#  Sibyl

> A Student Information System inspired by *Psycho-Pass*
> Automatically adapts to your system's **Dark / Light mode**


## Overview

**Sibyl** is a modern Student Information System built with a clean UI and system-based theme detection.
It allows efficient management of students, colleges, and programs with right-click editing functionality and detailed database viewing.


## Theme

* Automatically follows your system’s **Dark / Light mode**
* Styled UI using:

  * `sv-ttk`
  * `darkdetect`
  * `pywinstyles`

## 
Dark Mode
<img width="638" align="center" height="396" alt="Sibyl Dark Mode" src="https://github.com/user-attachments/assets/3b3888fd-0e66-44b0-beaf-b3b76af10d08" />

<br clear="right"/>

Light Mode
<img width="638" align="center" height="396" alt="Sibyl Light Mode" src="https://github.com/user-attachments/assets/40cbc81f-2473-42d6-9ea3-f3d4e49417a5" />

<br clear="right"/>

## Features

### Student Page

* Add new students by filling in required information
* Edit students using their **ID Number**
* Right-click to edit or delete student records


### College Page

* View list of colleges with:
  * College Code
  * Full College Name
* Add new colleges via **+ button**
* Manage Programs (same design as College tab)
* Right-click to edit or delete colleges/programs


###  Database Page

* View total number of students
* Display complete student records
* In-depth individual student information view
* Right-click to edit or delete entries


##  Installation
The app is already pre-built with the executable file given.

Install the required dependencies:

```bash
pip install sv-ttk
pip install darkdetect
pip install pywinstyles
pip install pillow
```

Pyinstaller Installation:
```bash
pyinstaller -w -F `
--add-data "ui/Assets;ui/Assets" `
--add-data "data;data" `
-i "ui/Assets/APP_ICON.ico" `
-n "SYBL" main.py `
```

### Inspiration

Inspired by the system and aesthetic of *Psycho-Pass*
bringing structured order to student information management.
