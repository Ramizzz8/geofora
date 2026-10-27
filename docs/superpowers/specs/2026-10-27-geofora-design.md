# GEOFORA — Documento de diseño

> Fecha: 2026-10-27 · Autor: Andrés · Estado: borrador para aprobación

Este documento recoge **qué** vamos a construir, **por qué**, y **cada decisión tomada con su motivo**. Las decisiones marcadas como *(propuesta de Claude)* no las pidió Andrés expresamente: son sugerencias razonadas que él puede revisar o rechazar.

---

## 1. La idea en una frase

Un globo terráqueo interactivo en la web donde, al hacer click en cualquier país, se despliega un panel con lo que está pasando allí y cómo es: sus datos básicos, sus últimas noticias, su música y un resumen de su cultura.

## 2. Por qué existe

- **Para quién:** cualquier persona en internet. Es una herramienta pública y real, no una demo de portafolio.
- **Para qué se usa** (en palabras de Andrés): *por curiosidad* o *para mantenerse informado sobre el mundo hoy en día*.
  - **Visita por curiosidad:** alguien gira el globo, toca un país que apenas conoce y descubre su música, su cultura y su actualidad. → El globo debe ser bonito y fluido y el panel debe enganchar.
  - **Visita para estar al día:** alguien entra a ver qué pasa en el mundo. → Las noticias deben ser recientes, con fecha y fuente visibles, y el globo debe señalar dónde está pasando algo.

**Por qué importa esto para el diseño:** al ser una herramienta usada de verdad (no una demo), cambian tres cosas: las cuotas de las APIs gratuitas obligan a cachear en servidor, los datos deben parecer frescos y citar su fuente, y la web tiene que funcionar en móvil.

## 3. Objetivos, no-objetivos y anti-objetivos

### Objetivos (v1)
1. Globo 3D clicable con los ~195 países.
2. Panel por país con cuatro apartados: **ficha básica, noticias, música y cultura**.
3. El globo muestra por sí mismo qué países tienen más noticias en las últimas 24 h (mapa de calor). *(propuesta de Claude)*
4. Cada país tiene una URL propia y compartible: `/pais/afganistan`. *(propuesta de Claude)*
5. Funciona bien en escritorio y en móvil.
6. Desplegado en el VPS de Hetzner bajo un subdominio de `andresrami.com`.

### No-objetivos (fuera de v1, pueden llegar después)
- **Economía** (PIB, inflación, paro…) y **organizaciones/mercados** (ONU, UE, OTAN, BRICS, OPEP, Mercosur…). Formaban parte de la idea inicial pero Andrés no los eligió para la v1 → pasan a la **v2**.
- Ciudades y regiones: la unidad es el **país**.
- Cuentas de usuario, favoritos o seguimiento de países. *(propuesta de Claude: sin registro en v1)*
- Clima político (gobierno, elecciones), tiempo meteorológico.
- Contenido escrito a mano por país.

### Anti-objetivos (cosas que harían fracasar el proyecto aunque "funcione")
- **Apartados vacíos o rotos.** Un país sin música o sin noticias nunca debe mostrar un hueco: siempre un respaldo o un mensaje honesto. *Por qué:* la primera impresión de "web rota" mata una herramienta pública.
- **Noticias viejas presentadas como actuales.** Toda noticia lleva fecha y fuente visibles.
- **Click lento.** Abrir un país no debe tardar varios segundos en lo esencial.
- **Exponer claves de API** en el navegador.
- **Depender de mantenimiento manual por país** (no es sostenible con 195 países).

## 4. Alcance de la v1: los cuatro apartados

| Apartado | Qué muestra | Fuente | Por qué esta fuente |
|---|---|---|---|
| **Ficha básica** (cabecera del panel, siempre visible) | Bandera, nombre, capital, idiomas, moneda, población, hora local | **REST Countries** (descarga única → JSON estático) | Gratis, sin clave, cubre todos los países; los datos casi no cambian, así que no merece la pena consultarla en cada click. |
| **Noticias** | Titulares de las últimas 24–48 h con fuente, fecha y enlace al original | **GDELT DOC 2.0 API** | Gratis, sin clave, cobertura mundial y multilingüe, permite filtrar por país. NewsAPI/GNews tienen planes gratuitos muy limitados y prohíben uso en producción gratuita. |
| **Música** | Canciones/artistas más escuchados del país, con fragmento de 30 s | **Last.fm** (`geo.getTopTracks`) + **Deezer** (fragmentos de audio) + **MusicBrainz** (respaldo) | Last.fm da rankings por país; Deezer da previews de 30 s sin autenticación de usuario; MusicBrainz permite encontrar artistas *originarios* de un país cuando no hay ranking. |
| **Cultura** | Resumen general del país + enlace a "Cultura de X" en Wikipedia | **Wikipedia REST API (es)** | Gratuita, en español, automática para todos los países. Andrés eligió la **opción A** (resumen + enlace) frente a la B (secciones de gastronomía, fiestas, UNESCO) por ser sencilla y cubrir todos los países sin huecos. |

### Música: cadena de respaldo *(propuesta de Claude, aceptada implícitamente)*
1. Si Last.fm tiene ranking del país → mostrarlo.
2. Si no → artistas originarios del país (MusicBrainz por área / Last.fm por etiqueta de país) con su música.
3. Si tampoco → mensaje honesto: "Aún no tenemos música de aquí".

**Por qué:** las plataformas solo tienen rankings fiables de ~60–80 países. Sin respaldo, países como Afganistán saldrían vacíos, que es justo el anti-objetivo nº 1.

### Cambio tras el despliegue (2026-10-27): archivos GKG en lugar de la API
La API DOC de GDELT bloqueó al VPS (429 y conexiones sin respuesta) incluso con 5 s entre peticiones. Decidido con Andrés: las noticias se obtienen de los **archivos GKG que GDELT publica cada 15 min** (uno en inglés y otro traducido de ~65 idiomas, con ~1 h de retraso).
- Cada archivo se descarga y se lee **en memoria**; nunca se escribe en disco. *Por qué:* Andrés pidió no acumular información innecesaria.
- Una noticia se asigna a los países que más lugares menciona (como mucho 3, y solo los que tienen al menos la mitad de menciones que el principal). Esa cuenta es su **relevancia**: el panel ordena por relevancia y después por fecha.
- De cada tanda se guardan solo las 5 noticias más relevantes por país; el mapa de calor usa recuentos aparte, por lo que cuenta todas.
- Los titulares repetidos desde otras URL se muestran una vez.
- 4 descargas por hora en total en lugar de cientos de peticiones; la primera vez se recuperan las últimas 2 h.
- Se pierde la prioridad a medios del propio país (el GKG no indica el país del medio).

### Noticias: matiz importante (planteamiento original con la API)
GDELT permite filtrar por **país de la fuente** (`sourcecountry:`) y por **menciones** del país. No es lo mismo "noticias publicadas en Afganistán" que "noticias sobre Afganistán". Para la v1, la consulta combinará ambas (noticias sobre el país, con prioridad a medios del propio país) y se descartarán duplicados por URL/título. El constructor debe validar la calidad con varios países reales (uno grande, uno pequeño, uno en conflicto) antes de dar el criterio por cerrado.

### Noticias: en cualquier idioma, con traducción — decidido por Andrés
Las noticias se recogen **en cualquier idioma**. *Por qué:* limitarlas al español dejaría a muchos países casi sin titulares; en su idioma local hay mucha más cobertura y voces del propio país.

Para que el panel no sea una mezcla ilegible, se **traducen al español solo los titulares** (no los artículos completos) *(propuesta de Claude)*:
- **Cuándo:** bajo demanda, al abrir un país, no en la tarea programada. Cada titular traducido se guarda en SQLite por su hash y no se vuelve a traducir nunca. *Por qué:* traducir todos los titulares de los 195 países cada hora serían ~300.000 caracteres por ciclo y agotaría cualquier plan gratuito en horas; traduciendo solo lo que alguien abre, y una sola vez, el volumen cae a una fracción.
- **Con qué:** **DeepL API Free** (500.000 caracteres/mes gratis, la mejor calidad) como proveedor principal, detrás de una interfaz propia `traducir(texto, origen, destino)` para poder cambiarlo. Respaldo si se agota la cuota: **Argos Translate** autoalojado en el VPS (gratis e ilimitado, calidad algo menor) o Google Cloud Translation (también 500.000 gratis/mes). *Por qué una interfaz propia:* el proveedor puede cambiar sin tocar el resto del código.
- **Si la traducción falla o se agota:** se muestra el titular original con su idioma indicado. Nunca se deja vacío.
- **En la interfaz:** cada titular traducido lleva la marca "Traducido automáticamente · idioma original: árabe" y un botón para ver el original. El enlace lleva al artículo en su idioma; el navegador del usuario puede traducirlo si quiere.
- **Detección del idioma:** GDELT ya devuelve el idioma de cada artículo, así que no hace falta detectarlo; los titulares que ya están en español no se traducen.
- **Futuro:** si se añaden resúmenes con IA (ver §9), un mismo modelo podría traducir y resumir a la vez.

## 5. Decisiones técnicas y su porqué

### 5.1 Estrategia de datos: **opción C (mixta)** — elegida por Andrés

Se consideraron tres formas de obtener los datos:

| Opción | Cómo funciona | A favor | En contra |
|---|---|---|---|
| A. Bajo demanda + caché | El backend pide los datos cuando alguien hace click y los guarda unas horas | Lo más simple; no gasta cuota en países que nadie mira | Primer click lento (2–4 s); **impide el mapa de calor de noticias** porque no sabes qué pasa en un país hasta que alguien lo abre |
| B. Todo precargado | Tareas programadas recorren los 195 países para todos los apartados | Todo instantáneo; mapa de calor gratis | Gasta mucha cuota en países que casi nadie abre; más piezas que mantener |
| **C. Mixto ✅** | **Noticias precargadas** periódicamente; **música y cultura bajo demanda con caché larga**; ficha básica como JSON estático | Lo único que necesita estar al día (noticias) lo está y alimenta el mapa de calor; lo demás no malgasta cuota | Dos mecanismos distintos de obtención (tarea programada + bajo demanda) |

**Por qué C:** las noticias son el único dato que necesita frescura y verse en el globo; la música cambia como mucho semanalmente y la cultura casi nunca, así que precargarlas no compensa.

**Frecuencias (TTL) previstas:**

| Dato | Cómo se obtiene | Se refresca cada | Por qué |
|---|---|---|---|
| Ficha básica | JSON estático en el repo | Manual, ocasional | Población/moneda cambian muy poco |
| Noticias | Tarea programada (todos los países) | 30–60 min | Frescura para "estar al día". GDELT pide ~1 petición cada 5 s → 195 países ≈ 16 min por ciclo, cabe holgado en 30–60 min |
| Música | Bajo demanda, caché | 3–7 días | Los rankings cambian poco; ahorra cuota de Last.fm |
| Cultura (Wikipedia) | Bajo demanda, caché | 2–4 semanas | El resumen de un país casi no cambia |

Si una fuente externa falla, se sirve **la última versión cacheada** aunque esté caducada, indicando su fecha. *Por qué:* mejor un dato de ayer etiquetado que un apartado vacío.

### 5.2 Backend: **Python + FastAPI**

Alternativa considerada: Node + Express (mismo lenguaje que el frontend).

**Por qué Python:**
- El backend se dedica casi entero a **pedir datos a otras APIs, limpiarlos y cachearlos**, que es terreno natural de Python.
- La opción C necesita una **tarea programada** que recorra los 195 países: con APScheduler dentro de FastAPI (o `cron` en el VPS) son pocas líneas.
- **Procesar datos** (deduplicar noticias, contar artículos por país para el mapa de calor, limpiar resúmenes) es más cómodo en Python.
- **Deja la puerta abierta** a resumir, traducir o clasificar noticias con IA en el futuro, donde Python tiene el mejor ecosistema.
- Andrés **ya ha usado Python**.
- Para un estudiante de DAW, un backend en Python suma al currículum.

**Coste asumido:** dos lenguajes en el proyecto (no se comparten tipos entre front y back). Es asumible porque el frontend solo consume una API JSON.

**Piezas concretas:**
- **FastAPI**: rápido, moderno, genera documentación automática (`/docs`).
- **httpx**: peticiones asíncronas, para consultar varias fuentes en paralelo.
- **APScheduler**: tarea periódica de noticias.

### 5.3 Base de datos / caché: **SQLite**

Alternativa considerada: Redis.

**Por qué SQLite:** un único fichero, cero mantenimiento, suficiente para el volumen esperado (195 países × unas decenas de noticias + cachés). Redis solo se añadirá si algún día hay mucho tráfico concurrente. *Por qué no Redis ya:* es otro servicio más que mantener en el VPS sin necesidad real hoy.

### 5.4 Frontend: **React + Vite**

**Por qué:** es lo que Andrés ya usa en su portafolio; Vite da arranque y compilación rápidos.

### 5.5 Globo: **react-globe.gl**

Alternativas consideradas:
- **Cesium**: más parecido a Google Earth real (relieve, zoom a calle), pero mucho más pesado y complejo; ese nivel de detalle no aporta nada si la unidad es el país.
- **MapLibre** (mapa plano): ligero y muy bueno en móvil, pero pierde el efecto "globo" que hace atractiva la exploración por curiosidad.

**Por qué react-globe.gl:** da un globo 3D con polígonos de países clicables, coloreables (perfecto para el mapa de calor) y es ligero. Encaja con React.

**Geometría de países:** GeoJSON de **Natural Earth** (escala 1:110m para que cargue rápido), enlazado por código ISO-3166 con REST Countries. *(propuesta de Claude)*

### 5.6 Despliegue: **VPS Hetzner + Nginx, subdominio de andresrami.com**

**Por qué:** Andrés ya tiene el VPS y el dominio, con otras demos (Moves, Novacapital) desplegadas en subdominios; se reutiliza la misma infraestructura sin coste extra.

- Nginx sirve el frontend compilado (estático) y hace de proxy inverso hacia FastAPI (Uvicorn) en `/api`.
- FastAPI corre como servicio (systemd o Docker, a elegir por el constructor).
- HTTPS con Let's Encrypt.
- Las **claves de API** (Last.fm, DeepL) viven solo en variables de entorno del servidor. *Por qué:* nunca deben llegar al navegador.

## 6. Arquitectura

```
Navegador (React + react-globe.gl)
   │  GET /api/...
   ▼
Nginx (VPS Hetzner, subdominio andresrami.com)
   ├── sirve frontend estático
   └── proxy /api → FastAPI (Uvicorn)
                       │
                       ├── SQLite (noticias + cachés)
                       │
                       ├── Tarea programada (APScheduler, cada 30–60 min)
                       │      └── GDELT → noticias de los 195 países → SQLite
                       │
                       └── Bajo demanda (con caché)
                              ├── Last.fm / Deezer / MusicBrainz → música
                              └── Wikipedia REST (es) → cultura

Ficha básica: JSON estático generado una vez desde REST Countries
```

### Endpoints previstos (orientativos)
- `GET /api/countries` → lista ligera de países (código, nombre) para búsqueda.
- `GET /api/heatmap` → nº de noticias por país en las últimas 24 h (colorea el globo).
- `GET /api/country/{iso}/news`
- `GET /api/country/{iso}/music`
- `GET /api/country/{iso}/culture`

Cada apartado tiene su propio endpoint. **Por qué:** el panel puede pintar cada sección en cuanto llega, sin esperar a la más lenta, y un fallo en música no tumba las noticias.

## 7. Experiencia de usuario

- Al entrar: globo girando suavemente, coloreado según actividad de noticias de las últimas 24 h.
- Click en un país → el globo se centra en él y se abre un **panel lateral** (escritorio) o **hoja inferior deslizable** (móvil).
- Panel: cabecera con la ficha básica + secciones Noticias, Música y Cultura, cada una con su estado de carga y su respaldo.
- La URL cambia a `/pais/{nombre}` → se puede compartir y abrir directamente.
- Buscador de países (para quien no sabe dónde está Burkina Faso en el mapa). *(propuesta de Claude)*
- Fuente y fecha visibles en cada dato externo.
- Idioma de la interfaz: **español**. *(pendiente de confirmar, ver §10)*

## 8. Riesgos y cómo se mitigan

| Riesgo | Mitigación |
|---|---|
| GDELT devuelve noticias irrelevantes o duplicadas | Deduplicar por URL/título; validar con varios países reales; ajustar la consulta |
| Países pequeños con pocas noticias | Ampliar la ventana a 48 h–7 días si hay menos de N titulares, indicando el rango |
| Música inexistente en muchos países | Cadena de respaldo (§4) |
| Una API externa cae o cambia | Servir caché caducada con su fecha; cada apartado falla de forma aislada |
| Territorios en disputa (Kosovo, Taiwán, Sáhara Occidental, Palestina…) | Usar las fronteras y nombres de Natural Earth tal cual, sin editorializar *(propuesta de Claude)* |
| Cuota de traducción agotada | Traducir solo titulares, bajo demanda y cacheados para siempre; respaldo autoalojado (Argos) o mostrar el original |
| Licencias: música y noticias | No alojar audio ni artículos: solo previews oficiales de Deezer, titulares y enlaces al original |
| El globo 3D va lento en móviles modestos | Geometría a 1:110m, limitar efectos; si hiciera falta, modo mapa plano como plan B |

## 9. Hoja de ruta

- **v1 (este documento):** globo, mapa de calor de noticias, panel con ficha básica + noticias + música + cultura, URLs por país, buscador, móvil, despliegue.
- **v2:** economía (Banco Mundial: PIB, PIB per cápita, inflación, paro, deuda + gráfica) y organizaciones/mercados (JSON propio: ONU, UE, OTAN, BRICS, OPEP, Mercosur, G20…).
- **Ideas futuras:** resúmenes/traducción de noticias con IA, comparar países, favoritos, cuentas.

## 10. Lo que queda abierto

### Para Andrés
- Subdominio exacto (sugerencia: `geofora.andresrami.com`).

### Ya decidido
- **Nombre:** GEOFORA.
- **Idioma de las noticias:** cualquier idioma, con titulares traducidos al español (§4).

### Para quien lo construya (decisiones menores)
- systemd o Docker para el backend.
- Librería de estado/peticiones en el frontend (p. ej. TanStack Query) y estilos.
- Número exacto de titulares por país y umbral para ampliar la ventana temporal.
- Escala de color del mapa de calor.
- Estructura de carpetas (sugerencia: `frontend/`, `backend/`, `docs/`).
