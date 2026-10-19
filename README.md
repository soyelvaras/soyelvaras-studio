# Soy Elvaras Studio

Tú grabas tus clips. Claude edita el reel.

Plugin de Claude que convierte clips verticales hablando a cámara en reels terminados con la marca Soy Elvaras: elige
las mejores tomas, corta silencios y miradas fuera de cámara, pone subtítulos de marca, efectos y sonido, y entrega una
copia para revisar en el celular.

## Instalar en la app de escritorio de Claude (recomendado)

La edición corre en tu computador, así que esta es la forma principal de usarlo.

1. Abre la app de escritorio de Claude y entra a la pestaña **Code**.
2. Haz clic en el **+** junto a la caja de mensajes, luego **Plugins** y luego **Browse plugins**.
3. Arriba a la derecha, haz clic en **Add**, luego **Add marketplace** y luego **Add from a repository**.
4. Pega este link y haz clic en **Sync**:

```
https://github.com/soyelvaras/soyelvaras-studio
```

5. Instala **Soy Elvaras Studio** desde la lista.
6. Abre un chat nuevo y escribe:

```
/elvaras-studio setup
```

## Instalar desde el navegador (claude.ai)

Sirve para dejarlo instalado en tu cuenta desde cualquier computador.

1. Entra a [claude.ai/customize/plugins](https://claude.ai/customize/plugins) (**Customize > Plugins**).
2. Haz clic en **Add** y luego **Add marketplace**.
3. Escribe `soyelvaras/soyelvaras-studio`.
4. Instala **Soy Elvaras Studio**.

El plugin queda guardado en tu cuenta y aparece solo en la app de escritorio y en Claude Code la próxima vez que abras
una sesión con esa cuenta. Si no aparece, escribe `/reload-plugins` o abre Claude Code de nuevo.

**Importante:** el chat del navegador no puede editar video. Los clips, ffmpeg, Python y el render viven en tu
computador, así que la edición se hace en la app de escritorio (pestaña **Code**) o en Claude Code. Desde el
navegador o el celular lo usas con Remote Control, que se explica a continuación.

## Editar desde el navegador o el celular (Remote Control)

Remote Control abre en el navegador o en la app del celular una sesión que corre en tu computador. Los clips y el
render siguen en el PC; tú solo das las instrucciones desde donde estés.

1. En tu computador, dentro de una sesión de Claude Code, escribe:

```
/remote-control
```

   O, desde una terminal en la carpeta donde trabajas:

```bash
claude remote-control
```

2. Abre el link que aparece en cualquier navegador, búscalo en [claude.ai/code](https://claude.ai/code), o escanea el
   código QR con la app de Claude en el celular.
3. Escribe ahí lo mismo de siempre: "edítalo", "abre el selector", etc.

Requisitos: plan Pro, Max, Team o Enterprise. El computador tiene que quedar encendido y con la sesión abierta. Los
comandos de plugins (`/plugin`) no funcionan desde el navegador ni el celular: instala y actualiza en el computador.

## Instalar desde la terminal

Solo si usas Claude Code en Terminal (Mac) o PowerShell (Windows). Ejecútalos tú, no dentro de Claude. Cada línea es
un pegado.

```bash
claude plugin marketplace add soyelvaras/soyelvaras-studio
```

```bash
claude plugin install elvaras-studio@soyelvaras-studio
```

En Windows necesitas [Git for Windows](https://git-scm.com/downloads) instalado antes.

Si el comando `claude` no existe (solo tienes la app de escritorio), usa la instalación de la app.

Luego abre Claude Code y escribe `/elvaras-studio setup`.

## Primer uso

`/elvaras-studio setup` (o "configura el Studio") hace tres cosas, una sola vez:

1. Revisa y descarga sus herramientas (Python, ffmpeg, modelos y sonidos) en segundo plano.
2. Pregunta dónde quedan tus clips (por defecto Descargas) y dónde guardar los proyectos (por defecto `reel-edits`).
3. Abre el **selector de estilo** para que elijas tus subtítulos, efectos y transiciones. También puedes saltártelo y
   mandar un reel de ejemplo: el Studio lo estudia y copia ese look.

Después solo dejas los clips en Descargas y dices **"edítalo"**.

## Cómo se usa

| Lo que dices | Lo que pasa |
|---|---|
| **edítalo** (o "edita estos clips", "dejé clips en descargas") | Edita el reel completo y te entrega la copia para el celular y el render final. |
| **primero solo el corte** | Te entrega solo el corte apretado para aprobar el ritmo antes de los efectos. |
| **abre el selector** / **cambia mi estilo** | Abre el selector completo. |
| **cambia mis subtítulos** / **cambia mis efectos** / **cambia mis transiciones** | Abre esa pestaña del selector. |
| "hazlo como este" + un reel, captura o link | Estudia el ejemplo y desde ahí todos tus reels usan ese estilo. |
| "cambia X" (un corte, una palabra, un efecto) | Hace el cambio y entrega una versión nueva (`-v2`, `-v3`). |
| "prueba Karaoke en este" | Cambia los subtítulos solo en ese reel, sin tocar tus elecciones. |
| **dame la versión web** | Renderiza también en 16:9. |

Cada proyecto queda en `reel-edits/<nombre>/`, con los renders en `renders/`.

## Actualizaciones

Los arreglos y efectos nuevos llegan como actualizaciones del plugin. Tus elecciones y tu estilo se mantienen.

**Desde el chat:** di `actualiza el Studio` y Claude instala la versión nueva; cuando haya una, también te avisa solo
(una vez al día revisa la versión de la rama `main` de este repositorio).

**Desde el navegador:** en **Customize > Plugins**, abre el marketplace y haz clic en **Check for updates**, o activa
**Sync automatically**.

**Desde la terminal:** cada línea es un pegado.

```bash
claude plugin marketplace update soyelvaras-studio
```

```bash
claude plugin update elvaras-studio@soyelvaras-studio
```

Abre un chat nuevo después de actualizar para que Claude cargue la versión nueva.

## Para desarrollar

```
.claude-plugin/marketplace.json     el catálogo para instalarlo en Claude
elvaras-studio/                     el plugin
  .claude-plugin/plugin.json        nombre y versión
  skills/elvaras-studio/
    SKILL.md                        el flujo de edición (con la sección de marca Soy Elvaras)
    brands/soyelvaras/              colores, tipografías, logo, tono
    brands/clientes/_plantilla/     copia esta carpeta para cada cliente
    captions/  effects/  engine/    estilos de subtítulos, efectos y motor de render
    picker/                         el selector de estilo (página local)
    references/  scripts/
.claude/launch.json                 abre el selector en el navegador de la app
dev/                                elecciones de prueba del selector (no se suben)
tests/check_quality.py              falla si algún script baja la calidad de la voz o de la imagen (regla 9)
tests/e2e.py                        el Studio de punta a punta, como lo vive un comprador nuevo
.github/workflows/                  calidad.yml en cada cambio; e2e.yml en Windows, Mac Intel y Mac Apple Silicon
```

Las pruebas, en este computador:

```bash
python tests/check_quality.py
```

```bash
python tests/e2e.py --rapido
```

En GitHub, `e2e` corre sola cuando cambia la skill, y a mano desde la pestaña **Actions** ("Run workflow"). Los
resultados (resumen, render, copia para el celular y hojas de revisión) quedan como artefactos de cada corrida.

Instalar la copia de trabajo directo desde esta carpeta:

```bash
claude plugin marketplace add "C:/Users/crist/Documents/soyelvaras-studio"
```

```bash
claude plugin install elvaras-studio@soyelvaras-studio
```

Ver el selector en el navegador sin instalar nada:

```bash
python "elvaras-studio/skills/elvaras-studio/picker/serve.py" --keep-alive --port 4790 --config "dev/studio-picks.json"
```

Y abre http://127.0.0.1:4790/
