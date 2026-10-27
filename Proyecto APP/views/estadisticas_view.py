import flet as ft
from database.db_manager import DBManager
from models.movimiento import ICONOS, moneda


class EstadisticasView(ft.Column):
    """Vista analítica con distribución porcentual y visual de gastos por categoría."""

    def __init__(self, db: DBManager):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        self.db = db
        self.contenedor_tarjeta_total = ft.Container()
        self.columna_categorias = ft.Column(spacing=14)

        self.controls = [
            ft.Text("Estadísticas de Gastos", size=24, weight=ft.FontWeight.BOLD),
            self.contenedor_tarjeta_total,
            ft.Text("Desglose por Categoría", size=18, weight=ft.FontWeight.W_600),
            self.columna_categorias,
        ]
        self.actualizar_datos()

    def actualizar_datos(self):
        """Calcula y refresca las métricas de gasto por categoría."""
        resumen = self.db.obtener_resumen()
        total_gastos = resumen["gastos"]
        categorias = self.db.obtener_gastos_por_categoria()

        # Tarjeta resumen de gastos
        self.contenedor_tarjeta_total.content = ft.Container(
            padding=18,
            border_radius=14,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("Gasto Total Acumulado", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(moneda(total_gastos), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=12,
                        bgcolor=ft.Colors.RED_50,
                        content=ft.Icon(ft.Icons.PIE_CHART_OUTLINE, color=ft.Colors.RED_700, size=24),
                    ),
                ],
            ),
        )

        if categorias and total_gastos > 0:
            filas = []
            for item in categorias:
                cat = item["categoria"]
                total = item["total"]
                pct = item["porcentaje"]
                cant = item["cantidad"]
                icono = ICONOS.get(cat, ft.Icons.MORE_HORIZ)

                fila_cat = ft.Container(
                    padding=14,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                padding=6,
                                                border_radius=8,
                                                bgcolor=ft.Colors.TEAL_50,
                                                content=ft.Icon(icono, color=ft.Colors.TEAL_700, size=18),
                                            ),
                                            ft.Column(
                                                spacing=0,
                                                controls=[
                                                    ft.Text(cat, weight=ft.FontWeight.W_600, size=14),
                                                    ft.Text(f"{cant} {'gasto' if cant == 1 else 'gastos'}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        spacing=0,
                                        controls=[
                                            ft.Text(moneda(total), weight=ft.FontWeight.BOLD, size=14),
                                            ft.Text(f"{pct:.1f}%", size=11, color=ft.Colors.TEAL_700, weight=ft.FontWeight.W_600),
                                        ],
                                    ),
                                ],
                            ),
                            ft.ProgressBar(
                                value=pct / 100.0,
                                color=ft.Colors.TEAL_700,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            ),
                        ],
                    ),
                )
                filas.append(fila_cat)

            self.columna_categorias.controls = filas
        else:
            self.columna_categorias.controls = [
                ft.Container(
                    padding=32,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INSIGHTS_OUTLINED, size=40, color=ft.Colors.OUTLINE),
                            ft.Text(
                                "Sin datos de gastos",
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Registra movimientos de tipo 'Gasto' para visualizar el análisis.",
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
