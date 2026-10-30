# GEOFORA v3 — Público y propuesta de valor

> Fecha: 2026-10-30 · Autor: Andrés · Estado: aprobado (clasificador antes que usuarios)
> Complementa a `2026-10-27-geofora-design.md`. Lo marcado como *(propuesta de Claude)* no lo pidió Andrés expresamente.

## 1. Por qué este documento

GEOFORA es hoy un explorador atractivo, pero no resuelve una necesidad concreta de nadie en particular. Es su punto débil para el módulo de proyecto y hace que las fases siguientes (usuarios, IA, panel, alertas) parezcan añadidos sueltos. Elegir un público les da un sentido común.

## 2. Público — decidido por Andrés

**Quienes siguen la actualidad internacional.** Núcleo concreto: estudiantes de Periodismo y de Relaciones Internacionales. *(El núcleo es propuesta de Claude.)*

**Por qué:**
- Las Fases 4 a 8 responden todas a su necesidad.
- Son fáciles de encontrar para las pruebas con usuarios de la Fase 9.
- Se descartó secundaria porque mostrar noticias de guerras o violencia sin filtrar a menores es un riesgo y las alertas apenas aplican; y empresas y analistas, porque exigen una fiabilidad que GDELT no garantiza y son difíciles de conseguir como usuarios de prueba.

### Persona de referencia

Lucía, 21 años, estudia Relaciones Internacionales y sigue el Sahel y el Cáucaso para un trabajo de clase. *(Ficticia, a validar en la Fase 9.)* Hoy revisa varios medios, en varios idiomas, y se entera tarde de lo que no sale en portada.

## 3. Propuesta de valor

> **GEOFORA: el monitor de actualidad internacional. Sigue los países que te importan, ve de qué se habla en cada uno y entiende qué está cambiando.**

**Necesidad:** «en 2 minutos al día, saber qué pasa en los países que me importan, por temas, y que me avise si ocurre algo importante».

**Qué nos diferencia:** Google News, X y similares organizan la actualidad por noticia o por persona. GEOFORA la organiza por **lugar**: se ve de un vistazo qué países y temas se mueven hoy, en más de 60 idiomas y traducidos.

**El modo exploración no se elimina.** El globo, la música, la cultura, las fotos y la economía siguen ahí: son lo que atrae a quien llega por curiosidad y dan contexto al país que se sigue.

### Uso diario previsto

1. Entra e inicia sesión.
2. Ve sus países seguidos con lo nuevo desde su última visita y el resumen de cada uno.
3. Filtra por tema o abre un país para ver el detalle y las noticias originales.
4. Si algo se dispara mientras no está, le llega una alerta.

## 4. Qué implica para cada fase

| Fase | Qué aporta a este público | Decisiones ya orientadas |
|---|---|---|
| **4. Usuarios** | Cuentas y países seguidos: es lo que convierte una visita en un hábito | Registro por correo y contraseña cifrada; roles usuario y administrador; descargar y borrar la cuenta |
| **5. Clasificador** | «De qué se habla»: temas por noticia y filtro del globo | Ver §5 |
| **6. Panel** | «Qué está cambiando»: evolución, comparativas y tendencias | Empieza por «qué se mueve hoy»: actividad de las últimas 24 h frente a la media de los días anteriores |
| **7. Alertas** | «Avísame si ocurre algo»: subidas de actividad o temas en países seguidos | Primero avisos dentro de la web; el correo después, porque enviar correos requiere un proveedor |
| **8. Resumen IA** | «En 2 minutos»: resumen diario de cada país seguido | Solo países seguidos y siempre con enlaces a sus fuentes |

### Orden: se adelanta el clasificador *(propuesta de Claude)*

Orden acordado hasta ahora: usuarios → clasificador → panel → alertas → resumen.
**Orden aprobado: clasificador → usuarios → panel → alertas → resumen.**

**Por qué:** los temas son lo que da valor a seguir un país, y se ven y se pueden probar sin cuenta. Además, el clasificador es lo que el profesor está dando ahora mismo. El coste es que usuarios y roles, la mayor laguna frente a los RA4 y RA6, se retrasan una fase. Si hay una entrega próxima de esos RA, conviene mantener el orden original.

## 5. Riesgo a resolver en la Fase 5: qué aporta un clasificador propio

Los archivos de GDELT ya traen etiquetas de temas en cada noticia. Entrenar un modelo solo para imitarlas no aportaría nada a la web, y un profesor puede preguntarlo en la defensa. Por eso:

1. **Base de comparación:** convertir las etiquetas de GDELT a nuestros temas con reglas.
2. **Modelo propio:** entrenado con esas etiquetas.
3. **Conjunto de prueba:** unos 300 titulares etiquetados a mano, en varios idiomas.
4. **Se publica el que gane con las métricas**, y la comparación va a la memoria, salga como salga.

Queda para el diseño de la Fase 5 decidir cómo tratar los titulares en idiomas que el modelo no conozca.

## 6. Cambios de esta fase (pequeños, sin funciones nuevas)

Se aplican tras aprobar este documento, en español y en inglés:

- **Lema y portada:** «El monitor de actualidad internacional» y una línea con lo que la web ya hace hoy. La promesa completa de §3 (seguir países, ver cambios) se publicará cuando existan esas funciones.
- **Buscadores y redes:** títulos y descripciones de `backend/app/seo.py`, que hoy presentan GEOFORA solo como «el mundo en un globo 3D».
- **Memoria:** se actualiza en la Fase 9 con este público y su justificación.

## 7. Cómo sabremos si funciona

| Pregunta | Cómo se mide | Objetivo |
|---|---|---|
| ¿Cumple «en 2 minutos»? | Prueba con 5 estudiantes o más: tiempo para explicar qué pasa en dos países | ≤ 2 minutos |
| ¿Se entiende para qué sirve? | Tras ver la portada 10 segundos, decir qué hace la web | 4 de cada 5 |
| ¿Lo usarían? | Cuestionario final: «¿lo usarías cada semana?» | Mayoría a favor |
| ¿Vuelven? | Usuarios activos por semana, una vez existan las cuentas | Medir, sin objetivo aún |
| ¿Llega gente? | Visitas en GoatCounter | Medir, sin objetivo aún |

GoatCounter no identifica a las personas, así que no sirve para saber si vuelven: eso solo se podrá medir con las cuentas, y de forma agregada. Los objetivos son orientativos.

## 8. Fuera de alcance

- Noticias escritas o verificadas por nosotros: GEOFORA agrega y siempre enlaza a la fuente.
- Una app móvil nativa, redes sociales o comentarios.
- Ciudades y regiones: la unidad sigue siendo el país.
- URLs propias para el inglés: solo si los datos muestran interés internacional.

## 9. Riesgos

| Riesgo | Respuesta |
|---|---|
| Ruido de GDELT: noticias mal asignadas a un país | Lo muestran las pruebas; el clasificador y la puntuación de relevancia lo reducen; las fuentes siempre están visibles |
| Un resumen con IA inventa datos | Resúmenes con enlaces a las noticias usadas y marcados como generados por IA |
| Con cuentas ya hay datos personales | Política de privacidad, borrado de cuenta y solo los datos imprescindibles (Fase 4). «No tiene registro de usuarios» dejará de ser cierto en la página legal |
| Poco tiempo: cinco fases grandes por delante | Cada fase se publica terminada; si falta tiempo, se recorta desde el final (resumen IA y correo) |
