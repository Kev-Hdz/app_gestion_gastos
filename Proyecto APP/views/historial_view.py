from typing import Callable
import flet as ft
from database.db_manager import DBManager
from models.movimiento import Movimiento
from components.movement_item import crear_item_movimiento


class HistorialView(ft.Column):
    """Vista con listado completo de transacciones, buscador en tiempo real y filtros por tipo."""

    def __init__(
        self,
        db: DBManager,
        on_edit: Callable[[Movimiento], None],
        on_delete: Callable[[Movimiento], None],
    ):
        super().__init__(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.campo_busqueda = ft.TextField(
            hint_text="Buscar por descripción o categoría...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            dense=True,
            on_change=lambda e: self.actualizar_datos(),
        )

        self.filtro_tipo = ft.SegmentedButton(
            selected=["Todos"],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value="Todos", label=ft.Text("Todos")),
                ft.Segment(value="Gasto", label=ft.Text("Gastos")),
                ft.Segment(value="Ingreso", label=ft.Text("Ingresos")),
            ],
            on_change=lambda e: self.actualizar_datos(),
        )

        self.texto_contador = ft.Text(
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
            weight=ft.FontWeight.W_500,
        )
        self.columna_movimientos = ft.Column(spacing=8)

        self.controls = [
            ft.Text("Historial de Movimientos", size=24, weight=ft.FontWeight.BOLD),
            self.campo_busqueda,
            self.filtro_tipo,
            self.texto_contador,
            self.columna_movimientos,
        ]
        self.actualizar_datos()

    def actualizar_datos(self):
        """Filtra y renderiza los movimientos según la búsqueda y el tipo seleccionado."""
        busqueda = self.campo_busqueda.value or ""
        tipo_sel = self.filtro_tipo.selected[0] if self.filtro_tipo.selected else "Todos"

        movimientos = self.db.obtener_todos(
            busqueda=busqueda if busqueda.strip() else None,
            tipo=tipo_sel,
        )

        total = len(movimientos)
        self.texto_contador.value = f"Mostrando {total} {'movimiento' if total == 1 else 'movimientos'}"

        if movimientos:
            self.columna_movimientos.controls = [
                crear_item_movimiento(m, self.on_edit, self.on_delete)
                for m in movimientos
            ]
        else:
            self.columna_movimientos.controls = [
                ft.Container(
                    padding=32,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=ft.Colors.OUTLINE),
                            ft.Text(
                                "No se encontraron movimientos",
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Prueba con otro término de búsqueda o cambia el filtro.",
                                size=12,
                                color=ft.Colors.OUTLINE,
                            ),
                        ],
                    ),
                )
            ]

        try:
            self.update()
        except RuntimeError:
            pass
