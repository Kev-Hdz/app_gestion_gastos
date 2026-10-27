Para entender un proyecto con arquitectura MVC (Modelo-Vista-Controlador) o basado en componentes de manera lógica y sin abrumarte, lo ideal es ir de la base (los datos y el arranque) hacia la superficie (la interfaz completa).

Con la estructura que mostraste anteriormente, esta es la secuencia recomendada para leer y entender el código:

**1. El punto de entrada (`main.py`)**
Revisa este archivo primero. Es donde arranca la aplicación de Flet.
Aquí entenderás la configuración inicial de la ventana, el tema de colores y cómo se maneja la navegación (el enrutamiento) entre las diferentes pantallas de la app.

**2. Los Modelos (`models/`)**
Abre archivos como `movimiento.py`. Antes de ver cómo se dibuja algo en pantalla, necesitas saber qué información maneja el sistema. Aquí verás las clases que definen los objetos (por ejemplo, si un movimiento tiene `id`, `monto`, `fecha`, etc.).

**3. La Base de Datos (`database/`)**
Revisa `db_manager.py`. Una vez que sabes qué datos existen (Modelos), aquí verás cómo se guardan, leen, actualizan o eliminan físicamente en la base de datos (SQLite). Esto te dará el contexto de la lógica de negocio y las operaciones CRUD.

**4. Los Componentes Reutilizables (`components/`)**
Archivos como `movement_item.py`, `cards.py` o `dialogs.py`. Son las "piezas de Lego" de tu interfaz. Es mejor entender cómo funciona un botón, una tarjeta o una fila de texto individualmente antes de ver una pantalla llena de ellos.

**5. Las Vistas o Pantallas (`views/`)**
Finalmente, revisa los archivos como `dashboard_view.py`, `estadisticas_view.py` o `historial_view.py`. Aquí es donde todo cobra sentido: verás cómo la Vista toma los datos de la Base de Datos, los envuelve en los Modelos, y los dibuja usando los Componentes que ya leíste.

Con lo que mostraste en las capturas anteriores es suficiente para definir esta ruta, pero si dentro de estas carpetas tienes subestructuras más complejas y te surge alguna duda con un flujo específico, puedes enviar una nueva captura para analizarla.
