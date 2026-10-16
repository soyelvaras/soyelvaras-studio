# Soy Elvaras Studio

Edición de reels con la identidad de Soy Elvaras, dentro de Claude. Grabas tus clips, Claude edita el reel.

**Uso personal de Cristobal Varas.** Es una adaptación del kit Claude Creator Studio de Ten Fold Marketing,
hecha bajo la licencia de comprador (ajustar plantillas y configuración para uso propio). No se comparte, no se
publica y no se vende. Este repositorio tiene que ser **privado**.

## Qué hay aquí

```
.claude-plugin/marketplace.json     el catálogo para instalarlo en Claude
elvaras-studio/                     el plugin
  .claude-plugin/plugin.json
  skills/elvaras-studio/
    SKILL.md                        el flujo de edición (con la sección de marca Soy Elvaras)
    brands/soyelvaras/              colores, tipografías, logo, tono
    brands/clientes/_plantilla/     copia esta carpeta para cada cliente
    captions/  effects/  engine/    estilos de subtítulos, efectos y motor de render
    picker/                         el selector de estilo (página local)
    references/  scripts/
.claude/launch.json                 abre el selector en el navegador de la app
dev/                                elecciones de prueba del selector (no se suben)
```

## Instalar en Claude (desde esta carpeta)

```bash
claude plugin marketplace add "C:/Users/crist/Documents/soyelvaras-studio"
```

```bash
claude plugin install elvaras-studio@soyelvaras-studio
```

Luego, en un chat nuevo: `/elvaras-studio setup`.

## Ver el selector en el navegador

```bash
python "elvaras-studio/skills/elvaras-studio/picker/serve.py" --keep-alive --port 4790 --config "dev/studio-picks.json"
```

Abre http://127.0.0.1:4790/

## Pendiente (plan de 7 días)

- [ ] Grabar los videos de muestra propios y reemplazar todos los previews (subtítulos, estilos, efectos).
- [ ] Traducir nombres y descripciones de estilos y efectos (`picker/data`, `captions/styles.json`).
- [ ] Llevar los colores de marca a los valores por defecto de cada estilo de subtítulos y efecto.
- [ ] Exportación 16:9 para la web.
- [ ] Perfiles por cliente en el flujo.
- [ ] Repo privado en GitHub y fuente de actualizaciones propia (`scripts/update.py`, `SOURCE`).
