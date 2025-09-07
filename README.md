# Control de VMs con Cloud Functions (OOP, Python 3.11)

Esta Cloud Function (Gen2) procesa mensajes de **Pub/Sub** para gestionar instancias de Compute Engine.  
Permite **iniciar**, **detener**, **crear** y **borrar** VMs.  

Esta basada en la Cloud function del [repositorio de ArnauSB](https://github.com/ArnauSB/gcp-examples/tree/main/cloud-functions) del módulo de GCP para el MCDS.

Diseñada con una arquitectura **orientada a objetos** y **modular**:

- `main.py`: punto de entrada `start_stop_vm` compatible con Pub/Sub.
- `utils/clients.py`: inicializa clientes y credenciales.
- `utils/controller.py`: clase `VMController` con métodos para `start`, `stop`, `create` y `delete`.

---

## Formato de los mensajes Pub/Sub

### Caso general
El `data` del mensaje debe contener (en Base64) un string con el formato:

```
<vm_name>:<zone>:<action>
```

Ejemplo:
patriciomallea-vm1:europe-southwest1-b:start

### Caso especial: `create` con parámetros
Se pueden pasar parámetros adicionales en **attributes** del mensaje Pub/Sub:

Ejemplo de publicación con `gcloud`:

gcloud pubsub topics publish patriciomallea-control-vm \
  --message="patriciomallea-vm2:europe-southwest1-b:create" \
  --attribute="machine_type=e2-medium,image_family=debian-12,network=global/networks/default"

### Parámetros soportados en `attributes` para `create`
- `machine_type` (ej: `e2-small`, `e2-medium`, o `zones/.../machineTypes/...`)
- `image_family` (ej: `debian-11`, `debian-12`)
- `network` (ej: `global/networks/default`)

Si no se especifican, se usan los defaults:
- `machine_type = e2-small`
- `image_family = debian-11`
- `network = global/networks/default`

---

## Requisitos

- Runtime: **Python 3.11**
- Entry point: **start_stop_vm**
- Dependencias: ver `requirements.txt`

### Roles mínimos de la Service Account
- `roles/compute.instanceAdmin.v1`
- `roles/logging.logWriter`
- (Opcional según trigger) `roles/pubsub.subscriber`, `roles/pubsub.publisher`

---

## Ejemplos de uso

- **Start**  
  `patriciomallea-vm1:europe-southwest1-b:start`

- **Stop**  
  `patriciomallea-vm1:europe-southwest1-b:stop`

- **Delete**  
  `patriciomallea-vm1:europe-southwest1-b:delete`

- **Create (con parámetros extra)**  
  Mensaje:  
  `patriciomallea-vm2:europe-southwest1-b:create`  
  Atributos:  
  `machine_type=e2-medium,image_family=debian-12,network=global/networks/default`

---

## Arquitectura y diseño

- **Orientado a objetos**: encapsula la lógica de Compute Engine en `VMController`.
- **Modularidad**: separación de responsabilidades (clientes vs. control).
- **Extensible**: fácil de añadir nuevas acciones (`resize`, `snapshot`, etc).
- **Robusto**: manejo de excepciones (`NotFound`, `PermissionDenied`, errores genéricos).
