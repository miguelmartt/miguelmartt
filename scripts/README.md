# Scripts de generación de assets

Estos scripts generan las imágenes SVG que usa el README del perfil (`assets/radar-*.svg` y `assets/card-stats-*.svg`). Se ejecutan automáticamente cada día mediante GitHub Actions (`.github/workflows/update-assets.yml`), así que **normalmente no hace falta tocarlos**.

## generate_radar.py

Lee `assets/skills.json` y dibuja un radar de habilidades autoevaluadas.

Para cambiar tu autoevaluación, edita `assets/skills.json`:

```json
{
  "skills": {
    "PHP & Laravel": 9,
    "Automatización (n8n)": 9,
    "DevOps & VPS": 8,
    "Bases de Datos": 7,
    "JavaScript / Frontend": 7,
    "IA / LLM": 6
  }
}
```

Los valores van de 0 a 10. Haz commit y push del JSON: el workflow lo detecta y regenera el radar solo.

Para probarlo en local:

```bash
pip install -r scripts/requirements.txt
python3 scripts/generate_radar.py
```

## generate_terminal_banner.py

Genera un banner tipo terminal animado (SVG puro, con SMIL) que "escribe" unas líneas de comandos al cargar la página — sin dependencias externas ni servicios de terceros. Para cambiar el texto que se "escribe", edita la lista `LINES` al principio del script.

```bash
python3 scripts/generate_terminal_banner.py
```

## generate_stats_card.py

Llama a la API pública de GitHub para tu usuario y genera una tarjeta con: repos públicos, commits aproximados, estrellas, forks y seguidores. No necesita configuración — en GitHub Actions usa automáticamente el `GITHUB_TOKEN` que la plataforma inyecta en cada ejecución (solo para evitar el límite de peticiones anónimas, los datos que lee son siempre públicos).

Para probarlo en local:

```bash
python3 scripts/generate_stats_card.py tu-usuario-de-github
```

## Snake de contribuciones (.github/workflows/snake.yml)

Workflow aparte que usa la acción pública `Platane/snk` para generar una animación de una serpiente "comiéndose" tu gráfico de contribuciones. Publica el resultado en una rama `output` del propio repo (se crea sola la primera vez que corre), y el README la referencia directamente desde ahí con una URL `raw.githubusercontent.com`. No requiere ningún script propio ni configuración adicional.

## Notas

- Todo corre sobre GitHub-hosted runners: no necesitas ningún servidor propio ni secretos adicionales (el `GITHUB_TOKEN` lo proporciona GitHub automáticamente).
- El workflow tiene permiso `contents: write` para poder hacer commit de los SVG regenerados.
- Si quieres cambiar la frecuencia de actualización, edita el `cron` en `.github/workflows/update-assets.yml` o `.github/workflows/snake.yml`.
