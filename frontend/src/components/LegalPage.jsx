import { useLang } from '../i18n'

const CONTACT = 'ajulianrague@gmail.com'
const REPO = 'https://github.com/Ramizzz8/geofora'
const Mail = () => <a href={`mailto:${CONTACT}`}>{CONTACT}</a>
const Out = ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>

function Spanish() {
  return (
    <>
      <h2>Aviso legal</h2>
      <p>
        En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información (LSSI-CE), se informa
        de que <b>geofora.andresrami.com</b> es un proyecto personal y académico (Proyecto Intermodular del
        ciclo de Desarrollo de Aplicaciones Web), sin ánimo de lucro ni actividad comercial.
      </p>
      <ul>
        <li>Titular: Andrés Ramírez</li>
        <li>Contacto: <Mail /></li>
        <li>Código fuente: <Out href={REPO}>github.com/Ramizzz8/geofora</Out></li>
      </ul>
      <h3>Contenidos de terceros</h3>
      <p>
        GEOFORA reúne información pública de otras fuentes y siempre indica cuál es. De las noticias solo muestra
        el titular, la imagen de previsualización y un enlace al artículo original, que pertenecen a cada medio.
        Las fotos de los países proceden de Wikimedia Commons y se muestran con su autor y licencia; los textos
        de cultura, de Wikipedia (CC BY-SA); la textura de la Tierra es de la NASA (dominio público). Otras
        fuentes: GDELT, REST Countries, Natural Earth, MusicBrainz, Apple Music, Deezer, Banco Mundial, FMI y Wikidata.
      </p>
      <h3>Responsabilidad</h3>
      <p>
        La información se recopila y se traduce de forma automática, por lo que puede contener errores o no estar
        actualizada. Si eres titular de algún contenido y quieres que se retire, escribe a la dirección de contacto.
      </p>

      <h2>Política de privacidad</h2>
      <p><b>GEOFORA no usa cookies</b> ni herramientas de analítica o publicidad y no tiene registro de usuarios ni
        formularios. Lo único que guarda en tu navegador es el idioma que eliges, y no sale de él.</p>
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
          <b> Wikimedia</b>; las imágenes de las noticias, de la web de cada medio; las portadas de música, de <b>Apple</b> y
          <b> Deezer</b>; y los fragmentos de música, de <b>Deezer</b>, solo cuando pulsas reproducir.
        </li>
        <li>
          Para traducir titulares, el servidor envía el texto del titular a DeepL. No se envía ningún dato tuyo.
        </li>
      </ul>
      <h3>Tus derechos</h3>
      <p>
        Como GEOFORA no conserva datos personales tuyos, no hay datos que consultar, corregir o borrar. Para
        cualquier duda puedes escribir a <Mail />. Si consideras que no se respetan tus derechos, puedes reclamar ante la{' '}
        <Out href="https://www.aepd.es">Agencia Española de Protección de Datos</Out>.
      </p>
      <p className="source">Última actualización: 30 de octubre de 2026</p>
    </>
  )
}

function English() {
  return (
    <>
      <h2>Legal notice</h2>
      <p>
        In accordance with Spanish Law 34/2002 on information society services (LSSI-CE),
        <b> geofora.andresrami.com</b> is a personal and academic project (final project of a Web Application
        Development vocational degree), non-profit and with no commercial activity.
      </p>
      <ul>
        <li>Owner: Andrés Ramírez</li>
        <li>Contact: <Mail /></li>
        <li>Source code: <Out href={REPO}>github.com/Ramizzz8/geofora</Out></li>
      </ul>
      <h3>Third-party content</h3>
      <p>
        GEOFORA brings together public information from other sources and always says which one. For news it only
        shows the headline, the preview image and a link to the original article, all of which belong to each outlet.
        Country photos come from Wikimedia Commons and are shown with their author and license; culture texts, from
        Wikipedia (CC BY-SA); the Earth texture is by NASA (public domain). Other sources: GDELT, REST Countries,
        Natural Earth, MusicBrainz, Apple Music, Deezer, the World Bank, the IMF and Wikidata.
      </p>
      <h3>Liability</h3>
      <p>
        Information is collected and translated automatically, so it may contain errors or be out of date. If you own
        any content and want it removed, please write to the contact address.
      </p>

      <h2>Privacy policy</h2>
      <p><b>GEOFORA does not use cookies</b> or analytics or advertising tools, and has no user accounts or forms.
        The only thing it stores in your browser is the language you choose, and it never leaves your browser.</p>
      <h3>What data is processed</h3>
      <ul>
        <li>
          The server is hosted by Hetzner (Germany, European Union). As with any website, your browser sends your IP
          address when connecting, but GEOFORA does not store it: the application&apos;s technical logs do not contain
          visitors&apos; IP addresses and are overwritten by size.
        </li>
        <li>
          To show some content, your browser downloads it directly from other services, which receive your IP under
          their own policies: flags, from <b>flagcdn.com</b>; country photos, from <b>Wikimedia</b>; news images, from
          each outlet&apos;s website; music covers, from <b>Apple</b> and <b>Deezer</b>; and music previews, from
          <b> Deezer</b>, only when you press play.
        </li>
        <li>
          To translate headlines, the server sends the headline text to DeepL. None of your data is sent.
        </li>
      </ul>
      <h3>Your rights</h3>
      <p>
        Since GEOFORA keeps no personal data about you, there is no data to access, correct or delete. For any
        questions you can write to <Mail />. If you believe your rights are not being respected, you can complain to the{' '}
        <Out href="https://www.aepd.es">Spanish Data Protection Agency</Out>.
      </p>
      <p className="source">Last updated: 30 October 2026</p>
    </>
  )
}

export default function LegalPage({ onClose }) {
  const { lang, t } = useLang()
  return (
    <aside className="panel legal" aria-label={t('legalLink')}>
      <button type="button" className="close" onClick={onClose} aria-label={t('close')}>×</button>
      <div className="panel-scroll">
        {lang === 'en' ? <English /> : <Spanish />}
      </div>
    </aside>
  )
}
