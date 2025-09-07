from google.auth import default
from google.cloud import compute_v1


def get_compute_clients():
    """
    Devuelve credenciales, project ID y clientes de Compute Engine.
    """
    credentials, project = default()
    return {
        "project": project,
        "instances": compute_v1.InstancesClient(credentials=credentials),
        "images": compute_v1.ImagesClient(credentials=credentials),
    }
