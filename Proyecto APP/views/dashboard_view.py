from typing import Callable, Optional
import flet as ft
from database.db_manager import DBManager
from models.movimiento import Movimiento
from components.cards import crear_tarjeta_balance, crear_tarjetas_resumen
from components.movement_item import crear_item_movimiento


class DashboardView(ft.Column):
    """Vista principal con el balance global ajustado por período, tarjetas de flujo y últimos movimientos."""

    def __init__(
        self,
        db: DBManager,
        on_edit: Callable[[Movimiento], None],
        on_delete: Callable[[Movimiento], None],
        on_ver_todos: Callable[[], None],
        on_cambiar_periodo: Optional[Callable[[Optional[int]], None]] = None,
    ):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_ver_todos = on_ver_todos
        self.on_cambiar_periodo = on_cambiar_periodo
        self.periodo_dias: Optional[int] = None

        self.columna_recientes = ft.Column(spacing=8)
        self.contenedor_balance = ft.Container()
        self.contenedor_resumen = ft.Container()

        self.selector_periodo = ft.SegmentedButton(
            selected=["todos"],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value="todos", label=ft.Text("Todos")),
                ft.Segment(value="15", label=ft.Text("15 días")),
                ft.Segment(value="30", label=ft.Text("30 días")),
            ],
            on_change=self._al_cambiar_segmento,
        )

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Mis Finanzas", size=24, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.TEAL_700),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.selector_periodo],
            ),
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

    def _al_cambiar_segmento(self, e):
        """Manejador del cambio de período en el SegmentedButton."""
        val = self.selector_periodo.selected[0] if self.selector_periodo.selected else "todos"
        if val == "15":
            self.periodo_dias = 15
        elif val == "30":
            self.periodo_dias = 30
        else:
            self.periodo_dias = None

        if self.on_cambiar_periodo:
            self.on_cambiar_periodo(self.periodo_dias)
        else:
            self.actualizar_datos(self.periodo_dias)

    def establecer_periodo(self, dias: Optional[int]):
        """Sincroniza el selector visual con un período específico."""
        self.periodo_dias = dias
        if dias == 15:
            self.selector_periodo.selected = ["15"]
        elif dias == 30:
            self.selector_periodo.selected = ["30"]
        else:
            self.selector_periodo.selected = ["todos"]

    def actualizar_datos(self, dias: Optional[int] = None):
        """Refresca la información del balance y la lista de movimientos recientes según el período."""
        if dias is not None:
            self.establecer_periodo(dias)
        else:
            dias = self.periodo_dias

        resumen = self.db.obtener_resumen(dias=dias)

        if dias == 15:
            etiqueta = "Balance (Últimos 15 días)"
        elif dias == 30:
            etiqueta = "Balance (Últimos 30 días)"
        else:
            etiqueta = "Balance actual (Histórico)"

        self.contenedor_balance.content = crear_tarjeta_balance(resumen["balance"], etiqueta=etiqueta)
        self.contenedor_resumen.content = crear_tarjetas_resumen(resumen["ingresos"], resumen["gastos"])

        movimientos_recientes = self.db.obtener_todos(limite=5, dias=dias)

        if movimientos_recientes:
            self.columna_recientes.controls = [
                crear_item_movimiento(m, self.on_edit, self.on_delete)
                for m in movimientos_recientes
            ]
        else:
            periodo_txt = f"en los últimos {dias} días" if dias else "registrados"
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
                                f"No hay movimientos {periodo_txt}",
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Presiona el botón '+' para registrar un gasto o ingreso.",
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
