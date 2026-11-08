from typing import Callable, Optional
import flet as ft
from database.db_manager import DBManager
from models.movimiento import Movimiento
from components.movement_item import crear_item_movimiento


class HistorialView(ft.Column):
    """Vista con listado completo de transacciones, buscador en tiempo real y filtros por tipo y período."""

    def __init__(
        self,
        db: DBManager,
        on_edit: Callable[[Movimiento], None],
        on_delete: Callable[[Movimiento], None],
        on_cambiar_periodo: Optional[Callable[[Optional[int]], None]] = None,
    ):
        super().__init__(spacing=14, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_cambiar_periodo = on_cambiar_periodo
        self.periodo_dias: Optional[int] = None

        self.campo_busqueda = ft.TextField(
            hint_text="Buscar por descripción o categoría...",
            prefix_icon=ft.Icons.SEARCH,
            border=ft.OutlineInputBorder(border_radius=12),
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

        self.filtro_periodo = ft.SegmentedButton(
            selected=["todos"],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value="todos", label=ft.Text("Todo")),
                ft.Segment(value="15", label=ft.Text("15 días")),
                ft.Segment(value="30", label=ft.Text("30 días")),
            ],
            on_change=self._al_cambiar_periodo_segmento,
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
            ft.Text("Filtrar por tipo:", size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
            self.filtro_tipo,
            ft.Text("Filtrar por período:", size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
            self.filtro_periodo,
            self.texto_contador,
            self.columna_movimientos,
        ]
        self.actualizar_datos()

    def _al_cambiar_periodo_segmento(self, e):
        """Manejador al cambiar la selección en el SegmentedButton de período."""
        val = self.filtro_periodo.selected[0] if self.filtro_periodo.selected else "todos"
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
            self.filtro_periodo.selected = ["15"]
        elif dias == 30:
            self.filtro_periodo.selected = ["30"]
        else:
            self.filtro_periodo.selected = ["todos"]

    def actualizar_datos(self, dias: Optional[int] = None):
        """Filtra y renderiza los movimientos según la búsqueda, el tipo y el período seleccionado."""
        if dias is not None:
            self.establecer_periodo(dias)
        else:
            dias = self.periodo_dias

        busqueda = self.campo_busqueda.value or ""
        tipo_sel = self.filtro_tipo.selected[0] if self.filtro_tipo.selected else "Todos"

        movimientos = self.db.obtener_todos(
            busqueda=busqueda if busqueda.strip() else None,
            tipo=tipo_sel,
            dias=dias,
        )

        total = len(movimientos)
        periodo_sufijo = f" en los últimos {dias} días" if dias else ""
        self.texto_contador.value = f"Mostrando {total} {'movimiento' if total == 1 else 'movimientos'}{periodo_sufijo}"

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
                                "Prueba con otro término de búsqueda o cambia el filtro de período.",
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
