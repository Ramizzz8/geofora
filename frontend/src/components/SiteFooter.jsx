import { Link } from 'react-router-dom'
import { useLang } from '../i18n'

const LANGUAGES = [['es', 'ES', 'Español'], ['en', 'EN', 'English']]

export default function SiteFooter() {
  const { lang, setLang, t } = useLang()
  return (
    <footer className="site-footer">
      <div className="lang-switch">
        {LANGUAGES.map(([code, label, name]) => (
          <button key={code} type="button" lang={code} aria-label={name} aria-pressed={lang === code}
            onClick={() => setLang(code)}>
            {label}
          </button>
        ))}
      </div>
      <Link to="/legal">{t('legalLink')}</Link>
    </footer>
  )
}
