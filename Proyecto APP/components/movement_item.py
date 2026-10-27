import flet as ft
from models.movimiento import Movimiento, ICONOS, moneda


def crear_item_movimiento(mov: Movimiento, on_edit, on_delete) -> ft.Container:
    """Genera una tarjeta estilizada para visualizar un movimiento individual con acciones."""
    es_gasto = mov.tipo == "Gasto"
    color_monto = ft.Colors.RED_700 if es_gasto else ft.Colors.GREEN_700
    color_fondo_icono = ft.Colors.RED_50 if es_gasto else ft.Colors.GREEN_50
    signo = "-" if es_gasto else "+"
    icono = ICONOS.get(mov.categoria, ft.Icons.ATTACH_MONEY)
    descripcion = mov.descripcion.strip() if mov.descripcion and mov.descripcion.strip() else mov.categoria
    fecha_formateada = mov.fecha.strftime("%d/%m/%Y")

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=14,
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Bloque izquierdo: Ícono + Textos
                ft.Row(
                    expand=True,
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=9,
                            border_radius=10,
                            bgcolor=color_fondo_icono,
                            content=ft.Icon(icono, color=color_monto, size=22),
                        ),
                        ft.Column(
                            spacing=1,
                            expand=True,
                            controls=[
                                ft.Text(
                                    descripcion,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"{mov.categoria} · {fecha_formateada}",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                        ),
                    ],
                ),
                # Bloque derecho: Monto + Botones de Acción
                ft.Row(
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"{signo}{moneda(mov.monto)}",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=color_monto,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_size=18,
                            tooltip="Editar",
                            icon_color=ft.Colors.TEAL_700,
                            on_click=lambda e, m=mov: on_edit(m),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=18,
                            tooltip="Eliminar",
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, m=mov: on_delete(m),
                        ),
                    ],
                ),
            ],
        ),
    )
