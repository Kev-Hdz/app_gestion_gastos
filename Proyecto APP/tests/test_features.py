import unittest
import os
import tempfile
from datetime import datetime, timedelta
import flet as ft

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.movimiento import Movimiento, CATEGORIAS_GASTO, ICONOS
from database.db_manager import DBManager
from components.cards import crear_tarjeta_balance, crear_tarjetas_resumen
from components.variance_chart import crear_tarjeta_grafica_varianza
from views.dashboard_view import DashboardView
from views.historial_view import HistorialView
from views.estadisticas_view import EstadisticasView


class TestMejoras(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = os.path.join(self.temp_dir.name, "test_gastos.db")
        self.db = DBManager(db_path=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_categoria_despensa_en_modelos(self):
        """Verifica que la categoría 'Despensa' esté registrada en las listas y tenga icono."""
        self.assertIn("Despensa", CATEGORIAS_GASTO)
        self.assertIn("Despensa", ICONOS)
        self.assertEqual(ICONOS["Despensa"], ft.Icons.LOCAL_GROCERY_STORE)

    def test_guardar_y_consultar_despensa(self):
        """Verifica que se puedan persistir y consultar gastos de Despensa."""
        mov = Movimiento(
            tipo="Gasto",
            categoria="Despensa",
            descripcion="Supermercado semanal",
            monto=450.0,
            fecha=datetime.now(),
        )
        mov_id = self.db.agregar(mov)
        self.assertIsNotNone(mov_id)

        recuperado = self.db.obtener_por_id(mov_id)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.categoria, "Despensa")
        self.assertEqual(recuperado.monto, 450.0)

    def test_filtros_temporales_15_y_30_dias(self):
        """Verifica que el resumen y balance se calculen correctamente para 15 días, 30 días y todos."""
        ahora = datetime.now()

        # Limpiar base de datos para prueba exacta
        with self.db._get_connection() as conn:
            conn.cursor().execute("DELETE FROM movimientos")
            conn.commit()

        # Movimiento 1: Hoy (+1000 ingreso)
        self.db.agregar(Movimiento(
            tipo="Ingreso",
            categoria="Sueldo",
            descripcion="Pago hoy",
            monto=1000.0,
            fecha=ahora,
        ))

        # Movimiento 2: Hace 5 días (-200 gasto en Comida)
        self.db.agregar(Movimiento(
            tipo="Gasto",
            categoria="Comida",
            descripcion="Cena",
            monto=200.0,
            fecha=ahora - timedelta(days=5),
        ))

        # Movimiento 3: Hace 20 días (-300 gasto en Despensa)
        self.db.agregar(Movimiento(
            tipo="Gasto",
            categoria="Despensa",
            descripcion="Despensa quincenal",
            monto=300.0,
            fecha=ahora - timedelta(days=20),
        ))

        # Movimiento 4: Hace 45 días (+500 ingreso antiguo)
        self.db.agregar(Movimiento(
            tipo="Ingreso",
            categoria="Ventas",
            descripcion="Venta antigua",
            monto=500.0,
            fecha=ahora - timedelta(days=45),
        ))

        # 1. Resumen últimos 15 días: debe incluir Mov 1 (+1000) y Mov 2 (-200)
        res_15 = self.db.obtener_resumen(dias=15)
        self.assertEqual(res_15["ingresos"], 1000.0)
        self.assertEqual(res_15["gastos"], 200.0)
        self.assertEqual(res_15["balance"], 800.0)
        self.assertEqual(res_15["total_items"], 2)

        # 2. Resumen últimos 30 días: debe incluir Mov 1 (+1000), Mov 2 (-200), Mov 3 (-300)
        res_30 = self.db.obtener_resumen(dias=30)
        self.assertEqual(res_30["ingresos"], 1000.0)
        self.assertEqual(res_30["gastos"], 500.0)
        self.assertEqual(res_30["balance"], 500.0)
        self.assertEqual(res_30["total_items"], 3)

        # 3. Resumen Todos: incluye los 4 movimientos
        res_todos = self.db.obtener_resumen(dias=None)
        self.assertEqual(res_todos["ingresos"], 1500.0)
        self.assertEqual(res_todos["gastos"], 500.0)
        self.assertEqual(res_todos["balance"], 1000.0)
        self.assertEqual(res_todos["total_items"], 4)

    def test_obtener_datos_varianza_y_picos(self):
        """Verifica el cálculo de varianza entre gastos totales y comida, y detección de picos."""
        ahora = datetime.now()

        with self.db._get_connection() as conn:
            conn.cursor().execute("DELETE FROM movimientos")
            conn.commit()

        # Día 1 (Hace 3 días): Gasto Comida 150, Gasto Transporte 100 -> Total Gasto 250, Comida 150
        f1 = ahora - timedelta(days=3)
        self.db.agregar(Movimiento("Gasto", "Comida", "Almuerzo", 150.0, f1))
        self.db.agregar(Movimiento("Gasto", "Transporte", "Taxi", 100.0, f1))

        # Día 2 (Hace 1 día): Gasto Despensa 800 -> Total Gasto 800, Comida 0 (Pico de gasto)
        f2 = ahora - timedelta(days=1)
        self.db.agregar(Movimiento("Gasto", "Despensa", "Super", 800.0, f2))

        # Día 3 (Hoy): Gasto Comida 500 -> Total Gasto 500, Comida 500 (Pico de comida)
        f3 = ahora
        self.db.agregar(Movimiento("Gasto", "Comida", "Cena lujosa", 500.0, f3))

        datos = self.db.obtener_datos_varianza_gastos_comida()
        self.assertEqual(datos["total_dias"], 3)

        # Pico de gastos debe ser 800.0 en el Día 2
        self.assertEqual(datos["pico_gastos"]["monto"], 800.0)

        # Pico de comida debe ser 500.0 en el Día 3
        self.assertEqual(datos["pico_comida"]["monto"], 500.0)

        # Puntos
        puntos = datos["puntos"]
        self.assertEqual(len(puntos), 3)
        self.assertEqual(puntos[0]["total_gastos"], 250.0)
        self.assertEqual(puntos[0]["total_comida"], 150.0)
        self.assertEqual(puntos[0]["varianza"], 100.0)

    def test_renderizado_componentes_y_vistas(self):
        """Verifica que los componentes visuales y vistas se instancien correctamente."""
        tarjeta_balance = crear_tarjeta_balance(500.0, "Balance (15 días)")
        self.assertIsNotNone(tarjeta_balance)

        tarjeta_balance_neg = crear_tarjeta_balance(-200.0, "Balance negativo")
        self.assertIsNotNone(tarjeta_balance_neg)

        datos_flujo = self.db.obtener_datos_grafica_ingresos_gastos()
        self.assertIn("total_ingresos", datos_flujo)
        self.assertIn("total_gastos", datos_flujo)
        self.assertIn("balance_neto", datos_flujo)
        self.assertGreaterEqual(len(datos_flujo["puntos"]), 1)

        tarjeta_grafica = crear_tarjeta_grafica_varianza(datos_flujo, "Últimos 15 días")
        self.assertIsNotNone(tarjeta_grafica)

        v_dash = DashboardView(self.db, lambda m: None, lambda m: None, lambda: None)
        self.assertIsNotNone(v_dash)

        v_hist = HistorialView(self.db, lambda m: None, lambda m: None)
        self.assertIsNotNone(v_hist)
        self.assertIsInstance(v_hist.campo_busqueda.border, ft.OutlineInputBorder)
        self.assertEqual(v_hist.campo_busqueda.border.border_radius, 12)

        v_stat = EstadisticasView(self.db)
        self.assertIsNotNone(v_stat)


if __name__ == "__main__":
    unittest.main()
