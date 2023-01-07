# vfl2csv

Kommandozeilenskript zur Umwandlung und Umformatierung von Ausgaben des propritären Versuchsflächendatenbanksystems
der TU Dresden Professur für Waldwachstum und Produktion von Holzbiomasse.

## Abhängigkeiten

* Python 3 & PIP
* OpenPyXL
* pandas

`python3 -m pip install openpyxl pandas`

## Ausführung

### in Bash  / Zsh:

```bash
vfl2csv$ PYTHONPATH='.'
vfl2csv$ python vfl2csv path/to/input out/
```

### über Powershell:

```powershell
PS G:\vfl2csv> $env:PYTHONPATH = '.'
PS G:\vfl2csv> python vfl2csv path/to/input out/
```









