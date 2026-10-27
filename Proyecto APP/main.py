"""
Control de Gastos - Finanzas Personales
Aplicación multiplataforma modular construida con Flet y SQLite.
Permite registrar ingresos y gastos, persistencia local segura,
análisis estadístico por categoría y exploración de historial con filtros.
"""

import flet as ft
from database.db_manager import DBManager
from models.movimiento import Movimiento
from components.dialogs import mostrar_formulario_movimiento, mostrar_dialogo_confirmacion
from views.dashboard_view import DashboardView
from views.historial_view import HistorialView
from views.estadisticas_view import EstadisticasView


def main(page: ft.Page):
    # Configuración de ventana y tema Material 3
    page.title = "Control de Gastos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.padding = ft.Padding.symmetric(horizontal=16, vertical=8)
    page.window.width = 480
    page.window.height = 840
    page.window.resizable = True

    # Inicialización de la base de datos local SQLite
    db = DBManager()

    def avisar(mensaje: str, color=ft.Colors.TEAL_700):
        """Muestra una notificación emergente SnackBar."""
        page.show_dialog(ft.SnackBar(ft.Text(mensaje), bgcolor=color))

    def refrescar_todo():
        """Sincroniza los datos en todas las vistas montadas."""
        vista_dashboard.actualizar_datos()
        vista_historial.actualizar_datos()
        vista_estadisticas.actualizar_datos()
        page.update()

    def on_guardado(mensaje: str):
        """Callback al agregar o editar un movimiento con éxito."""
        refrescar_todo()
        avisar(mensaje)

    def on_editar(mov: Movimiento):
        """Abre el diálogo modal precargado para editar un movimiento."""
        mostrar_formulario_movimiento(page, db, mov_existente=mov, al_guardar=on_guardado)

    def on_eliminar(mov: Movimiento):
        """Solicita confirmación antes de borrar definitivamente un registro."""
        def ejecutar_eliminacion():
            db.eliminar(mov.id)
            refrescar_todo()
            avisar("Movimiento eliminado correctamente", color=ft.Colors.RED_700)

        mostrar_dialogo_confirmacion(
            page=page,
            titulo="Eliminar movimiento",
            mensaje=f"¿Estás seguro de que deseas eliminar '{mov.descripcion or mov.categoria}' (${mov.monto:,.2f})?",
            al_confirmar=ejecutar_eliminacion,
        )

    def ir_a_historial():
        """Navega programáticamente a la vista de historial."""
        nav_bar.selected_index = 1
        cambiar_vista(1)

    # Creación de vistas desacopladas
    vista_dashboard = DashboardView(
        db=db,
        on_edit=on_editar,
        on_delete=on_eliminar,
        on_ver_todos=ir_a_historial,
    )
    vista_historial = HistorialView(
        db=db,
        on_edit=on_editar,
        on_delete=on_eliminar,
    )
    vista_estadisticas = EstadisticasView(db=db)

    vistas = [vista_dashboard, vista_historial, vista_estadisticas]
    contenedor_principal = ft.Container(content=vista_dashboard, expand=True)

    def cambiar_vista(indice: int):
        """Conmuta la vista visible en el contenedor principal."""
        contenedor_principal.content = vistas[indice]
        vistas[indice].actualizar_datos()
        page.update()

    # Barra de navegación inferior (Material 3 NavigationBar)
    nav_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Inicio",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                selected_icon=ft.Icons.RECEIPT_LONG,
                label="Historial",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED,
                selected_icon=ft.Icons.INSIGHTS,
                label="Estadísticas",
            ),
        ],
        on_change=lambda e: cambiar_vista(e.control.selected_index),
    )

    # Conmutador de modo claro / oscuro
    def alternar_tema(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            btn_tema.icon = ft.Icons.LIGHT_MODE_OUTLINED
            btn_tema.tooltip = "Cambiar a modo claro"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            btn_tema.icon = ft.Icons.DARK_MODE_OUTLINED
            btn_tema.tooltip = "Cambiar a modo oscuro"
        page.update()

    btn_tema = ft.IconButton(
        icon=ft.Icons.DARK_MODE_OUTLINED,
        tooltip="Cambiar a modo oscuro",
        on_click=alternar_tema,
    )

    # Barra superior de la aplicación
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.WALLET, color=ft.Colors.TEAL_700),
        title=ft.Text("Control de Gastos", weight=ft.FontWeight.BOLD, size=18),
        actions=[btn_tema],
        bgcolor=ft.Colors.SURFACE,
    )

    # Botón Flotante para nuevo movimiento
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.TEAL_700,
        foreground_color=ft.Colors.WHITE,
        tooltip="Nuevo movimiento",
        on_click=lambda e: mostrar_formulario_movimiento(page, db, al_guardar=on_guardado),
    )

    page.navigation_bar = nav_bar
    page.add(contenedor_principal)


if __name__ == "__main__":
    ft.run(main)
