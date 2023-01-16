# vfl2csv

Kommandozeilenskript zur Umwandlung und Umformatierung von Ausgaben des propritären Versuchsflächendatenbanksystems
der TU Dresden Professur für Waldwachstum und Produktion von Holzbiomasse.

## Abhängigkeiten

* Python 3 & PIP
* pandas
* OpenPyXL
* PySide6

```bash
python3 -m pip install pandas openpyxl pyside6
```

## Ausführung

### Bash oder Zsh:

```bash
vfl2csv$ python -m vfl2csv path/to/input out/
vfl2csv$ python -m vfl2csv_forms
```

### Powershell:

```powershell
PS G:\vfl2csv> python -m vfl2csv path/to/input out/
PS G:\vfl2csv> python -m vfl2csv_forms
```
