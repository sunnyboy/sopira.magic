# ProgressTracker – Ako používať

Účel: jednoduché priebežné logovanie progresu (percentá/ETA) pre dlhé operácie v generator module (seeding, čistenie, ďalšie skripty).

## API
- Trieda: `sopira_magic.apps.generator.progress.ProgressTracker`
- Konštruktor:
  - `name`: názov operácie (string)
  - `total`: celkový počet krokov (int). Ak 0, percentá sa nepočítajú.
  - `logger`: voliteľný logger (INFO)
  - `log_fn`: voliteľný callback pre okamžitý výpis (napr. `self.stdout.write` v management príkaze)
  - `min_interval`: minimálny čas medzi logmi (sekundy, default 2.0)
- Metódy:
  - `start()`
  - `step(n=1, note=None)` – inkrement o `n`, voliteľná poznámka
  - `finish()`

## Jednoduché použitie v manage príkaze
```python
from sopira_magic.apps.generator.progress import ProgressTracker

progress = ProgressTracker(
    name="my_command",
    total=expected_count,   # napr. queryset.count(), alebo suma plánovaných krokov
    logger=logger,          # voliteľné
    log_fn=self.stdout.write  # odporúčané pre okamžitý výpis do konzoly
)
progress.start()

# ... počas práce
progress.step(n=batch_size, note="users batch")

progress.finish()
```

## Kde je výstup viditeľný
- Ak zadáš `logger`, ide do backend logu (INFO).
- Ak zadáš `log_fn` (napr. `self.stdout.write`), ide priamo na stdout pri behu management príkazu.

## Aktuálna integrácia
- `generate_all_data` (manage command): tracker s loggerom + stdout; počíta total ako sum(count) z `GENERATOR_CONFIG`.
- `clear_all_data` (manage command): tracker s loggerom + stdout; loguje mazanie modelov (user je chránený sopira).
- `generate_seed_data` (service): tracker s loggerom; ak chceš aj stdout, priamo v command-e použi vlastný tracker (ako v `generate_all_data`) alebo rozšír signatúru podľa potreby.

## Tipy a poznámky
- Ak je `total` neznáme, môže byť 0 – percentá sa nepočítajú, ale stále vidíš elapsed/ETA založené na doterajšom priemere.
- `min_interval` nastav podľa toho, koľko logov chceš (default 2 s).
- Pri veľkých modeloch môžeš logovať medzikroky cez `step` po dávkach (napr. každých 1000 záznamov).
- Progress logy neovplyvňujú transakcie – pri atomic blokoch sa výpisy zobrazia hneď, aj keď dáta sa commitnú až na konci.

