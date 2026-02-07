# Metrix

[![Tests](https://github.com/USERNAME/metrix/actions/workflows/tests.yml/badge.svg)](https://github.com/USERNAME/metrix/actions/workflows/tests.yml)

> **Nota:** Reemplaza `USERNAME` en el badge con tu nombre de usuario de GitHub.

**Metrix** es una herramienta CLI en Python para calcular métricas de evaluación de sistemas ASR (Automatic Speech Recognition) y otros sistemas de procesamiento de lenguaje natural. Diseñada como una alternativa robusta y moderna a `sctk sclite`, Metrix ofrece capacidades avanzadas de transformación de texto y ajustes personalizados.

## Características Principales

- ✅ **Word Error Rate (WER)** - Cálculo robusto con manejo de casos especiales
- ✅ **Character Error Rate (CER)** - Evaluación a nivel de caracteres
- 🔄 **Sistema de Adjustments** - Reemplazos, equivalencias y limpieza de texto
- 📊 **Múltiples formatos de salida** - CSV, JSON y reportes detallados
- 🎨 **CLI moderna** - Interfaz bonita y fácil de usar con Rich y Typer
- 📁 **Formatos flexibles** - Soporte para archivos TRN (nativo y sclite) y CSV compacto

## Instalación

### Requisitos

- Python 3.7 o superior
- pip

### Pasos de Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd metrix
```

2. Crear y activar un entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso Rápido

### Ejemplo Básico - WER

```bash
python metrix.py wer \
  --hypothesis samples/example_hypothesis.trn \
  --reference samples/example_reference.trn \
  --on-screen
```

### Ejemplo con Adjustments

```bash
python metrix.py wer \
  --hypothesis samples/example_hypothesis.trn \
  --reference samples/example_reference.trn \
  --adjustments samples/example_adjustments.json \
  --output results/ \
  --on-screen
```

### Ejemplo con CSV Compacto

```bash
python metrix.py wer \
  --compact-input data/input.csv \
  --output results/wer_report.txt
```

## Comandos Disponibles

### `wer` - Word Error Rate

Calcula el Word Error Rate entre hypothesis y reference.

**Opciones principales:**

| Opción | Abreviación | Descripción |
|--------|-------------|-------------|
| `--hypothesis` | `-h` | Archivo TRN con las hypotheses |
| `--reference` | `-r` | Archivo TRN con las referencias |
| `--compact-input` | `-ci` | Archivo CSV compacto (ID, reference, hypothesis) |
| `--adjustments` | `-a` | Archivo JSON con adjustments |
| `--output` | `-o` | Ruta de salida (carpeta o archivo) |
| `--case-sensitive` | `-cs` | Habilitar case-sensitive |
| `--keep-punctuation` | `-kp` | Mantener puntuación |
| `--neutralize-hyphens` | `-nh` | Reemplazar guiones por espacios |
| `--neutralize-apostrophes` | `-na` | Remover apostrofes |
| `--on-screen` | `-os` | Mostrar resultados en pantalla |
| `--sclite-format` | `-S` | Usar formato sclite en archivos TRN |

**Nota:** Las opciones `-h/-r` y `-ci` son mutuamente exclusivas. Debes usar una u otra.

### `cer` - Character Error Rate

Calcula el Character Error Rate entre hypothesis y reference. Tiene las mismas opciones que `wer`, excepto `--adjustments` (no aplica para CER).

## Formatos de Archivos

### Archivos TRN

Metrix soporta dos formatos de archivos TRN:

**Formato nativo de Metrix:**
```
audio0001.wav: this is a test sentence
audio0002.wav: want to go to the store
```

**Formato sclite:**
```
this is a test sentence (audio0001.wav)
want to go to the store (audio0002.wav)
```

Usa la opción `--sclite-format` (`-S`) cuando trabajes con archivos en formato sclite.

### CSV Compacto

El formato CSV compacto permite proporcionar hypothesis y reference en un solo archivo:

```csv
ID,reference,hypothesis
audio0001.wav,this is a test sentence,this is a test sentence
audio0002.wav,want to go to the store,wanna go to the store
```

### Archivo de Adjustments (JSON)

El archivo de adjustments permite definir transformaciones avanzadas:

```json
{
  "case_sensitive": false,
  "reference_replacements": {
    "teh": "the",
    "adn": "and"
  },
  "equivalences": {
    "want_to": ["want to", "wanna"],
    "going_to": ["going to", "gonna"],
    "dont_know": ["don't know", "dunno"]
  },
  "clean_up": [
    "wow", "huh", "ugh", "uh", "ah", "eh"
  ]
}
```

**Campos del JSON de adjustments:**

- `case_sensitive` (boolean): Si los reemplazos deben ser case-sensitive (default: `false`)
- `reference_replacements` (object): Reemplazos solo en la referencia (corrección de errores). Usa word boundaries.
- `equivalences` (object): Equivalencias entre formas válidas. La primera forma en la lista es la canónica.
- `clean_up` (array): Lista de palabras/interjecciones a remover de ambos textos

**Orden de aplicación:**
1. `reference_replacements` (solo en referencia)
2. Transformaciones básicas (case, puntuación, etc.)
3. `equivalences` (en ambos textos)
4. `clean_up` (en ambos textos)

## Salidas

Metrix genera tres tipos de archivos de salida:

1. **CSV** (`*_metrics.csv`) - Métricas en formato tabular
2. **JSON** (`*_metrics.json`) - Métricas en formato JSON
3. **Reporte** (`*_report.txt`) - Reporte detallado con:
   - Resumen de configuración
   - Resultados numéricos (con y sin adjustments si aplica)
   - Alineaciones frase por frase

Si usas `--adjustments`, el reporte mostrará métricas tanto con como sin adjustments para comparación.

## Estructura del Proyecto

```
metrix/
├── metrix.py              # Punto de entrada principal (CLI)
├── requirements.txt       # Dependencias Python
├── README.md              # Este archivo
├── src/                   # Módulos del código
│   ├── input_handler.py   # Lectura de archivos TRN y CSV
│   ├── text_transformer.py # Transformaciones básicas de texto
│   ├── adjustments_processor.py # Procesamiento de adjustments
│   ├── metrics_calculator.py # Cálculo de WER/CER con Jiwer
│   └── output_generator.py # Generación de outputs
├── test/                  # Tests unitarios
├── samples/               # Archivos de ejemplo
│   ├── example_hypothesis.trn
│   ├── example_reference.trn
│   ├── example_compact.csv
│   └── example_adjustments.json
└── documentation/         # Documentación adicional
    ├── PLAN.md            # Plan de implementación
    └── IMPLEMENTATION_SUMMARY.md # Resumen de implementación
```

## Métricas Implementadas

### ✅ Word Error Rate (WER)

WER es la métrica estándar para evaluar sistemas ASR. Metrix calcula WER de forma robusta:

- Manejo de casos especiales (referencias vacías)
- Integración con Jiwer para alineación y cálculo
- Soporte para adjustments personalizados
- Cálculo con y sin adjustments para comparación

**Fórmula:** `WER = (S + D + I) / N`

Donde:
- S = Substituciones
- D = Deletions
- I = Insertions
- N = Número total de palabras en la referencia

### ✅ Character Error Rate (CER)

CER evalúa el rendimiento a nivel de caracteres. Útil para sistemas que procesan texto sin espacios o para análisis más granular.

**Fórmula:** `CER = (S + D + I) / N`

Donde N es el número total de caracteres en la referencia.

### 🔜 Próximamente

- MER (Match Error Rate)
- TER (Translation Error Rate)
- DER (Diarization Error Rate)
- Precision, Recall, F1 y matriz de confusión (para sistemas de clasificación)

## Dependencias

- **Typer** - Framework CLI moderno
- **Rich** - Formato bonito en terminal
- **Jiwer** - Cálculo de métricas WER/CER
- **NumPy** - Operaciones numéricas
- **pandas** - Manejo de datos tabulares
- **Matplotlib** - Visualizaciones (para futuras funcionalidades)

## Ejemplos de Uso

### Ejemplo 1: Cálculo básico de WER

```bash
python metrix.py wer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -o results/
```

### Ejemplo 2: WER con adjustments y visualización

```bash
python metrix.py wer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -a adjustments.json \
  -os \
  -o results/
```

### Ejemplo 3: Usando CSV compacto

```bash
python metrix.py wer \
  -ci data/evaluation.csv \
  -o results/wer_results
```

### Ejemplo 4: CER con transformaciones

```bash
python metrix.py cer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -cs \
  -kp \
  -o results/cer_results
```

## Notas Técnicas

- **Manejo de referencias vacías:** Metrix maneja correctamente los casos donde la referencia está vacía, calculándolos manualmente ya que Jiwer no los soporta nativamente.
- **Word boundaries:** Todos los reemplazos en adjustments usan word boundaries para evitar coincidencias en substrings.
- **Orden de transformaciones:** Las transformaciones se aplican en un orden específico para garantizar resultados consistentes.
- **Compatibilidad sclite:** Metrix es compatible con el formato de archivos TRN usado por sclite, facilitando la migración.

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

[Especificar licencia aquí]

## Referencias

- [Jiwer Documentation](https://github.com/jitsi/jiwer)
- [NIST SCTK sclite](https://github.com/usnistgov/SCTK)

## Documentación Técnica

Para detalles técnicos sobre cómo se calculan las métricas y cómo funcionan las transformaciones:

- [`documentation/WER_GUIDE.md`](documentation/WER_GUIDE.md) - Guía técnica detallada sobre Word Error Rate (WER)
  - Proceso de transformaciones de texto
  - Sistema de adjustments
  - Cálculo de métricas
  - Casos especiales
  - Integración con Jiwer

- [`documentation/CER_GUIDE.md`](documentation/CER_GUIDE.md) - Guía técnica detallada sobre Character Error Rate (CER)
  - Transformaciones aplicadas
  - Cálculo a nivel de caracteres
  - Diferencias con WER
  - Casos de uso recomendados

---
