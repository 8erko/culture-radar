# Culture Radar – Reddit Miner (Setup)

Dieses Mini-Tool zieht **täglich kostenlos** echte Top-Posts + Top-Kommentare aus deinen Subreddits und legt sie als `data/latest.json` ab. Dein Cowork-Dashboard liest diese Datei dann jeden Morgen und macht Berk-Style-Ideen daraus.

Kein API-Key nötig, keine Kosten. Läuft auf GitHub Actions (gratis).

---

## Was hier drin ist
- `reddit_miner.py` – der Scraper (nutzt Reddits öffentliche `.json`-Endpunkte)
- `config.json` – deine Subreddits, Mindest-Score, Keywords (frei editierbar)
- `.github/workflows/daily.yml` – startet den Scraper täglich automatisch
- `data/` – wird automatisch erzeugt (`latest.json` + dated Archiv)

---

## Einrichtung (einmalig, ~5 Min)

1. **GitHub-Account** (falls nicht vorhanden): https://github.com → Sign up.

2. **Neues Repo anlegen:** „New repository" → Name z. B. `culture-radar` → **Public** (wichtig, damit das Dashboard die JSON lesen darf – es sind eh nur öffentliche Reddit-Posts) → Create.

3. **Diese Dateien hochladen:** Auf der Repo-Seite „Add file → Upload files" und den kompletten Inhalt dieses `reddit-miner`-Ordners reinziehen (inkl. dem versteckten `.github`-Ordner). Committen.
   - Falls der Upload den `.github`-Ordner schluckt: leg die Datei manuell an über „Add file → Create new file" und tippe als Pfad `.github/workflows/daily.yml`, dann den Inhalt reinkopieren.

4. **Actions aktivieren:** Reiter „Actions" → falls gefragt, „I understand my workflows, enable them".

5. **Erstlauf testen:** Actions → „Daily Reddit Mine" → „Run workflow". Nach ~1–2 Min sollte im Repo ein Ordner `data/` mit `latest.json` auftauchen.

6. **Deine Daten-URL kopieren:** Sie sieht so aus:
   ```
   https://raw.githubusercontent.com/DEIN-USERNAME/culture-radar/main/data/latest.json
   ```
   (`DEIN-USERNAME` ersetzen; falls dein Default-Branch `master` heißt statt `main`, anpassen.)

7. **Mir die URL schicken** – ich trage sie in deine tägliche Cowork-Aufgabe ein. Ab dann zieht das Dashboard jeden Morgen echte Reddit-Threads + Kommentare als Quelle.

---

## Anpassen
Alles in `config.json`:
- **Subreddits** hinzufügen/entfernen: Eintrag `{ "name": "subredditname", "min_score": 50 }`.
- **min_score**: wie viele Upvotes ein Post mind. braucht (höher = nur die echten Banger).
- **keywords**: nur Posts behalten, die eins der Wörter im Titel/Text haben (z. B. bei r/todayilearned sinnvoll, um auf Fashion/Design zu filtern).
- **timeframe**: `"day"` oder `"week"`.
- **posts_per_sub** / **comments_per_post**: wie viel pro Subreddit/Post gezogen wird.

## Uhrzeit ändern
In `.github/workflows/daily.yml` die `cron`-Zeile. Achtung: GitHub-Cron läuft in **UTC**. `0 5 * * *` = 05:00 UTC ≈ 07:00 deutsche Zeit (Sommer).
