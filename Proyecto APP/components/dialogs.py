from datetime import datetime
from typing import Optional, Callable
import flet as ft
from models.movimiento import Movimiento, CATEGORIAS_GASTO, CATEGORIAS_INGRESO
from database.db_manager import DBManager


def mostrar_formulario_movimiento(
    page: ft.Page,
    db: DBManager,
    mov_existente: Optional[Movimiento] = None,
    al_guardar: Optional[Callable[[str], None]] = None,
):
    """Muestra un diálogo modal para registrar un nuevo movimiento o editar uno existente."""
    es_edicion = mov_existente is not None
    titulo_modal = "Editar Movimiento" if es_edicion else "Nuevo Movimiento"

    tipo_inicial = mov_existente.tipo if es_edicion else "Gasto"
    categoria_inicial = mov_existente.categoria if es_edicion else CATEGORIAS_GASTO[0]
    monto_inicial = f"{mov_existente.monto:g}" if es_edicion else ""
    desc_inicial = mov_existente.descripcion if es_edicion else ""
    fecha_seleccionada = [mov_existente.fecha if es_edicion else datetime.now()]

    # Controles del formulario
    segmento_tipo = ft.SegmentedButton(
        selected=[tipo_inicial],
        allow_multiple_selection=False,
        segments=[
            ft.Segment(value="Gasto", label=ft.Text("Gasto"), icon=ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE)),
            ft.Segment(value="Ingreso", label=ft.Text("Ingreso"), icon=ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE)),
        ],
    )

    campo_monto = ft.TextField(
        label="Monto",
        value=monto_inicial,
        prefix="$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        autofocus=True,
    )

    categorias_disponibles = CATEGORIAS_GASTO if tipo_inicial == "Gasto" else CATEGORIAS_INGRESO
    campo_categoria = ft.Dropdown(
        label="Categoría",
        border_radius=10,
        options=[ft.DropdownOption(key=c, text=c) for c in categorias_disponibles],
        value=categoria_inicial if categoria_inicial in categorias_disponibles else categorias_disponibles[0],
    )

    campo_desc = ft.TextField(
        label="Descripción (opcional)",
        value=desc_inicial,
        border_radius=10,
    )

    btn_fecha = ft.OutlinedButton(
        content=f"Fecha: {fecha_seleccionada[0].strftime('%d/%m/%Y')}",
        icon=ft.Icons.CALENDAR_MONTH,
    )

    # DatePicker
    def al_cambiar_fecha(e):
        if picker_fecha.value:
            val = picker_fecha.value
            if isinstance(val, str):
                fecha_seleccionada[0] = datetime.fromisoformat(val)
            else:
                fecha_seleccionada[0] = datetime(val.year, val.month, val.day)
            btn_fecha.content = f"Fecha: {fecha_seleccionada[0].strftime('%d/%m/%Y')}"
            try:
                btn_fecha.update()
            except RuntimeError:
                pass

    picker_fecha = ft.DatePicker(
        value=fecha_seleccionada[0],
        on_change=al_cambiar_fecha,
    )

    def abrir_calendario(e):
        page.show_dialog(picker_fecha)

    btn_fecha.on_click = abrir_calendario

    # Cambio reactivo de categorías
    def al_cambiar_tipo(e):
        seleccion = segmento_tipo.selected[0]
        nuevas_cats = CATEGORIAS_GASTO if seleccion == "Gasto" else CATEGORIAS_INGRESO
        campo_categoria.options = [ft.DropdownOption(key=c, text=c) for c in nuevas_cats]
        campo_categoria.value = nuevas_cats[0]
        try:
            campo_categoria.update()
        except RuntimeError:
            pass

    segmento_tipo.on_change = al_cambiar_tipo

    # Lógica de guardado
    def guardar(e):
        try:
            monto = float(campo_monto.value.replace(",", "").strip())
            if monto <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            campo_monto.error = "Ingresa un monto válido mayor a 0"
            try:
                campo_monto.update()
            except RuntimeError:
                pass
            return

        campo_monto.error = None

        if es_edicion:
            mov_existente.tipo = segmento_tipo.selected[0]
            mov_existente.categoria = campo_categoria.value or categorias_disponibles[0]
            mov_existente.descripcion = (campo_desc.value or "").strip()
            mov_existente.monto = monto
            mov_existente.fecha = fecha_seleccionada[0]
            db.actualizar(mov_existente)
            mensaje = "Movimiento actualizado con éxito"
        else:
            nuevo_mov = Movimiento(
                tipo=segmento_tipo.selected[0],
                categoria=campo_categoria.value or categorias_disponibles[0],
                descripcion=(campo_desc.value or "").strip(),
                monto=monto,
                fecha=fecha_seleccionada[0],
            )
            db.agregar(nuevo_mov)
            mensaje = f"{nuevo_mov.tipo} registrado correctamente"

        page.pop_dialog()
        if al_guardar:
            al_guardar(mensaje)

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo_modal, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=360,
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    segmento_tipo,
                    campo_monto,
                    campo_categoria,
                    campo_desc,
                    btn_fecha,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.FilledButton(
                "Guardar",
                icon=ft.Icons.CHECK,
                on_click=guardar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(dialogo)


def mostrar_dialogo_confirmacion(
    page: ft.Page,
    titulo: str,
    mensaje: str,
    al_confirmar: Callable[[], None],
):
    """Muestra un cuadro de confirmación para acciones destructivas como eliminar."""
    def confirmar(e):
        page.pop_dialog()
        al_confirmar()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.FilledButton(
                "Eliminar",
                bgcolor=ft.Colors.RED_700,
                color=ft.Colors.WHITE,
                icon=ft.Icons.DELETE,
                on_click=confirmar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialogo)
