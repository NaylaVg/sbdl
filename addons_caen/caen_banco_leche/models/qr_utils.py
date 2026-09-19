import base64
import io
import logging
from odoo import _

_logger = logging.getLogger(__name__)

# mapeo de modelos a su acción de ventana en Odoo
_ACCIONES_POR_MODELO = {
    'caen.frasco': 'caen_banco_leche.action_caen_frasco',
    'caen.pasteurizacion': 'caen_banco_leche.action_caen_pasteurizacion',
    'caen.biberon': 'caen_banco_leche.action_caen_fraccionamiento',
}


def _obtener_url_servidor(env):
    """Lee la URL base del servidor desde odoo.conf.
    Si no está configurada, usa http://localhost:8069.
    El sysadmin agrega esta línea al odoo.conf durante el deploy:
        caen_server_url = http://192.168.1.50:8069
    """
    from odoo.tools import config as odoo_config
    return odoo_config.get('caen_server_url', 'http://localhost:8069').rstrip('/')


def construir_url_registro(env, modelo, registro_id):
    """
    Construye la URL que abre directamente el formulario de un registro en Odoo.
    Ejemplo: http://192.168.1.50:8069/odoo/action-caen_banco_leche.action_caen_frasco/37

    Args:
        env: entorno Odoo (self.env)
        modelo: nombre técnico del modelo (ej: 'caen.frasco')
        registro_id: ID entero del registro

    Returns:
        string con la URL completa, o None si el modelo no tiene acción configurada
    """
    accion_xmlid = _ACCIONES_POR_MODELO.get(modelo)
    if not accion_xmlid:
        return None
    base = _obtener_url_servidor(env)
    return f"{base}/odoo/action-{accion_xmlid}/{registro_id}"


def generar_qr_imagen(texto, box_size=10, border=2):
    """
    Genera una imagen PNG de un código QR a partir de un texto.

    Args:
        texto: el string que se codifica en el QR (URL o identificador)
        box_size: tamaño de cada cajita del QR en píxeles
        border: cantidad de cajitas de borde blanco alrededor del QR

    Returns:
        bytes con la imagen PNG CODIFICADA EN BASE64 (formato que esperan
        los campos Binary de Odoo), o None si falla.
    """
    try:
        import qrcode
        from PIL import Image

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(texto)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue())

    except ImportError:
        _logger.warning(
            "La librería 'qrcode' no está instalada. "
            "Ejecutá: pip install qrcode[pil]"
        )
        return None
    except Exception as e:
        _logger.error("Error al generar QR para '%s': %s", texto, e)
        return None
