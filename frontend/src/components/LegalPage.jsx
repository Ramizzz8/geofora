const CONTACT = 'ajulianrague@gmail.com'
const UPDATED = '30 de octubre de 2026'

export default function LegalPage({ onClose }) {
  return (
    <aside className="panel legal" aria-label="Aviso legal y privacidad">
      <button type="button" className="close" onClick={onClose} aria-label="Cerrar">×</button>
      <div className="panel-scroll">
        <h2>Aviso legal</h2>
        <p>
          En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información (LSSI-CE), se informa
          de que <b>geofora.andresrami.com</b> es un proyecto personal y académico (Proyecto Intermodular del
          ciclo de Desarrollo de Aplicaciones Web), sin ánimo de lucro ni actividad comercial.
        </p>
        <ul>
          <li>Titular: Andrés Ramírez</li>
          <li>Contacto: <a href={`mailto:${CONTACT}`}>{CONTACT}</a></li>
          <li>Código fuente: <a href="https://github.com/Ramizzz8/geofora" target="_blank" rel="noopener noreferrer">github.com/Ramizzz8/geofora</a></li>
        </ul>
        <h3>Contenidos de terceros</h3>
        <p>
          GEOFORA reúne información pública de otras fuentes y siempre indica cuál es. De las noticias solo muestra
          el titular, la imagen de previsualización y un enlace al artículo original, que pertenecen a cada medio.
          Las fotos de los países proceden de Wikimedia Commons y se muestran con su autor y licencia; los textos
          de cultura, de Wikipedia (CC BY-SA); la textura de la Tierra es de la NASA (dominio público). Otras
          fuentes: GDELT, REST Countries, Natural Earth, MusicBrainz, Last.fm y Deezer.
        </p>
        <h3>Responsabilidad</h3>
        <p>
          La información se recopila y se traduce de forma automática, por lo que puede contener errores o no estar
          actualizada. Si eres titular de algún contenido y quieres que se retire, escribe a la dirección de contacto.
        </p>

        <h2>Política de privacidad</h2>
        <p><b>GEOFORA no usa cookies</b> ni herramientas de analítica o publicidad, no tiene registro de usuarios ni
          formularios y no guarda datos en tu navegador.</p>
        <h3>Qué datos se tratan</h3>
        <ul>
          <li>
            El servidor está alojado en Hetzner (Alemania, Unión Europea). Como en cualquier web, tu navegador envía
            tu dirección IP al conectarse, pero GEOFORA no la guarda: los registros técnicos de la aplicación no
            contienen la IP de quien visita y se sobrescriben por tamaño.
          </li>
          <li>
            Al mostrar ciertos contenidos, tu navegador los descarga directamente de otros servicios, que reciben tu
            IP según sus propias políticas: las banderas, de <b>flagcdn.com</b>; las fotos de los países, de
            <b> Wikimedia</b>; las imágenes de las noticias, de la web de cada medio; y los fragmentos de música, de
            <b> Deezer</b>, solo cuando pulsas reproducir.
          </li>
          <li>
            Para traducir titulares, el servidor envía el texto del titular a DeepL. No se envía ningún dato tuyo.
          </li>
        </ul>
        <h3>Tus derechos</h3>
        <p>
          Como GEOFORA no conserva datos personales tuyos, no hay datos que consultar, corregir o borrar. Para
          cualquier duda puedes escribir a <a href={`mailto:${CONTACT}`}>{CONTACT}</a>. Si consideras que no se
          respetan tus derechos, puedes reclamar ante la{' '}
          <a href="https://www.aepd.es" target="_blank" rel="noopener noreferrer">Agencia Española de Protección de Datos</a>.
        </p>
        <p className="source">Última actualización: {UPDATED}</p>
      </div>
    </aside>
  )
}
