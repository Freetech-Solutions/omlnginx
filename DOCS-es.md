Descripción general
===================

Omnidialer (OMD) es un software de marcador diseñado como un componente FLOSS para Omnileads (OML) que puede usarse como una alternativa al marcador Wombat.

Está implementado en Python y utiliza componentes como Docker, docker-compose, Postgres, Redis y Gearman.

El uso de Gearman permite escalar horizontalmente el sistema de manera sencilla agregando trabajadores de Gearman dedicados a los recursos que más consumen tiempo y memoria.

El sistema está diseñado para ejecutarse en cualquier sistema GNU/Linux que soporte bash, docker y docker-compose.

Puede ejecutarse en el mismo host en el que se ejecuta OML o en un host externo configurando las variables de entorno presentes en el archivo env.
Las variables de entorno relevantes en este caso son: *REDIS_OML_SERVER*, *REDIS_OML_PORT*, *ASTERISK_APP*, *ASTERISK_USER*, *ASTERISK_PASS*, *ASTERISK_HOST*, *ASTERISK_PORT*, *DIALER_ACD_HOST*, *POSTGRES_OML_PASSWORD*, *POSTGRES_OML_SERVER* y *POSTGRES_OML_PORT* .

Uso:

La forma más sencilla de utilizar el sistema es ejecutar el script start-dedicated.bash

Asegúrate de tener Docker y Docker-Compose instalados y de que tienes la shell bash disponible.

Luego, realiza lo siguiente:

$ cp env .env

Si estás en un host diferente al de OML:

$ docker network create omnileads_omnileads

En cualquier caso, ejecuta:

$ bash start-dedicated.bash

Un servidor Flask estará corriendo en 0.0.0.0:1440 con un job server de Gearman y los workers de Gearman necesarios.

Después de esto, puedes acceder a los diferentes endpoints para interactuar con el sistema. Consulta la carpeta 'test/curls' para ver algunos ejemplos.


Explicación de Endpoints
=======================

Crear campaña
---------------

### Endpoint: `[POST] /create-campaign/<id_campaign>`

#### Descripción
El endpoint create-campaign crea una campaña dentro de OMD importando los datos relacionados desde una campaña de OML.

El valor <id_campaign> corresponde al id de una campaña de OML, y será también el id de la nueva campaña en OMD.

Los otros valores importados desde OML son los campos estado, nombre, fecha_inicio, fecha_fin, control_de_duplicados y prioridad de la tabla ominicontacto_app_campana, que se copiarán a la tabla _campaign_. Adicionalmente, se importarán las entradas relacionadas con reglas de incidencia y contactos en las tablas _incidence_rules_, _incidence_rules_disposition_, _contact_in_campaign_ y _contact_, respectivamente.

El parámetro JSON _contact_strategy_ también se agrega como un campo de la tabla campaign. Esto se usará en el futuro para personalizar la forma en que el marcador llama más de una vez a un contacto en la campaña actual.

#### Método
- **Método HTTP:** `POST`

### Cuerpo de la solicitud
```json
{
  "contact-strategy": "[<id_strategy1>, <id_strategy2>, ... ,<id_strategy_n>]"
}
```


Editar campaña
---------------

### Endpoint: `[POST] /edit-campaign/<id_campaign>`

#### Descripción
El endpoint edit-campaign edita una campaña en OMD modificando los datos relacionados con los valores actuales de la campaña con el mismo id en OML.

El valor <id_campaign> corresponde al id de una campaña en OML y OMD.

Las tablas _campaign_, _incidence_rules_ e _incidence_rules_disposition_ podrían modificarse de acuerdo con los datos existentes en OML.

#### Método
- **Método HTTP:** `POST`

### Cuerpo de la petición
```json
{
  "contact-strategy": "[<id_strategy1>, <id_strategy2>, ... ,<id_strategy_n>]"
}
```


Iniciar campaña
---------------

### Endpoint: `[POST] /start-campaign/<id_campaign>`

#### Descripción

El endpoint start-campaign inicia el proceso principal de la campaña, estableciendo el campo 'dialer_status' en estado ACTIVO e iniciará un bucle que llamará a los contactos de la base de datos OMD de acuerdo con la configuración de la campaña y los agentes disponibles en OML.

El valor <id_campaign> corresponde al id de una campaña en OML y OMD.

#### Método
- **Método HTTP:** `POST`



Pausar campaña
---------------

### Endpoint: `[POST] /pause-campaign/<id_campaign>`

#### Descripción

El endpoint pause-campaign pausa el proceso de la campaña en OMD modificando el campo dialer_status de la entrada de la campaña al valor PAUSED.

El valor <id_campaign> corresponde al id de una campaña en OML y OMD.

#### Método
- **Método HTTP:** `POST`


Reanudar campaña
---------------

### Endpoint: `[POST] /resume-campaign/<id_campaign>`

#### Descripción

El endpoint resume-campaign reanuda el proceso de la campaña en OMD modificando el campo dialer_status de la entrada de la campaña al valor RESUMED y reiniciará el proceso de la campaña.

El valor <id_campaign> corresponde al id de una campaña en OML y OMD.

#### Método
- **Método HTTP:** `POST`

Detener (finalizar) campaña
---------------
### Endpoint: `[POST] /post-campaign/<id_campaign>`

#### Descripción

El endpoint post-campaign detiene una campaña en ejecución estableciendo primero el campo dialer_status en estado FINALIZED y después copiará todas las entradas relacionadas con la campaña en las tablas históricas. Las entradas se mueven a las tablas campaign_historic, contact_in_campaign_historic, incidence_rules_historic e incidence_rules_disposition_historic. Finalmente, la campaña original y las tablas relacionadas se eliminan de la base de datos como si se estuviera usando el endpoint delete-campaign.

Eliminar campaign
---------------

### Endpoint: `[POST] /delete-campaign/<id_campaign>`

#### Description
The delete-campaign endpoint first pauses a campaign and then remove it completely from the DB; the tables _campaign_, _incidence_rules_, _incidence_rules_disposition_ and _contact_in_campaign_ can be affected with this endpoint.

The value <id_campaign> correspond to the id of a campaign in OML and OMD.

#### Method
- **HTTP Method:** `POST`


Add disposition for contact
---------------------------

### Endpoint: `[POST] /add-incidence-rule-disposition/<id_campaign>`

#### Description
The add-incidence-rule-disposition endpoint is meant to be used by OML to signal that a disposition option was added to a contact in the campaign and that an incidence rule should be analyzed in this case. OMD will add the information about the disposition to the contact history in the campaign and if the linked incidence rule matches it will schedule a call for the contact.

The value <id_campaign> correspond to the id of a campaign in OML and OMD.

The tables _campaign_, _incidence_rules_ and _incidence_rules_disposition_ could be modified according to the existent data in OML.

#### Method
- **HTTP Method:** `POST`

### Request Body
```json
{
        "id_contact": <id_contact>,
        "disposition_option": <id_disposition_option>
}
```


Arquitecture
============

The arquitecture of the system is shown in the following diagram:

![alt text](images/omnidialer-arquitecture.svg "Omnidialer arquitecture")

The system serves the endpoints with a Flask server that, in turn redirects the tasks to the running Gearman workers.

There is also a websocket server that will receive the ARI events linked to the calls and will redirect the task to a Gearman worker.

The data of the system is persisted in a Postgres instance and some data are replicated on a Redis instance.

The data saved in Redis is related with contact history in a campaign and reports of the campaign.

The system also publish in PUBSUB channels information about reports and status of the campaigns.

Horizontal scalability
======================

The system is designed with the ability to horizontal scale by simply creating more Gearman job servers and workers.

To add more gearman job servers you will need to modify the environment variable GEARMAN_JOB_SERVERS and add a new job server in the following way:

$ docker run --rm -itd -p 4731:4731 --network=omnileads_omnileads --name=gearman_job_server_2 artefactual/gearmand:1.1.18-alpine

You can also add more workers in the same host by using the following way:

$ bash add-worker-single-job.bash <name_of_the_gearman_job_to_serve> <new_container_name>

for example:

$ bash add-worker-single-job.bash process-contact process-contact-5

If you are in other host you can run the docker-compose file _docker-compose-single-worker.yml_ after setting the relevant values in the .env file and after that you can more workers as needed

Tests
=====

For run the unit tests just do:

$ bash rebuild-testing-truncated.bash

$ bash run-tests.bash

Logging
=======

If you want to see debug logs on every single worker you need to change the environment variable PYTHON_LOGLEVEL from _warning_ to _debug_
