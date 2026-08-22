Tabla 1: collection_centers (Centros de Recolecta para el que no sepa Francés)

Es una tabla "padre". Toda madre, frasco, extraccion y personal esta vinculado a un centro. Sin centros no hay datos
Campo	                            Por que lo puse
id	                                Id xd
code	                            Abreviatura corta: SPE, VID, PED, CS, PERR. Sirve para armar los codigos de barra (SPE-M01-F123)
name	                            Nombre completo del centro (en caso de haber muchos sepa de donde salio/pertenece)
address	                            Direccion fisica del centro
phone	                            telefono de contacto del centro
responsible	                        Persona a cargo del centro
is_active	                        Si el centro sigue operando o no (por si cierra temporalmente)
created_at                        	Fecha de alta en el sistema


Tabla 2: donors (Donantes)
Esta tabla guarda quién da la leche y también se decide si la madre es apta. Si serology_status no es ok, el sistema debe impedir (bloquear) que se generen frascos de leche para pasteurizar de esta madre

id	                                será necesario poner siempre xq puse id? tal vez...
donor_code	                        La clave: Aquí se genera el identificador único (ej: M01). Este código es el que se usa para hacer el QR del frasco: CENTRO-DONANTE-FRASCO
first_name / last_name	            Identidad de la donante
dni	                                Para evitar duplicados y cruzar datos médicos legales.
serology_status	                    Crítico: pending, ok, rejected. Define si su leche puede pasar a pasteurización.
status	                            active, suspended, dismissed.
center_id	                        Relación: Para saber cual centro se hizo cargo de la donante.


Tabla 3: visits (Hojas de Ruta)
Esta tabla controla el trabajo de campo y asegura que no se pierdan donantes
Por que se pidió "alarma si una madre no fue visitada en 7 días" y esta tabla es la que permite comparar la fecha actual contra la última visit_date para disparar esa notificación automática

donor_id	                        Vincula la visita a una madre específica
visit_date	                        Fecha real en que se pasó a buscar la leche
volume_raw_ml	                    Cuánta leche cruda se recolectó en esa visita
responsible	                        Quién fue a buscar la leche (chofer/técnico)
next_visit_due	                    Alarma: Calcula la fecha límite para la próxima visita (7 días)


tabla 4: milk_batches (frascos de leche cruda)
esta es la tabla central que une todo el flujo, cada frasco es un objeto único con su propio qr, si algo sale mal, el sistema busca todos los registros vinculados a ese donante y los marca para descarte automático

barcode	                            el contenido del qr: centro-madre-numero, es la clave para la trazabilidad
donor_id	                        relaciona el frasco con la madre que lo donó
volume_ml	                        cantidad de leche cruda
milk_type	                        diferencia entre leche para prematuros o término
status	                            indica en qué etapa está: cruda, pasteurizada o descartada
expiration_date                 	la fecha clave para la alarma automática de vencimiento al mes
visit_id	                        vincula el frasco con la visita específica en la que se recolectó


tabla 5: pasteurization_records (pasteurización)
este es el punto de no retorno, el frasco crudo se transforma en leche segura o si un lote falla el control de calidad, el sistema tiene que saber para no enviarlo a fraccionamiento

batch_id	                        conecta con el frasco crudo original para mantener trazabilidad completa
new_barcode	                        el nuevo qr que se genera después del proceso, ahora identifica leche pasteurizada
method	                            indica qué tipo de pasteurización se usó, holder a 62.5° o flash a 72°
temp_celsius	                    registro exacto de la temperatura alcanzada para auditoría
quality_result	                    si pasó o no el control de calidad post-pasteurización
discarded	                        si el lote se descartó, lo que genera notificación automática en inventario


tabla 6: donor_dismissals (altas de madres)
esta tabla registra cuándo una madre deja de ser donante activa, cuando se registra un alta aquí, el sistema debe cambiar automáticamente el estado de la madre en la tabla donors a inactiva y bloquear la generación de nuevos frascos de leche de esa donante

donor_id	                        vincula el alta con la madre específica
dismissal_date	                    fecha exacta en que se dio de baja
reason	                            motivo de la baja, médica, voluntaria o por reincorporación
dismissed_by	                    quién registró el alta, para control de auditoría
can_reenter	                        indica si la madre puede volver al programa en el futuro


tabla 7: internal_extractions (extracción interna)
acá se registra cuando una madre dona leche directamente dentro del CAEN en vez de por visita, se conecta por primera vez la madre con el bebé receptor, es decir empieza la trazabilidad completa de leche madre -> paciente

donor_id	                       madre que donó
patient_id	                       bebé que recibe la leche, si se usó en ese momento
batch_id	                       frasco nuevo que se genera si la leche se congela en vez de usarse
extraction_staff_id	               enfermera o técnica que hizo la extracción
volume_ml	                       cuánto se extrajo
frozen	                           si se congeló para después o se usó inmediatamente
 

tabla 8: formulas (catálogo de fórmulas y nutroterápicos)
esta es una tabla catálogo que lista todo lo que se puede alimentar a los bebés, cada movimiento de entrada o salida de stock en stock_entries y stock_exits referencia esta tabla para saber qué se está moviendo, cuánto queda y si vence pronto

name	                            nombre del producto, NAN, Enfamil, etc
brand	                            marca del producto
type	                            clasifica si es fórmula infantil, especial o nutroterápico
unit_measure	                    en qué unidad se mide, gramos, ml o porciones
min_stock_alert	                    cantidad mínima antes de que salga la alarma automática de stock bajo
requires_prescription	            si necesita indicación médica para ser administrada


tabla 9: stock_entries (ingresos/entradas de stock)
cada vez que entra algo nuevo al inventario se registra acá, se conecta la leche pasteurizada con el inventario, cuando pasteurization_records genera un lote nuevo, automáticamente se crea un registro aquí con el stock disponible

formula_id	                       si el ingreso es una fórmula, referencia al catálogo
pasteurization_id	               si el ingreso es leche pasteurizada del lote recién procesado
quantity	                       cuántas unidades entraron
expiration_date	                   fecha de vencimiento, la que dispara la alarma automática
pharmacy_request_date	           cuándo se pidió a farmacia o librería, útil para control de demoras
lot_number	                       número de lote del proveedor para trazabilidad externa


abla 10: stock_exits (egresos/salidas de stock)
acá se registra cada vez que sale algo del inventario, ya sea para alimentar a un bebé o para descartar, se conecta la planilla diaria de salida de alimentación artificial que pidió Ivana, cada vez que se alimenta a un bebé se genera un registro que decrementa el stock automáticamente

stock_entry_id	                      conecta con el ingreso original para saber qué lote se está usando
patient_id	                          bebé que recibe el alimento
exit_type	                          clasifica si es leche pasteurizada, cruda, fórmula o alimentación manual
quantity	                          cuánto salió
reason	                              si fue para alimentar, donar, descartar o transferir
center_id	                          a qué centro se trasladó el producto


tabla 11: stock_alerts (alarmas automáticas)
esta tabla no la llenan los usuarios, el sistema la genera solo cuando detecta un problema, esta es la columna vertebral del sistema de alertas que Ivana pidió sí o sí, cada vez que un stock baja del mínimo, un frasco está por vencer o una madre no fue visitada en 7 días, el sistema inserta un registro acá automáticamente


alert_type	                            qué tipo de alarma es: stock bajo, vencimiento o visita no realizada
entity_type	                            a qué entidad pertenece: fórmula, frasco o stock
severity	                            cuán urgente es: informativa, de advertencia o crítica
message	                                texto descriptivo del problema para que el usuario entienda rápido
is_acknowledged	                        si alguien ya vio y atendió la alarma


tabla 12: patients (bebés receptores)
acá se registra cada bebé que recibe leche o fórmula del CAEN, esta tabla es el punto de llegada de toda la trazabilidad, de acá salen los planes de alimentación y el seguimiento nutricional con gráficas automáticas que pidió Ivana

patient_code	                        código único del bebé para identificarlo en todo el sistema
first_name	                            nombre del bebé
birth_date	                            fecha de nacimiento, base para calcular edad en días
birth_weight_g	                        peso al nacer en gramos, punto de partida de las gráficas
gestational_age_weeks	                semanas de gestación, clave para saber si es prematuro
mother_id	                            si la madre es donante del mismo sistema, se vincula directo
status	                                si está activo, dado de alta o transferido


tabla 13: feeding_plans (planes de alimentación)
acá se guarda qué leche o fórmula recibe cada bebé y en qué cantidad se conecta la indicación médica con el inventario, cuando un médico indica que un bebé necesita X ml de fórmula al día, el sistema debe descontar eso del stock automáticamente y verificar que alcance

patient_id	                           bebé al que se le asigna el plan
formula_id	                           si recibe fórmula, referencia al catálogo
feeding_type	                       si es leche pasteurizada, cruda, fórmula o mixta
volume_ml_per_feed	                   cuántos ml recibe en cada toma
feeds_per_day	                       cuántas tomas tiene por día
total_daily_ml	                       ml totales diarios, se calcula automáticamente
prescribed_by	                       médico o nutricionista que indicó el plan
status	                               si el plan está activo, modificado o cancelado


tabla 14: nutrition_tracking (seguimiento nutricional)
acá se guardan las mediciones de cada bebé para generar las gráficas automáticas de crecimiento que Ivana quiso sí o sí, el sistema compara el peso y la talla del bebé con las tablas de la OMS y grafica la evolución mes a mes automáticamente

patient_id	                           bebé al que se le toman las medidas
measurement_date	                   fecha de la medición
weight_g	                           peso actual en gramos
height_cm	                           talla actual en centímetros
weight_percentile_oms	               percentil de peso según curvas de la OMS
height_percentile_oms	               percentil de talla según curvas de la OMS
daily_kcal	                           calorías totales que ingiere al día
feeding_plan_id	                       vincula con el plan activo en ese momento


tabla 15: staff (personal del CAEN)
acá se registra todo el personal que opera el sistema, una enfermera no puede modificar planes de alimentación y un técnico de extracción no puede cambiar stock de fórmulas, el rol define los permisos

employee_code	                       código único de cada empleado
role	                               define qué puede hacer: admin, médico, nutricionista, enfermera, técnica de extracción
center_id	                           centro donde trabaja habitualmente
email	                               para login y notificaciones
is_active	                           si sigue trabajando en el CAEN


tabla 16: daily_assignments (asignaciones diarias)
esta tabla sirve para saber quién es responsable de cada sector y centro durante el día es fundamental para la responsabilidad sanitaria, si ocurre un error en el pasteurizado o en la entrega de leche, el sistema registra exactamente qué persona estuvo a cargo ese día, cumpliendo con los requisitos de auditoría

assignment_date	                       fecha de la jornada
staff_id	                           empleado asignado
center_id	                           centro donde cumplirá funciones ese día
role_day	                           función específica del día: encargada de pasteurización, nutricionista de guardia, etc
shift	                               turno: mañana, tarde, noche


tabla 17: audit_log (registro de auditoría)
esta tabla no la edita nadie manualmente, cada acción que se hace en el sistema queda registrada acá automáticamente, si mañana una auditoría pregunta quién autorizó el descarte de un frasco o quién cambió el plan de alimentación de un bebé, esta tabla lo responde con exactitud absoluta y no se puede borrar ni modificar

timestamp	                          fecha y hora exacta de la acción
staff_id	                          quién hizo la acción
action	                              qué hizo: crear, modificar, eliminar, cambiar estado o escanear un qr
entity_type	                          sobre qué entidad actuó: donante, frasco, stock, paciente
entity_id	                          el registro exacto que modificó
old_values	                          el valor anterior antes del cambio
new_values	                          el valor nuevo después del cambio
ip_address	                          desde qué computadora se hizo
device_info	                          desde qué dispositivo