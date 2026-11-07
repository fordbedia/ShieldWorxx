## To add a package:
`cd ~/Sites/jobguard/backend && source .venv/bin/activate`

### 1. Add the package by hand to requirements.in, e.g.:
`djangorestframework`

```shell
pip-compile requirements.in      # 2. regenerate the lock (requirements.txt)
pip-sync requirements.txt        # 3. install it into the venv
```


## Other cases

| Task | Do this |
|---|---|
| Remove a package | Delete its line from `requirements.in`, then run `pip-compile` and `pip-sync` |
| Upgrade one package | `pip-compile --upgrade-package langgraph`, then `pip-sync` (like `composer update vendor/pkg`) |
| Upgrade everything | `pip-compile --upgrade`, then `pip-sync` (like `composer update`) |
| Fresh clone or new machine | `pip install pip-tools`, then `pip-sync requirements.txt` (like `composer install`) |
