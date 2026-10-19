#!/usr/bin/env python3
"""Soy Elvaras Studio, de punta a punta, como lo vive alguien que lo instala por primera vez.

  1. La revisión de herramientas (start.sh / start.ps1) en un computador sin Python, Node ni ffmpeg para el Studio,
     dos veces: la primera consigue todo, la segunda solo revisa.
  2. Un clip de prueba: una imagen de prueba que se mueve y la voz del propio computador diciendo dos frases con una
     pausa larga entre ellas. Nadie aparece en él.
  3. Una edición completa siguiendo SKILL.md: ingest, la lista de cortes sin la pausa, assemble, palabras, marcas,
     layout, init, armado con la guía roja, lint, instantáneas, armado limpio, render, autorrevisión y cortes.
  4. Calidad (SKILL.md regla 9): el audio unido a 320k / 48 kHz, la copia para el celular en 1080p con el MISMO audio
     del render, byte a byte, y tests/check_quality.py.
  5. Los 19 estilos de subtítulos y los 3 estilos completos: cada uno se arma y pasa el lint.
  6. update.py --check no se cae.

En GitHub corre en Windows, Mac Intel y Mac Apple Silicon (.github/workflows/e2e.yml). En un computador propio:
    python tests/e2e.py                       usa la carpeta del Studio de este computador (no toca sus elecciones:
                                              las elecciones de la prueba van en un archivo aparte)
    python tests/e2e.py --state <carpeta>     una carpeta nueva; su nombre debe terminar en elvaras-studio
    python tests/e2e.py --rapido              solo 3 estilos de subtítulos en el paso 5
Imprime una línea por paso y un resumen; termina con código 1 en el primer paso que falla. Solo biblioteca estándar.
"""
import json
import os
import platform
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'elvaras-studio', 'skills', 'elvaras-studio')
WIN = platform.system() == 'Windows'
OUT = os.path.abspath(os.environ.get('E2E_OUT') or os.path.join(ROOT, 'tests', 'out'))
FRASES = ('Claude edits my reels now. I record with my phone and it does the rest.',
          'It cuts the silences, adds captions and keeps my voice clean.')
PAUSA = 2.5                      # segundos de silencio entre las dos frases: la edición debe sacarlos
T0 = time.time()
PASOS = []

for _s in (sys.stdout, sys.stderr):      # la consola de Windows es cp1252 y los scripts imprimen símbolos
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


def opcion(nombre):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv[:-1] else None


ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
if opcion('--state'):
    ENV['CLAUDE_PLUGIN_DATA'] = os.path.abspath(opcion('--state'))


def log(texto):
    print(texto, flush=True)


def anotar(nombre, ok, codigo=0, opcional=False):
    PASOS.append({'paso': nombre, 'ok': ok, 'codigo': codigo, 'opcional': opcional})
    log(f'----- {"OK" if ok else ("FALLA (permitida)" if opcional else "FALLA")}: {nombre}')
    if not ok and not opcional:
        terminar(1)


def correr(nombre, cmd, debe=None, opcional=False, timeout=3600):
    """un paso: lo corre, muestra el final de su salida y revisa el código de salida y, si se da, un texto esperado"""
    log(f'\n##### {nombre}  [t+{time.time() - T0:.0f}s]\n$ ' + ' '.join(f'"{c}"' if ' ' in str(c) else str(c) for c in cmd))
    try:
        p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding='utf-8', errors='replace',
                           env=ENV, timeout=timeout)
        salida, codigo = (p.stdout or '') + (p.stderr or ''), p.returncode
    except (OSError, subprocess.SubprocessError) as e:
        salida, codigo = f'{type(e).__name__}: {e}', -1
    log('\n'.join(l for l in salida.splitlines() if l.strip())[-5000:])
    ok = codigo == 0 and (debe is None or re.search(debe, salida) is not None)
    if not ok and debe and codigo == 0:
        log(f'(no apareció /{debe}/)')
    anotar(nombre, ok, codigo, opcional)
    return salida


def terminar(codigo):
    os.makedirs(OUT, exist_ok=True)
    resumen = {'sistema': platform.platform(), 'maquina': platform.machine(), 'segundos': round(time.time() - T0),
               'paso': all(p['ok'] or p['opcional'] for p in PASOS) and codigo == 0, 'pasos': PASOS}
    with open(os.path.join(OUT, 'resumen.json'), 'w', encoding='utf-8') as fh:
        json.dump(resumen, fh, indent=1, ensure_ascii=False)
    log('\n' + '\n'.join(f'{"ok   " if p["ok"] else ("salta" if p["opcional"] else "FALLA")}  {p["paso"]}' for p in PASOS))
    log(f'\nRESULTADO {"PASÓ" if resumen["paso"] else "FALLÓ"} en {resumen["segundos"]} s en {resumen["sistema"]}')
    sys.exit(codigo)


def revision(nombre):
    if WIN:
        return correr(nombre, ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                               os.path.join(SK, 'scripts', 'start.ps1')], debe=r'STATUS state ')
    return correr(nombre, ['sh', os.path.join(SK, 'scripts', 'start.sh')], debe=r'STATUS state ')


def sondear(fp, archivo, flujo, campos):
    r = subprocess.run([fp, '-v', 'error', '-select_streams', flujo, '-show_entries', 'stream=' + campos,
                        '-of', 'json', archivo], capture_output=True, text=True)
    s = (json.loads(r.stdout or '{}').get('streams') or [{}])[0]
    return {k: s.get(k) for k in campos.split(',')}


def duracion(fp, archivo):
    r = subprocess.run([fp, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', archivo],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def huella_audio(ff, archivo):
    """md5 de los paquetes de audio tal como están guardados (sin decodificar): igual = el mismo audio, byte a byte"""
    r = subprocess.run([ff, '-v', 'error', '-i', archivo, '-map', '0:a:0', '-c', 'copy', '-f', 'md5', '-'],
                       capture_output=True, text=True)
    return r.stdout.strip()


def voz(ff, trabajo):
    """las dos frases con la voz del computador, unidas con PAUSA segundos de silencio -> voz.wav"""
    partes = []
    for i, frase in enumerate(FRASES):
        destino = os.path.join(trabajo, f'frase{i + 1}.' + ('wav' if WIN else 'aiff'))
        if WIN:
            ps = ('Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                  f"$s.SetOutputToWaveFile('{destino}'); $s.Speak('{frase}'); $s.Dispose()")
            correr(f'voz de prueba {i + 1} (voz de Windows)', ['powershell', '-NoProfile', '-Command', ps])
        else:
            correr(f'voz de prueba {i + 1} (say de macOS)', ['say', '-o', destino, frase])
        partes.append(destino)
    salida = os.path.join(trabajo, 'voz.wav')
    correr('unir las frases con una pausa', [ff, '-y', '-loglevel', 'error', '-i', partes[0], '-i', partes[1],
           '-filter_complex', f'[0:a]aresample=48000,apad=pad_dur={PAUSA}[a];[1:a]aresample=48000[b];[a][b]concat=n=2:v=0:a=1',
           '-ac', '2', salida])
    return salida


def tramos_con_voz(ff, clip):
    """[(entrada, salida)] de cada tramo hablado, leídos con silencedetect (lo mismo que hace una persona al cortar)"""
    r = subprocess.run([ff, '-hide_banner', '-nostats', '-i', clip, '-vn', '-af', 'silencedetect=n=-40dB:d=0.6',
                        '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    marcas = [(k, float(v)) for k, v in re.findall(r'silence_(start|end): ([\d.]+)', r.stderr or '')]
    tramos, inicio = [], 0.0
    for k, v in marcas:
        if k == 'start':
            if v - inicio > 0.3:
                tramos.append((max(0.0, inicio - 0.06), v + 0.05))
        else:
            inicio = v
    total = duracion(FP, clip)
    if total - inicio > 0.3 and (not marcas or marcas[-1][0] == 'end'):
        tramos.append((max(0.0, inicio - 0.06), total - 0.05))
    unidos = []                          # pausas cortas dentro de una frase no separan: solo la pausa larga
    for a, b in tramos:
        if unidos and a - unidos[-1][1] < 1.5:
            unidos[-1] = (unidos[-1][0], b)
        else:
            unidos.append((a, b))
    return [(round(a, 3), round(b, 3)) for a, b in unidos]


def main():
    global FP
    trabajo = os.path.join(OUT, 'trabajo')
    os.makedirs(trabajo, exist_ok=True)

    # 1. la revisión de herramientas, como la corre Claude la primera vez y después en cada sesión
    salida = revision('revisión de herramientas, primera vez')
    estado = re.search(r'STATUS state (.+?) \(', salida).group(1).strip()
    with open(os.path.join(estado, '.platform.json'), encoding='utf-8') as fh:
        reg = json.load(fh)
    anotar('el Studio quedó listo (.platform.json ready)', bool(reg.get('ready')))
    py, ff, FP = reg['python'], reg['ffmpeg'], reg['ffprobe']
    revision('revisión de herramientas, segunda vez')
    S = lambda n: os.path.join(SK, 'scripts', n)      # noqa: E731

    # 2. el clip de prueba: imagen de prueba + la voz del computador (nadie aparece en él)
    v = voz(ff, trabajo)
    clip = os.path.join(trabajo, 'clip crudo 1.mp4')            # con espacios, como los nombres reales
    correr('armar el clip de prueba', [ff, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=1080x1920:r=30',
                                       '-i', v, '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                                       '-c:a', 'aac', '-b:a', '320k', clip])

    # 3. una edición completa, paso a paso como en SKILL.md
    proyectos = os.path.join(OUT, 'reel-edits')
    proj = os.path.join(proyectos, 'e2e-reel')
    os.makedirs(proj, exist_ok=True)
    correr('1 ingest (primer modelo de voz)', [py, S('ingest.py'), proj, clip], debe=r'c1 ')
    tramos = tramos_con_voz(ff, clip)
    anotar(f'2 la pausa larga separa dos tramos con voz ({tramos})', len(tramos) == 2)
    edl = [{'id': f's{i + 1}', 'clip': 'c1', 'in': a, 'out': b, 'zoom': 1.0, 'cx': .5, 'cy': .5, 'line': FRASES[i]}
           for i, (a, b) in enumerate(tramos)]
    with open(os.path.join(proj, 'edl.json'), 'w', encoding='utf-8') as fh:
        json.dump(edl, fh, indent=1)
    salida = correr('3 assemble', [py, S('assemble.py'), proj], debe=r'total frames')
    anotar('3 los cuadros de assemble calzan (sin MISMATCH)', 'MISMATCH' not in salida)
    aroll = os.path.join(proj, 'assets', 'aroll.mp4')
    corto = duracion(FP, aroll)
    anotar(f'3 la pausa salió del corte ({duracion(FP, clip):.1f} s -> {corto:.1f} s)', corto < duracion(FP, clip) - PAUSA + 0.6)
    a = sondear(FP, aroll, 'a:0', 'codec_name,sample_rate,bit_rate')
    # se pide 320k (check_quality.py lo revisa en el código); con una voz sintética y silencios el codificador AAC gasta
    # menos, así que aquí basta con que supere los 192k de antes
    anotar(f'3 la voz unida en AAC 48 kHz sobre 192k ({a})', a['codec_name'] == 'aac' and a['sample_rate'] == '48000'
           and int(a['bit_rate'] or 0) > 192000)
    correr('4 palabras (segundo modelo de voz)', [py, S('transcribe_cut.py'), proj, 'Claude, Soy Elvaras'])
    with open(os.path.join(proj, 'words.json'), encoding='utf-8') as fh:
        palabras = json.load(fh)
    n = len(re.findall(r'"(?:w|word|text)"\s*:', json.dumps(palabras)))   # la voz del computador puede no ser inglesa
    anotar(f'4 hay palabras con tiempo para los subtítulos ({n})', n >= 12)
    correr('4 marcas', [py, S('marks.py'), proj])
    correr('5 layout (motor de render + recorte rápido)', [py, S('layout.py'), proj])
    correr('6 init', [py, S('init_project.py'), proj])

    picks = os.path.join(trabajo, 'picks-keyword.json')       # elecciones de la prueba: nunca las del usuario
    with open(picks, 'w', encoding='utf-8') as fh:
        json.dump({'mode': 'custom', 'style': None, 'captionStyle': 'keyword', 'effects': [], 'effectSections': None}, fh)
    correr('8 armado con la guía roja', [py, S('build_reel.py'), proj, '--safe', '--picks', picks])
    correr('8 lint', [py, S('hf.py'), proj, 'lint'], debe=r'0 errors')
    correr('8 instantáneas (navegador del motor)', [py, S('hf.py'), proj, 'snapshot', '--at', '0.5,2.0,4.0', '--no-end',
                                                     '--describe', 'false'])
    correr('9 armado limpio', [py, S('build_reel.py'), proj, '--picks', picks])
    render = os.path.join(proj, 'renders', 'e2e-reel-v1.mp4')
    correr('9 render', [py, S('hf.py'), proj, 'render', '-o', 'renders/e2e-reel-v1.mp4', '--quality', 'high'])
    correr('9 autorrevisión', [py, S('frames_check.py'), proj, 'renders/e2e-reel-v1.mp4'])
    correr('9 cortes + copia para el celular', [py, S('check_cuts.py'), proj, 'renders/e2e-reel-v1.mp4', '--phone'],
           debe=r'audio copied, not re-encoded')

    # 4. calidad (SKILL.md regla 9)
    vr = sondear(FP, render, 'v:0', 'codec_name,width,height')
    anotar(f'calidad: el render es 1080x1920 ({vr})', (vr['width'], vr['height']) == (1080, 1920))
    celular = os.path.join(proj, 'renders', 'e2e-reel-v1-phone.mp4')
    vc = sondear(FP, celular, 'v:0', 'codec_name,width,height')
    anotar(f'calidad: la copia para el celular es 1080p ({vc})', (vc['width'], vc['height']) == (1080, 1920))
    anotar('calidad: la copia para el celular tiene el mismo audio que el render, byte a byte',
           huella_audio(ff, render) == huella_audio(ff, celular) != '')
    correr('calidad: tests/check_quality.py', [sys.executable, os.path.join(ROOT, 'tests', 'check_quality.py')],
           debe=r'quality OK')

    # 5. cada estilo se arma y pasa el lint (sin render: eso ya se probó arriba)
    with open(os.path.join(SK, 'captions', 'styles.json'), encoding='utf-8') as fh:
        subtitulos = [s['key'] for s in json.load(fh)['styles']]
    if '--rapido' in sys.argv:
        subtitulos = [k for k in subtitulos if k in ('karaoke', 'bold', 'terminal')]
    with open(os.path.join(SK, 'picker', 'data', 'styles.json'), encoding='utf-8') as fh:
        completos = [s['key'] for s in json.load(fh)['styles']]
    elecciones = ([(f'subtítulos {k}', {'mode': 'custom', 'style': None, 'captionStyle': k, 'effects': []}) for k in subtitulos]
                  + [(f'estilo completo {k}', {'mode': 'style', 'style': k}) for k in completos])
    for nombre, eleccion in elecciones:
        archivo = os.path.join(trabajo, 'picks-' + re.sub(r'[^a-z0-9-]', '-', nombre) + '.json')
        with open(archivo, 'w', encoding='utf-8') as fh:
            json.dump(eleccion, fh)
        correr(f'{nombre}: armado', [py, S('build_reel.py'), proj, '--picks', archivo])
        correr(f'{nombre}: lint', [py, S('hf.py'), proj, 'lint'], debe=r'0 errors')

    # 6. la búsqueda de actualizaciones nunca se cae (con o sin fuente configurada)
    correr('update.py --check', [py, S('update.py'), '--check'], debe=r'STATUS update ')

    # lo que conviene mirar a ojo
    mirar = os.path.join(OUT, 'mirar')
    os.makedirs(mirar, exist_ok=True)
    for origen in (render, celular, os.path.join(proj, 'snapshots', 'contact-sheet.jpg'),
                   os.path.join(proj, 'work', 'cut_check.jpg'), os.path.join(proj, 'work', 'layout', 'check.jpg'),
                   os.path.join(proj, 'work', 'check', 'e2e-reel-v1.jpg')):
        if os.path.isfile(origen):
            with open(origen, 'rb') as a, open(os.path.join(mirar, os.path.basename(origen)), 'wb') as b:
                b.write(a.read())
    terminar(0)


if __name__ == '__main__':
    main()
