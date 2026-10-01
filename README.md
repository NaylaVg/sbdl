# 🍼 SBDL — Software de Banco de Leche

## Sistema de gestión integral para el Banco de Leche Humana

Módulo personalizado desarrollado sobre **Odoo 19 Community**

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![Python 3](https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Odoo Community](https://img.shields.io/badge/Odoo-Community-714B67?style=for-the-badge)

🚧 **Proyecto en desarrollo**

---

## 📋 Descripción

**SBDL** es un sistema de gestión integral para el **Banco de Leche Humana**, desarrollado como módulo personalizado sobre **Odoo 19 Community**.

El sistema busca centralizar y digitalizar la gestión de los distintos sectores involucrados en el proceso, manteniendo la trazabilidad de la leche desde su ingreso hasta su utilización.

### 🔄 Trazabilidad principal

```text
👩 Donante
   │
   ▼
🏪 Centro de recolección
   │
   ▼
🍼 Leche cruda
   │
   ▼
♨️ Pasteurización
   │
   ▼
🧴 Fraccionamiento
   │
   ▼
📦 Stock
   │
   ▼
👶 Paciente
```

El sistema contempla además la gestión de **consentimientos, serologías, centros de recolección, asignaciones de personal, alertas, stock y reportes**.

---

## 🧰 Stack tecnológico

![Tecnologías utilizadas](https://skillicons.dev/icons?i=python,postgres,js,git,github,vscode,windows&perline=7)

| Tecnología              | Uso                          |
| ----------------------- | ---------------------------- |
| **Odoo 19.0 Community** | Framework principal          |
| **Python 3**            | Backend                      |
| **ORM de Odoo**         | Acceso y gestión de datos    |
| **PostgreSQL**          | Base de datos                |
| **OWL**                 | Framework JavaScript de Odoo |
| **QWeb**                | Plantillas                   |
| **CSS**                 | Estilos personalizados       |
| **JavaScript**          | Funcionalidades frontend     |
| **`caen_banco_leche`**  | Módulo personalizado         |

---

## 🏥 Áreas del sistema

El proyecto contempla la gestión de los diferentes sectores involucrados:

### 🍼 Banco de Leche Humana

* Registro de madres donantes.
* Centros de recolección.
* Ingreso de leche cruda.
* Identificación individual de frascos.
* Registro de serologías.
* Pasteurización.
* Stock de leche cruda y pasteurizada.
* Salida y utilización de leche.

### 👩‍🍼 Sector de Extracción

* Registro de madres que asisten al sector.
* Registro de extracción.
* Volumen extraído.
* Horarios.
* Registro de leche almacenada.
* Seguimiento del stock disponible.

### 🧴 Sector de Fraccionamiento

* Fraccionamiento de leche cruda congelada.
* Fraccionamiento de leche pasteurizada.
* Fórmulas infantiles.
* Fórmulas especiales.
* Nutro-terapéuticos.
* Control de entradas y salidas.
* Control de stock y vencimientos.

### 🩺 Sector Médico Nutricional

* Registro de alimentación indicada.
* Lactarios.
* Control de insumos.
* Seguimiento nutricional.
* Datos antropométricos.
* Evolución de peso y talla.
* Seguimiento del volumen y tipo de alimento.

---

## 🏷️ Trazabilidad mediante códigos

Cada frasco de leche debe contar con un **código de barras individual** que permita relacionarlo con:

```text
Centro de recolección
        +
      Madre
        +
      Frasco
        +
      Registro de ingreso
        +
     Responsable
```

Esto permite mantener identificada la leche durante las distintas etapas del proceso.

---

## 📁 Estructura del repositorio

```text
sbdl/
│
├── odoo/
│   ├── odoo-bin
│   └── odoo.conf
│
├── odoo.conf.example
│
└── addons_caen/
    │
    └── caen_banco_leche/
        │
        ├── __init__.py
        ├── __manifest__.py
        │
        ├── models/
        ├── views/
        ├── security/
        ├── data/
        │
        └── static/
            └── src/
                ├── css/
                ├── js/
                └── xml/
```

### 📌 Importante

La carpeta `odoo/` corresponde al código fuente del framework Odoo y **no debe modificarse directamente** para desarrollar las funcionalidades del proyecto.

El desarrollo específico se encuentra dentro de:

```text
addons_caen/caen_banco_leche/
```

---

## ⚙️ Puesta en marcha

### 1. Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd sbdl
```

### 2. Crear el entorno virtual

```powershell
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r odoo/requirements.txt
```

### 4. Configurar Odoo

Copiar:

```text
odoo.conf.example
```

como:

```text
odoo/odoo.conf
```

y completar la configuración local.

Entre los datos necesarios:

```ini
addons_path = ...
db_user = ...
db_password = ...
```

> ⚠️ **`odoo.conf` nunca debe subirse al repositorio.**

Cada integrante debe utilizar su propia configuración local.

### 5. Preparar PostgreSQL

Verificar que PostgreSQL esté instalado y funcionando y que la base de datos correspondiente esté disponible.

### 6. Actualizar el módulo

Desde `odoo/`:

```powershell
python odoo-bin -d NOMBRE_BASE -u caen_banco_leche --stop-after-init
```

La actualización debería finalizar con:

```text
Modules loaded.
```

sin errores `ERROR` o `CRITICAL`.

### 7. Iniciar Odoo

```powershell
python odoo-bin -d NOMBRE_BASE
```

Luego acceder a:

```text
http://localhost:8069
```

---

## 🌿 Git y ramas

La rama base de integración del equipo es:

```text
caen_odoo
```

Las funcionalidades se desarrollan mediante ramas específicas:

```text
feature/<nombre-descriptivo>
```

Ejemplo:

```text
caen_odoo
    │
    ├── feature/donantes
    ├── feature/pasteurizacion
    ├── feature/fraccionamiento
    └── feature/dashboard
```

### Reglas de trabajo

* Crear la rama desde `caen_odoo` actualizada.
* Mantener una rama por funcionalidad.
* Realizar commits pequeños y frecuentes.
* Cada commit debe representar un cambio lógico.
* Verificar que el trabajo propio esté commiteado antes de realizar un merge.
* Mantener actualizada la rama antes de integrar cambios.

---

## 🎨 Interfaz personalizada

El sistema cuenta con un **sidebar y header personalizados**, independientes del menú visual estándar de Odoo.

Los principales archivos relacionados son:

```text
static/src/xml/caen_profile.xml
static/src/css/caen_style.css
```

> ⚠️ Un `ir.ui.menu` puede existir correctamente en la base de datos y aun así no mostrarse en pantalla si no se incorpora también a la interfaz personalizada.

---

## 🔐 Seguridad y permisos

El módulo utiliza grupos y permisos específicos para controlar el acceso a determinadas funcionalidades.

Entre los permisos personalizados se encuentran, por ejemplo:

```text
perm_donantes
perm_asignaciones
```

Los permisos restringidos dependen de la asignación de los **Roles CAEN** correspondientes al usuario.

> ⚠️ Tener acceso de administrador en Odoo no significa necesariamente tener acceso a todas las funcionalidades personalizadas del módulo.

---

## 🚨 Alertas y controles

El sistema contempla controles y alertas relacionados con:

* 📅 Seguimiento de visitas a madres.
* 🧪 Serologías.
* 🍼 Ingreso de leche cruda.
* 🧊 Stock de leche.
* ⏳ Vencimientos.
* 📦 Stock de fórmulas.
* 🏥 Insumos del CAEN.
* 📊 Seguimiento nutricional.

---

## 📊 Reportes y estadísticas

El proyecto contempla la generación de información estadística de los distintos sectores.

Entre los datos a controlar se encuentran:

* Volúmenes de leche.
* Pasteurización.
* Descartes.
* Stock.
* Salidas.
* Alimentación.
* Seguimiento nutricional.
* Evolución antropométrica.

También se contempla la generación de estadísticas **mensuales y anuales**.

---

## 📈 Seguimiento nutricional

El sistema contempla registrar la evolución nutricional y antropométrica de los niños.

Los datos registrados pueden utilizarse para visualizar:

```text
Peso
 │
 ├── Evolución
 │
 └── Gráfica

Talla
 │
 ├── Evolución
 │
 └── Gráfica

Alimentación
 │
 ├── Volumen
 └── Tipo de alimento
```

---

## 🧪 Pasteurización

La gestión de pasteurización contempla información como:

* Madre correspondiente.
* Volumen.
* Calorías.
* Tipo de leche.
* Cantidad pasteurizada.
* Cantidad descartada.
* Stock disponible.
* Estado de serología.

También se contempla diferenciar el tipo de leche según corresponda.

---

## 🧴 Stock y fraccionamiento

El sistema contempla el control de entradas y salidas de diferentes tipos de alimentación:

```text
🍼 Leche cruda
🧊 Leche cruda congelada
🥛 Leche pasteurizada
🧃 Fórmulas infantiles
🧃 Fórmulas especiales
🥣 Nutro-terapéuticos
```

El objetivo es mantener actualizado el stock y controlar vencimientos y niveles mínimos.

---

## 🧯 Troubleshooting

Para errores comunes durante el desarrollo con Odoo, consultar:

```text
Checklist_Desarrollo_Odoo.docx
```

Algunos problemas frecuentes están relacionados con:

* XML.
* `__manifest__.py`.
* Dependencias.
* Permisos.
* `addons_path`.
* Caché del navegador.
* Actualización del módulo.
* PostgreSQL.

---

## 👩‍💻 Equipo

| Integrante | Responsabilidades |
| --- | --- |
| **Lucas S. Barrera** | Desarrollo del módulo custom; Sidebar / UI; Base de datos |
| **Nayla Vega** | Desarrollo del módulo custom; Organización de tareas; Reuniones |

---

## 🚧 Estado del proyecto

**En desarrollo.**

El sistema continúa evolucionando a medida que se incorporan y prueban nuevas funcionalidades.

---

🍼 **SBDL — Software de Banco de Leche**

*Proyecto de desarrollo para la gestión y trazabilidad del Banco de Leche Humana.*
