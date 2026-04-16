# 🕷️ Gaming Price Scraper - Control de Precios Gaming

Un proyecto educativo de web scraping para monitorear precios de productos gaming en diferentes tiendas en línea.

## 📋 Características

- **Scraping modular**: Fácil de agregar nuevas tiendas y juegos
- **Control de precios**: Registra históricamente los precios en CSV
- **Información completa**: Extrae seller, juego, item, precio, moneda, disponibilidad y URL
- **Timestamps automáticos**: Cada scraping incluye fecha y hora
- **Manejo robusto**: Fallbacks y manejo de errores
- **Entorno virtual**: Todas las dependencias aisladas

## 🎯 Estructura del Proyecto

```
WebScrappingGaming/
├── venv/                           # Entorno virtual de Python
├── output/                         # Directorio de archivos CSV generados
├── scrapers/                       # Módulos de scraping
│   ├── __init__.py
│   └── pagostore_scraper.py       # Scraper para Pagostore Garena
├── debug/                          # Archivos de depuración
├── main.py                         # Script principal
├── config.py                       # Configuración centralizada
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Este archivo
```

## 🛠️ Instalación y Configuración

### Requisitos previos
- Python 3.8 o superior
- pip

### Pasos de instalación

1. **Clonar o descargar el proyecto**
```bash
cd WebScrappingGaming
```

2. **Crear y activar el entorno virtual**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # En Windows
# o en Linux/Mac: source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Instalar navegadores para Playwright (opcional)**
```bash
python -m playwright install chromium
```

## 📊 Uso

### Ejecución básica

Para ejecutar el scraping de todas las tiendas configuradas:

```bash
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe main.py
```

### Salida

Se generará un archivo CSV en la carpeta `output/` con el nombre:
```
{vendedor}_{juego}_{timestamp}.csv
```

Ejemplo: `Pagostore_Free Fire_20260416_145524.csv`

## 📝 Formato del CSV

El archivo CSV contiene las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `seller` | Nombre del vendedor | Pagostore |
| `juego` | Nombre del juego | Free Fire |
| `item_id` | ID único del item | 17992 |
| `nombre_item` | Nombre descriptivo del producto | Diamond 100 + 10 Bonus |
| `precio` | Precio del producto | 3.50 |
| `moneda` | Moneda del precio | PEN |
| `disponible` | Disponibilidad (Sí/No) | Sí |
| `url_producto` | URL directa al producto | https://pagostore.garena.com/?item=17992 |
| `fecha_scrapping` | Fecha y hora del scraping | 2026-04-16 14:55:21 |

## 🔧 Configuración

Edita `config.py` para personalizar:

- **Sitios web**: Agrega nuevos vendedores en `SITES_CONFIG`
- **Juegos**: Configura qué juegos scrapecar y sus item IDs
- **Columnas CSV**: Modifica `CSV_COLUMNS` según necesites
- **Timeouts**: Ajusta `REQUEST_TIMEOUT` para conexiones lentas

### Ejemplo: Agregar un nuevo juego

En `config.py`:
```python
SITES_CONFIG = {
    "pagostore": {
        "url_base": "https://pagostore.garena.com/",
        "games": {
            "free_fire": {...},
            "roblox": {  # Nuevo juego
                "item_ids": list(range(18000, 18010)),
                "game_name": "Roblox"
            }
        }
    }
}
```

## 🔍 Agregar un nuevo vendedor

1. **Crear nuevo scraper** en `scrapers/nuevo_vendedor_scraper.py`
2. **Implementar clase** heredando de un patrón similar a `PagostoreScraper`
3. **Importar en `main.py`**
4. **Agregar configuración** en `config.py`
5. **Llamar en `main.py`** en la función principal

### Plantilla de nuevo scraper

```python
# scrapers/nuevo_scraper.py
class NuevoScraper:
    def __init__(self):
        self.base_url = "https://ejemplo.com/"
        self.seller = "NombreVendedor"
    
    def scrape_game(self, game_name, item_ids):
        results = []
        for item_id in item_ids:
            data = self.scrape_item(item_id, game_name)
            if data:
                results.append(data)
        return results
    
    def scrape_item(self, item_id, game_name):
        # Implementar lógica de scraping
        pass
```

## ⚙️ Dependencias

- **requests**: Para hacer requests HTTP
- **beautifulsoup4**: Para parsear HTML
- **lxml**: Parser HTML/XML
- **pandas**: Para manipulación de datos CSV
- **playwright**: Para renderizar JavaScript (opcional)
- **python-dotenv**: Para gestionar variables de entorno

## 🚨 Problemas comunes

### Error de encoding con emojis
```bash
$env:PYTHONIOENCODING='utf-8'
```

### Playwright no encuentra Chromium
```bash
python -m playwright install chromium
```

### Timeout en conexiones lentas
Aumenta `REQUEST_TIMEOUT` en `config.py`

## 📚 Estructura de datos devuelta

Cada scraper debe devolver una lista de diccionarios con esta estructura:

```python
{
    "seller": "Pagostore",
    "juego": "Free Fire",
    "item_id": 17992,
    "nombre_item": "Diamond 100 + 10 Bonus",
    "precio": "3.50",
    "moneda": "PEN",
    "disponible": "Sí",
    "url_producto": "https://...",
    "fecha_scrapping": "2026-04-16 14:55:21"
}
```

## 🎓 Propósito Educativo

Este proyecto fue desarrollado con fines educativos para:
- Aprender web scraping en Python
- Entender estructura de HTML y patrones de extracción
- Prácticar manejo de APIs y datos
- Trabajar con entornos virtuales y gestión de dependencias

## ⚠️ Consideraciones legales

- Respeta los términos de servicio de los sitios web
- No excedas el número de requests (implementa delays)
- Considera usar APIs oficiales cuando estén disponibles
- Algunos sitios pueden bloquear scrapers no autorizados

## 📈 Próximos pasos

- [ ] Agregar soporte para más vendedores (Gamerall, Instant Gaming, etc.)
- [ ] Crear interfaz gráfica para visualizar precios
- [ ] Implementar alertas de cambios de precio
- [ ] Base de datos para histórico de precios
- [ ] Análisis de tendencias de precios
- [ ] API REST para acceder a los datos

## 👨‍💻 Autor

Proyecto educativo de web scraping para gaming.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo licencia MIT.

---

**Nota**: Este scraper funciona con precios conocidos como fallback. Para scraping activo de sitios dinámicos, se recomienda usar Playwright o Selenium.
