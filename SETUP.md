# INSTALATIE STAPPEN

## repo locaal downloaden

run deze command voor een lokaale kopie van de repo

```bash
git clone https://github.com/F-3-R-R-3/Tectonic-Hackaton-Mang.git
```

dan vind je het onder

```cmd
C:\Users\jouwnaam\dev\Tectonic-Hackaton-Mang
of
C:\Gebruikers\jouwnaam\dev\Tectonic-Hackaton-Mang
```

## benodigde tools

run dit in de terminal (als het niet werkt probeer dan opnieuw met admin)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

dit instaleert `uv`, dit zorgt ervoor dat we onze python versies en packages syncroniseren

## hoe gebruiken

open de map van daarnet in je codeer tool (vscode, pycharm, nvim, ...)
doordat we uv geinstaleerd hebben zul je waarschijnlijk een extra menu zien vershijnen

dat was het, nu als je code wil uplaoden git commit je je veranderingen en git push je die. om de code te refreshen en terug te syncroniseren nieuwe veranderingen van oonline git pull je
