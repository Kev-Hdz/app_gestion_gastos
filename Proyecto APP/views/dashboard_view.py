from typing import Callable
import flet as ft
from database.db_manager import DBManager
from models.movimiento import Movimiento
from components.cards import crear_tarjeta_balance, crear_tarjetas_resumen
from components.movement_item import crear_item_movimiento


class DashboardView(ft.Column):
    """Vista principal con el balance global, tarjetas de flujo y últimos movimientos."""

    def __init__(
        self,
        db: DBManager,
        on_edit: Callable[[Movimiento], None],
        on_delete: Callable[[Movimiento], None],
        on_ver_todos: Callable[[], None],
    ):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_ver_todos = on_ver_todos
        self.columna_recientes = ft.Column(spacing=8)
        self.contenedor_balance = ft.Container()
        self.contenedor_resumen = ft.Container()

        self.controls = [
            ft.Text("Mis Finanzas", size=24, weight=ft.FontWeight.BOLD),
            self.contenedor_balance,
            self.contenedor_resumen,
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Movimientos recientes", size=18, weight=ft.FontWeight.W_600),
                    ft.TextButton(
                        "Ver todos",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=lambda e: self.on_ver_todos(),
                    ),
                ],
            ),
            self.columna_recientes,
        ]
        self.actualizar_datos()

    def actualizar_datos(self):
        """Refresca la información del balance y la lista de movimientos recientes."""
        resumen = self.db.obtener_resumen()
        self.contenedor_balance.content = crear_tarjeta_balance(resumen["balance"])
        self.contenedor_resumen.content = crear_tarjetas_resumen(resumen["ingresos"], resumen["gastos"])

        movimientos_recientes = self.db.obtener_todos(limite=5)

        if movimientos_recientes:
            self.columna_recientes.controls = [
                crear_item_movimiento(m, self.on_edit, self.on_delete)
                for m in movimientos_recientes
            ]
        else:
            self.columna_recientes.controls = [
                ft.Container(
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=40, color=ft.Colors.OUTLINE),
                            ft.Text(
                                "No hay movimientos registrados",
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Presiona el botón '+' para registrar tu primer gasto o ingreso.",
                                size=12,
                                color=ft.Colors.OUTLINE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            ]

        try:
            self.update()
        except RuntimeError:
            pass
