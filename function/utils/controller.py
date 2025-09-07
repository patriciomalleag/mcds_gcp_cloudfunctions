from google.cloud import compute_v1


class VMController:
    """
    Controlador OOP para VMs de Compute Engine.
    Soporta: start, stop, create, delete.
    """

    def __init__(self, project: str, instances: compute_v1.InstancesClient, images: compute_v1.ImagesClient):
        self.project = project
        self.instances = instances
        self.images = images

    def run(self, action: str, vm_name: str, zone: str, params: dict = None):
        params = params or {}
        action = (action or "").strip().lower()
        if action == "start":
            self._start(vm_name, zone)
        elif action == "stop":
            self._stop(vm_name, zone)
        elif action == "create":
            self._create(vm_name, zone, params)
        elif action == "delete":
            self._delete(vm_name, zone)
        else:
            raise ValueError(f"Invalid action: {action}")

    # ----- Acciones -----

    def _start(self, vm_name: str, zone: str):
        req = compute_v1.StartInstanceRequest(project=self.project, zone=zone, instance=vm_name)
        self.instances.start(request=req)

    def _stop(self, vm_name: str, zone: str):
        req = compute_v1.StopInstanceRequest(project=self.project, zone=zone, instance=vm_name)
        self.instances.stop(request=req)

    def _delete(self, vm_name: str, zone: str):
        req = compute_v1.DeleteInstanceRequest(project=self.project, zone=zone, instance=vm_name)
        self.instances.delete(request=req)

    def _create(self, vm_name: str, zone: str, params: dict):
        # Defaults
        machine_type = params.get("machine_type", "e2-small")
        image_family = params.get("image_family", "debian-11")
        network = params.get("network", "global/networks/default")

        # Normalizar machine_type
        if not machine_type.startswith("zones/"):
            machine_type = f"zones/{zone}/machineTypes/{machine_type}"

        # Obtener imagen base
        image = self.images.get_from_family(project="debian-cloud", family=image_family)

        config = compute_v1.Instance(
            name=vm_name,
            machine_type=machine_type,
            disks=[
                compute_v1.AttachedDisk(
                    boot=True,
                    auto_delete=True,
                    initialize_params=compute_v1.AttachedDiskInitializeParams(
                        source_image=image.self_link
                    ),
                )
            ],
            network_interfaces=[
                compute_v1.NetworkInterface(
                    network=network,
                    access_configs=[compute_v1.AccessConfig(name="External NAT")],
                )
            ],
            service_accounts=[
                compute_v1.ServiceAccount(
                    email="default",
                    scopes=[
                        "https://www.googleapis.com/auth/devstorage.read_write",
                        "https://www.googleapis.com/auth/logging.write",
                    ],
                )
            ],
        )
        req = compute_v1.InsertInstanceRequest(project=self.project, zone=zone, instance_resource=config)
        self.instances.insert(request=req)
