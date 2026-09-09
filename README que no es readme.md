domenteishon: https://www.odoo.com/documentation/19.0/es_419/administration/on_premise/source.html

# obligatorio tener Git y Python y PostgreSQL

clonar el repo de odoo: 
 git clone --branch 19.0 --single-branch https://github.com/odoo/odoo.git

tambien se puede la version de enterprise pero creo q piden licencia osea es pago :)

despues te creas un server en postgres, yo me cree uno aparte x las dudas jeje
despues te tenes que crear un usuario lento, click derecho y ahi en la opcion que dice create-> login/group/role; pones nombre y contraseña, yo le puse localhost y la contraseña de mi cuentasql nmas (ese usuario que creas ahi guardatelo xq lo vas a usar enseguida...) y el la seccion de permisos activa todos exepto el anteultimo

# create un entorno virtual: ctrl + c - ctrol + v :

python -m venv venv

.\venv\Scripts\Activate.ps1

# ahora instalas las dependencias :)
pip install setuptools wheel 

pip install -r requirements.txt

y si esta todo bien se activa odoo con este comando:
                #aca va el usuario que guardaste recien
python odoo-bin -r dbuser -w dbpassword --addons-path=addons -d mydb

en mi caso seria asi:                                      #aca va la base de datos que te creas en el server, 
                                                             me colgue xdxd
                                                             yo le puse odoo nmas

python odoo-bin --db_user=odoo19 --db_password=odoo19_pass --addons-path=addons -d bdl_odoo

una vez funcione dependera de donde pusite la ip pero de default es aca 
http://localhost:8069/

odoo ya te crea tambien por defecto un usuario: 
nombre:admin
contraña:admin

ahora me cree una carpetita llamada addons_caen  para editar ahi los modules xq hay mucho despelote en la carpeta de addons

modulos que voy a probar: 
# Contacts (Contactos), 
# Inventory (inventario), 
# Manufacturing (Fabricacion, xq agarra X cantidad de leche y los convierte en frasquitos/biberones), 
# Employees (Empleados), 
# Discuss / Mail (Mensajeria pro max ultra interna xq la de hablar por discord ni idea) 
# y Dashboards (pa las Métricas)

# Quality (Calidad, lo de serología y eso) ##### bueno al parecer este muchacho es de pago, podría hacerme una cuenta de prueba pero me da pereza#####, lo que no me da pereza es crearlo jeje

despues de activar los modulos

creamos el modulo custom del caen dentro de la carpeta addons_caen

la estructura de archivos queda asi:

caen_banco_leche/
    __init__.py                    # importa models
    __manifest__.py                # identidad del modulo, nombre version dependencias y archivos
    models/
        __init__.py                # importa todos los modelos uno por uno
        donante.py                 # madre donante, nombre dni zona estado etc
        consentimiento.py          # consentimiento de donacion con cant frascos y estado
        serologia.py               # los 7 estudios hiv hep b hep c htlv toxo chagas vdrl
        frasco.py                  # frasco de leche cruda con codigo qr etapa destino volumen
        pasteurizacion.py          # pasteurizacion con acidez dornic crema grasa kcal cultivos
        fraccionamiento.py         # fraccionamiento y biberon (biberon es modelo aparte)
        paciente.py                # bebe receptor con peso talla semanal etc
        nutricion.py               # plan de alimentacion y seguimiento nutricional
    views/
        menu_views.xml             # menu raiz banco de leche con submenus donantes procesos nutricion
        donante_views.xml          # pantalla de donantes con form y lista
        consentimiento_views.xml   # pantalla de consentimientos
        serologia_views.xml        # pantalla de serologias
        frasco_views.xml           # pantalla de frascos de leche
        pasteurizacion_views.xml   # pantalla de pasteurizacion con todos los campos de calidad
        fraccionamiento_views.xml  # pantalla de fraccionamiento con biberones embebidos
        paciente_views.xml         # pantalla de pacientes/bebes
        nutricion_views.xml        # pantalla de planes de alimentacion y seguimiento
    security/
        ir.model.access.csv        # permisos por modelo para los usuarios

# que hace cada archivo importante

__manifest__.py le dice a odoo como se llama el modulo y de que depende
en depends ponemos base contacts stock mrp hr
en data ponemos el csv de permisos y todos los xml de vistas

models/ es donde esta toda la logica, cada archivo define un modelo con sus campos
cada modelo es como una tabla en la base de datos pero odoo la crea sola

views/ es donde describimos las pantallas, odoo las genera automaticamente
no hace falta tocar html ni css ni nada

security/ ir.model.access.csv define que puede hacer cada usuario con cada modelo

# como se activa el modulo

reinicias odoo con el comando python odoo-bin -c odoo.conf -d bdl_odoo
pero si queres que detecte modulos nuevos o actualice algo le pones 
-u python odoo-bin -c odoo.conf -u caen_banco_leche -d bdl_odoo

despues entras a http://localhost:8069 y ahi en el menu lateral ya aparece "banco de leche"
con todos los submenus

# modelos creados

donante -> madre donante con sus datos y relacion con consentimientos serologias y frascos
consentimiento -> autorizacion para donar con vigencia y cant de frascos a imprimir
serologia -> los 7 estudios individuales hiv hep b hep c htlv toxo chagas vdrl
frasco -> frasco de leche cruda con su codigo qr etapa de leche y destino
pasteurizacion -> proceso de pasteurizacion con control de calidad completo dornic crema grasa kcal cultivos
fraccionamiento -> cabecera del fraccionamiento y biberon como modelo aparte con su qr
paciente -> bebe receptor con datos de nacimiento y planes de alimentacion
plan_alimentacion -> plan individual por paciente con volumen y frecuencia
seguimiento_nutricional -> registros de peso talla y z scores oms

# test

si el servidor esta caido levantalo con el python del venv, en mi caso es:
start-process -filepath "C:\Users\lucas\Desktop\code\BDL odoo\odoo\venv\Scripts\python.exe" -argumentlist "odoo-bin","-c","odoo.conf","-d","bdl_odoo" -workingdirectory "C:\Users\lucas\Desktop\code\BDL odoo\odoo" -windowstyle hidden

para instalar el modulo por primera vez o despues de grandes cambios usa:
python odoo-bin -c odoo.conf -d bdl_odoo -i caen_banco_leche --stop-after-init
el --stop-after-init hace que odoo instale y se apague solo, sirve para testear sin dejar el servidor corriendo
(completamente opcional pero si sos un colgado como yo sirve una banda)

# errores que salieron #parte2 

1 los one2many en donante.py usaban "donante_id" pero en los otros modelos el campo se llama "donor_id"
   hay que poner el mismo nombre en el one2many que en el many2one del modelo hijo (probablemente me quede con el ingles para mayor profesionalismo)

2 en odoo 19 el tag <tree> ya no existe, hay que usar <list>
   todos los xml tenian <tree> y hay que cambiarlos a <list>

3 el menu_views.xml tenia que cargarse primero en el manifest antes que las vistas que lo referencian
   si no odoo intenta usar el menu padre y no existe todavia

4 el odoo.conf necesita que el addons_path apunte a addons_caen tambien
   addons_path = addons,addons_caen

# datos de prueba para verificar que todo funciona

donantes creados: 3 
serologias: 14 (7 por donante, estudios hiv hep b hep c htlv toxo chagas vdrl) -> con la logica nueva, hoy 1 esta pendiente (htlv de lucia)
consentimientos: 2 (ambos activos con cant de frascos)
frascos: 3 con codigo qr -> se puede crear cualquiera sea el estado de la donante
pasteurizacion: 1 con acidez dornic 18.5, % crema, grasa, kcal/l 583.7, cultivos 24h y 48h ok

# la logica de "apta para donar"

cualquier madre puede donar, no se le impide crear un frasco aunque le falte algo
pero su leche NO se puede pasteurizar (o sea, no se puede usar para los bebes)
hasta que tenga las 7 serologias en OK y un consentimiento vigente

en la ficha de la donante aparecen 3 campos calculados:
serologias aptas / serologias pendientes / apta para donar (si/no)

# ciclo de vida del frasco (workflow)

el frasco arranca en crudo y va pasando de estado con botones en su pantalla:
crudo -> pasteurizado -> fraccionado -> entregado
(descartar se puede siempre, ej si falla un cultivo)
odoo solo muestra el boton que corresponde al estado actual y controla que no saltes pasos


# stock real con el modulo stock de odoo

cada frasco ahora se integra con el inventario real de odoo.
se crearon productos y ubicaciones internas:

productos: Leche Cruda / Leche Pasteurizada / Biberon Leche Humana
ubicaciones: Recepcion Crados, Heladera Cruda, Pasteurizacion,
Heladera Pasteurizada, Fraccionamiento, Distribucion/Entrega, Descarte

como funciona:
- al crear un frasco, entra stock de "Leche Cruda" en "Recepcion Crudos"
  (con su numero de lote = el codigo QR)
- al pasteurizar, cambia a producto "Leche Pasteurizada" y se mueve a
  "Heladera Leche Pasteurizada"
- al fraccionar, se mueve a "Fraccionamiento"
- al entregar, cambia a producto "Biberon" y se mueve a "Distribucion/Entrega"
- al descartar, se mueve a "Descarte"

asi odoo lleva el stock real (en litros, se convierte de ml) y podes ver
el inventario en el modulo de inventario/stock de odoo

la form del frasco ahora muestra:
- Lote/QR Stock (generado automaticamente con el codigo QR, en teoria)
- Producto (cambia segun la etapa del frasco)
- Ubicacion actual (donde esta el frasco fisicamente en el deposito)

# para cargar datos de prueba: xmlrpc

hay un archivo test_data.py que hace eso, se ejecuta con el python del venv
c:\Users\lucas\Desktop\code\BDL odoo\odoo\venv\Scripts\python.exe c:\Users\lucas\Desktop\code\BDL odoo\odoo\test_data.py

# alertas automaticas

se creó un modelo caen.alerta que genera notificaciones automaticamente
hay un cron que corre todos los dias y genera alertas segun:

1. serologias pendientes: si una donante tiene alguna serologia sin resultado
   genera una alerta de tipo "warning" diciendo que falta esa serologia

2. consentimientos por vencer: si un consentimiento vence en 30 dias o menos
   genera alerta, y si vence en 7 o menos dias es "critical", esto es pa probar nomas no se si realmente sea asi supongo que no

3. consentimientos vencidos: si un consentimiento ya vencio se marca como
   expirado automaticamente y genera alerta "critical"

4. stock bajo: si no hay leche cruda en recepcion genera alerta "critical"
   y si hay menos de 0.5L genera alerta "warning"

las alertas se pueden ver desde:
- el menu "Alertas" en el sidebar (dentro de Banco de Leche)
- el botón "Alertas" en el dashboard
- el botón "Refrescar Alertas" en el dashboard (regenera todo)

cada alerta tiene: tipo, severidad (info/warning/critical), donante asociada,
descripción, y estado (activa/reconocida/resuelta)


# reportes

dentro de Banco de Leche > menu "Reportes" (aparece en el "More Menu") hay:

frascos:
- Frascos por Donante (vista pivot: donante vs estado, con volumen)
- Frascos por Estado (gráfico de barras)

serologías:
- Serologías por Resultado (gráfico de torta: ok/pendiente/positivo)
- Serologías Pendientes (lista agrupada por donante)

stock:
- Stock por Ubicación (pivot: ubicación vs producto, con cantidad)
- Stock Leche Cruda (lista de quant en Recepción)
- Stock Leche Pasteurizada (lista de quant en Heladera Pasteurizada)

donantes:
- Donantes por Aptitud (gráfico: aptas vs no aptas)

extras:
- Historial de Alertas
- Seguimiento Nutricional

cada vista pivot tiene botón para descargar Excel (.xlsx)
se pueden cambiar entre vista pivot, gráfico y lista con los botones de arriba

# filtros guardados

se crearon 16 filtros reutilizables que aparecen en el panel de filtros
(icono  la barra de busqueda) de cada lista:

donantes:
- Solo Activas
- Solo Aptas para Donar
- No Aptas (con pendientes)

serologías:
- Solo Pendientes
- Solo Positivas (No aptas)
- Solo Aprobadas

frascos:
- Solo Crudos
- Solo Pasteurizados
- Solo Entregados
- Solo Descartados
- Solo para Prematuros
- Solo Calostro

consentimientos:
- Solo Vigentes
- Solo Vencidos

alertas:
- Solo Criticas
- Solo Alertas de Stock

estos son filtros compartidos (los ve cualquier usuario) con un click
aplican el filtro automaticamente sin cargar vistas


# formularios dinámicos (visibilidad)

los formularios muestran solo lo relevante según el estado de cada registro.

frasco:
- botones de flujo (Pasteurizar, Fraccionar, Entregar) visibles solo en la
  etapa correspondiente (vía statusbar)
- campos editables solo en "Crudo"; se bloquean (readonly) al avanzar de etapa
- sección "Stock" (lote, producto, ubicación) solo si ya tiene lote asignado
- alerta contextual de estado: "Leche Cruda - esperando pasteurización",
  "Leche Pasteurizada - lista para fraccionar", etc., según el estado
- indicador "Donante apta para pasteurizar" (checkbox) solo visible en Crudo
- si la donante NO es apta y el frasco está Crudo, muestra alerta roja:
  "Esta donante aún NO está apta. Complete las 7 serologías y tenga un
  consentimiento vigente antes de pasteurizar."

donante:
- la pestaña "Frascos" solo aparece si la donante tiene frascos
  (n_frascos > 0); si no tiene, se oculta para no mostrar una lista vacía

# visitas de donación (modelo caen.visita)

representa una visita de una madre donante al banco para donar leche.
menu: Banco de Leche > Donantes y Consentimientos > Visitas de donación

campos:
- donante (required), centro, fecha y hora de la visita
- estado: Programada / En curso / Completada / Cancelada
- frascos donados (one2many a caen.frasco via visit_id)
- n_frascos (computado) y volumen total (ml) (computado)
- apta_donar (relacionado de la donante)
- observaciones
- referencia autogenerada: VIS-0001, VIS-0002, ... (secuencia caen.visita)

flujo:
- los botones Marcar en Curso / Completar / Cancelar cambian el estado
- con el botón "Añadir Frasco" se abre el formulario de frasco en crudo
  pre-cargado con la donante, centro, fecha de la visita y el vínculo a la visita
- el frasco queda ligado a la visita, y la visita acumula n_frascos y volumen

relaciones:
- donante: pestaña "Visitas" en el formulario de donante (visit_ids)
- frasco: campo visit_id en el formulario y lista de frascos

# registros de distribución (modelo caen.distribucion)

registro de entrega de leche (frasco o biberón) a un paciente receptor.
menu: Banco de Leche > Procesamiento > Distribuciones

campos:
- paciente receptor (required)
- frasco/biberón entregado (required, debe estar en estado "entregado")
- fecha y hora de distribución (required)
- volumen, etapa, destino (computados del frasco)
- responsable (hr.employee)
- notas
- estado: Borrador / Confirmada
- referencia autogenerada: DIS-0001, DIS-0002, ...

validación: solo se puede vincular un frasco en estado "entregado"
(flujo Pasteurizar -> Fraccionar -> Entregar).

integraciones:
- paciente: pestaña "Distribuciones recibidas"
- menú bajo Procesamiento

# bitácora de cambios (modelo caen.bitacora)

registro inmutable de todos los cambios importantes del sistema.
menu: Banco de Leche > Bitácora (al fondo del menú principal)

campos:
- modelo, id y nombre del registro afectado
- tipo de acción: Creación / Modificación / Eliminación / Cambio de etapa / Movimiento de stock
- usuario, fecha, detalle de los cambios

seguridad:
- solo lectura para todos los usuarios (perm_read=1, write=0, create=0, unlink=0)
- inmutable: unlink() y write() levantan ValidationError

se registra automáticamente al:
- crear un frasco
- cambiar de etapa del frasco (Pasteurizar, Fraccionar, Entregar, Descartar)
- cambiar de etapa de la visita (En curso, Completar, Cancelar)
- confirmar una distribución


# errores adicionales a tratar

- el campo "numbercall" ya no existe en ir.cron, hay que quitarlo del xml
- el campo "type" de product.template solo acepta "consu", "service", "combo"
  (ya no acepta "product"). para hacer un producto almacenable hay que usar
  type="consu" + is_storable="True"
- los campos "property_cost_method" y "uom_po_id" ya no existen en Odoo 19
- los metodos de python que empiezan con _ son privados y no se pueden llamar
  via xmlrpc, hay que crear un wrapper publico sin el underscore
- las ubicaciones de stock deben tener la misma company_id que su padre
  (no se puede poner company_id=False si el padre tiene una empresa)
- en ir.filters: user_id ya no existe en Odoo 19, ahora es user_ids (many2many),
  y model_id ahora es un campo Selection (string) con el nombre del modelo
  (no un many2one con ref, se pone directamente "caen.frasco")
- ir.sequence.next_by_code devuelve cadena con prefix+padding si los tiene;
  para formatear manualmente quitar el prefix del xml. si la secuencia ya
  existía en la db con prefix, hay que borrar ir_sequence (y su ir.model.data)
  para que se recree al actualizar el módulo
- invalidate_cache ya no es método de recordset en Odoo 19: usar
  invalidate_recordset() (o invalidate_all() del modelo/env)
- _log_access = False impide usar create_uid/create_date en vistas list;
  quitar esa restricción si se necesitan esos campos en las vistas

# sidebar lateral

la navbar original de odoo se reconfiguro como sidebar vertical a la izquierda

estructura:
- caja de perfil reservada arriba (15vh, fondo oscuro, por ahora solo dice "Perfil")
- debajo estan los botones de todos los modulos con iconos
- los modulos con submenus usan acordeon (<details>/<summary> de html puro xq el nativo de odoo era un asco)

esto esta en:
- static/src/css/caen_style.css -> estilos de la sidebar
- static/src/xml/caen_profile.xml -> hereda web.NavBar y pone el html del sidebar

como funciona:
- el template caen_profile.xml hace xpath sobre <nav> del NavBar y pone el html
- el css oculta todo lo original de odoo (apps menu, brand, breadcrumbs, systray, sections, toggle)
- el css muestra .caen-sidebar con display flex
- los links son href directos a las acciones de odoo (/odoo/action-XXX)
- los ID de acciones se obtuvieron de la API /web/webclient/load_menus

acordeon:
- se usa <details>/<summary> nativo de html5
- al clickear un modulo con submenus se abre y muestra los hijos en forma de acordeon (nativamente es una panel emergente bastante molesto y estupidamente feo, despidan al que decidio eso)
- la flechita se usa con fontawesome (\f054) y gira cuando se abre


si se agrega un modulo nuevo habria que agregar el link a mano en caen_profile.xml




# verificación
esto se movera siempre hacia abajo de manera que sea mas facil encontrarlo por si me olvido
para verificar que todo funciona se puede abrir el navegador en
http://localhost:8069/odoo/
el servidor se levanta con:
python odoo-bin -c odoo.conf -d bdl_odoo