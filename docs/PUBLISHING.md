# Guía de Publicación y Distribución en PyPI

Esta guía documenta el procedimiento para empaquetar, validar y publicar oficialmente **IT Automation Toolkit (ITAT)** en el [Python Package Index (PyPI)](https://pypi.org/project/it-automation-toolkit/).

---

## 1. Arquitectura de Distribución

ITAT utiliza el estándar moderno de empaquetado **PEP 517 / PEP 621** basado en `setuptools` y `pyproject.toml`:

```
it-automation-toolkit/
├── pyproject.toml               # Metadata, dependencias, puntos de entrada
├── MANIFEST.in                  # Inclusión de activos no-Python (LICENSE, configs)
├── src/itat/
│   ├── py.typed                 # Marcador PEP 561 para compatibilidad de tipos
│   └── version.py               # Definición canónica de versión (__version__)
└── scripts/
    └── build_dist.py            # Script local de compilación y validación
```

---

## 2. Publicación Automatizada vía GitHub Actions (Recomendado)

El repositorio cuenta con un flujo de trabajo automatizado en [`.github/workflows/release.yml`](file://../.github/workflows/release.yml) que utiliza **PyPI Trusted Publishing (OIDC)**, eliminando la necesidad de gestionar contraseñas o tokens API manualmente.

### Paso 1: Configurar *Trusted Publisher* en PyPI (Solo una vez)
1. Inicia sesión en [pypi.org](https://pypi.org).
2. Ve a **Account Settings** > **Publishing** > **Add a new publisher**.
3. Selecciona **GitHub**:
   * **Owner**: `PortilloLab`
   * **Repository name**: `it-automation-toolkit`
   * **Workflow name**: `release.yml`
   * **Environment name**: `pypi`
4. Guarda la configuración. *(Repetir en [test.pypi.org](https://test.pypi.org) si se desea usar el entorno de pruebas).*

### Paso 2: Publicar una Nueva Versión
Para publicar un nuevo release:

```bash
# 1. Asegurar que la versión en pyproject.toml y src/itat/version.py esté actualizada (ej. 0.1.0)
# 2. Crear y enviar el tag de Git
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### ¿Qué hace el pipeline de GitHub Actions automáticamente?
1. Ejecuta la suite de pruebas completa en Python 3.11, 3.12 y 3.13.
2. Compila los paquetes `sdist` (`.tar.gz`) y `wheel` (`.whl`).
3. Valida la integridad del paquete con `twine check --strict`.
4. Publica en PyPI mediante OIDC token de corta duración.
5. Crea un **GitHub Release** en el repositorio adjuntando los artefactos de distribución y generando las notas de cambios.

---

## 3. Compilación y Validación Local

Antes de publicar, puedes validar la compilación localmente usando el script provisto:

```bash
# Instalar dependencias de desarrollo
pip install -e .[dev]

# Ejecutar el script de construcción y validación
python3 scripts/build_dist.py
```

El script verificará:
* Que la estructura interna del archivo `.whl` contenga todos los submódulos (`commands`, `core`, `skills`, `reports`, `connectors`).
* Que el punto de entrada de consola (`itat = itat.cli:main`) esté registrado.
* Que el `.tar.gz` incluya `LICENSE`, `README.md` y plantillas de configuración.
* Que `twine check` valide la metadata del paquete.

### Prueba de Instalación Local del Wheel
Puedes instalar y verificar el archivo `.whl` generado en un entorno limpio:

```bash
# Crear entorno virtual de prueba
python3 -m venv /tmp/test-itat-env
source /tmp/test-itat-env/bin/activate

# Instalar el wheel recién compilado
pip install dist/it_automation_toolkit-*.whl

# Verificar comando global
itat version
itat doctor

# Limpiar entorno
deactivate
rm -rf /tmp/test-itat-env
```

---

## 4. Publicación Manual con Twine (Alternativa)

Si deseas subir manualmente a PyPI o TestPyPI:

```bash
# Subir a TestPyPI
twine upload --repository testpypi dist/*

# Subir a PyPI Oficial
twine upload dist/*
```
