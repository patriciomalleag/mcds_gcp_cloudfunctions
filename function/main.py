import base64
import logging
import functions_framework

from google.api_core import exceptions
from utils.clients import get_compute_clients
from utils.controller import VMController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_message(msg: str):
    """
    Espera el formato: vm_name:zone:action
    Ejemplo: patriciomallea-vm:europe-southwest1-b:start
    """
    parts = msg.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid message format. Expected: vm_name:zone:action")
    vm_name, zone, action = [p.strip() for p in parts]
    return vm_name, zone, action


@functions_framework.cloud_event
def start_stop_vm(cloud_event):
    """
    Entry point para mensajes Pub/Sub.
    - data["message"]["data"]: base64 con el string vm:zone:action
    - data["message"]["attributes"]: diccionario opcional con parámetros extra (solo usado en 'create')
    """
    try:
        data = cloud_event.data
        raw = data["message"]["data"]
        message_str = base64.b64decode(raw).decode("utf-8")

        vm_name, zone, action = parse_message(message_str)
        attributes = data["message"].get("attributes", {})

        clients = get_compute_clients()
        ctrl = VMController(
            project=clients["project"],
            instances=clients["instances"],
            images=clients["images"],
        )

        ctrl.run(action=action, vm_name=vm_name, zone=zone, params=attributes)
        logger.info(f"Action '{action}' executed for VM '{vm_name}' in zone '{zone}'")

    except ValueError as ve:
        logger.error(str(ve))
    except exceptions.NotFound:
        logger.error("Resource not found.")
    except exceptions.PermissionDenied:
        logger.error("Permission denied.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
