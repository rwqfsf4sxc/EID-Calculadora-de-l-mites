# CALCULADORA DE LÍMITES MATEMÁTICOS
# Proyecto E.I.D. Cálculo Básico
# Alumnos : Catalina Ojeda, Tomás Mardones

import customtkinter as ctk
import matplotlib.pyplot as plt
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def calcular_limite(funcion_texto, h_texto):
    # Calcula el límite de f(x) cuando x tiende a h.
    # Primero trata de sustituir directamente, y si hay indeterminación
    # usa series de Taylor para resolverla.

    try:
        x = sp.Symbol('x')
        funcion = sp.sympify(funcion_texto)

        # Limpiamos el texto y vemos si h es infinito
        h_texto_limpio = h_texto.strip().lower()

        if h_texto_limpio in ['inf', 'infinito', 'oo', '+inf', '+oo']:
            h = sp.oo
        elif h_texto_limpio in ['-inf', '-infinito', '-oo']:
            h = -sp.oo
        else:
            h = sp.sympify(h_texto)

        # Intento 1: sustituir x = h directo en la función
        resultado = sp.simplify(funcion.subs(x, h))

        if resultado != sp.nan and resultado.is_finite:
            return resultado, None

        # Intento 2: si hay indeterminación (0/0, etc.), usamos series de Taylor
        # La idea es expandir f(x) alrededor de h y ver qué pasa
        if h not in (sp.oo, -sp.oo):
            try:
                serie = sp.series(funcion, x, h, 5).removeO()
                resultado = sp.simplify(serie.subs(x, h))

                if resultado != sp.nan and resultado.is_finite:
                    return resultado, None
            except Exception:
                pass

        # Intento 3: para límites al infinito hacemos t = 1/x
        # cuando x tiende a oo (inf), t tiende a 0, entonces evaluamos ahí
        if h == sp.oo:
            t = sp.Symbol('t')
            f_cambiada = sp.simplify(funcion.subs(x, 1/t))
            resultado = sp.simplify(f_cambiada.subs(t, 0))

            if resultado != sp.nan and resultado.is_finite:
                return resultado, None

            try:
                serie = sp.series(f_cambiada, t, 0, 3).removeO()
                coef = serie.subs(t, 0)
                if coef != sp.nan:
                    return sp.simplify(coef), None
            except Exception:
                pass

        # Lo mismo pero para -oo, usamos x = -1/t
        if h == -sp.oo:
            t = sp.Symbol('t')
            f_cambiada = sp.simplify(funcion.subs(x, -1/t))
            resultado = sp.simplify(f_cambiada.subs(t, 0))

            if resultado != sp.nan and resultado.is_finite:
                return resultado, None

            try:
                serie = sp.series(f_cambiada, t, 0, 3).removeO()
                coef = serie.subs(t, 0)
                if coef != sp.nan:
                    return sp.simplify(coef), None
            except Exception:
                pass

        return None, "indeterminado"

    except Exception as e:
        return None, f"Error: {str(e)}"


def hacer_grafica(ax, funcion_texto, h_texto, resultado):

    ax.clear()

    try:
        x = sp.Symbol('x')
        funcion = sp.sympify(funcion_texto)

        h_texto_limpio = h_texto.strip().lower()
        es_infinito = h_texto_limpio in [
            'inf', 'infinito', 'oo', '+inf', '+oo',
            '-inf', '-infinito', '-oo'
        ]

        # Rango del eje x
        if es_infinito:
            x_inicio, x_fin = -20, 20
        else:
            h_num = float(sp.sympify(h_texto))
            x_inicio = h_num - 5
            x_fin = h_num + 5

        # Evaluamos f(x) en 300 puntos entre x_inicio y x_fin
        paso = (x_fin - x_inicio) / 300
        puntos_x, puntos_y = [], []

        xi = x_inicio
        while xi <= x_fin:
            try:
                yi = float(funcion.subs(x, xi))
                # borramos valores muy grandes para que no se rompa la escala
                puntos_x.append(xi)
                puntos_y.append(yi if abs(yi) < 1000 else float('nan'))
            except Exception:
                puntos_x.append(xi)
                puntos_y.append(float('nan'))
            xi += paso

        ax.plot(puntos_x, puntos_y, color='steelblue', linewidth=2,
                label=f'f(x) = {funcion_texto}')

        if resultado is not None and not es_infinito:
            try:
                h_num = float(sp.sympify(h_texto))
                y_lim = float(resultado)

                ax.plot(h_num, y_lim, 'ro', markersize=10, #para marcar punto del limite con lineas segmentadas
                        label=f'Límite = {resultado}', zorder=5)
                ax.axvline(x=h_num, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax.axhline(y=y_lim, color='red', linestyle='--', alpha=0.5, linewidth=1)
            except Exception:
                pass

        # Ejes y cuadrícula
        ax.axhline(y=0, color='white', linewidth=0.8)
        ax.axvline(x=0, color='white', linewidth=0.8)
        ax.grid(True, alpha=0.3)

        titulo = (f'lim f(x) = {resultado}  cuando x → {h_texto}'
                  if resultado is not None
                  else f'Gráfica de f(x) = {funcion_texto}')
        ax.set_title(titulo, fontsize=11, color='white')
        ax.set_xlabel('x', color='white')
        ax.set_ylabel('f(x)', color='white')
        ax.legend(loc='upper right', fontsize=9) #cuadro con la informacion del resultado

    except Exception as e:
        ax.text(0.5, 0.5, f'No se pudo graficar\n{str(e)}',
                ha='center', va='center', transform=ax.transAxes, fontsize=10)
        ax.set_title('Error al graficar')


def boton_calcular():

    texto_funcion = entrada_funcion.get().strip()
    texto_h = entrada_h.get().strip()

    if not texto_funcion or not texto_h:
        label_resultado.configure(
            text=" Por favor ingresa la función y el valor de h",
            text_color="orange"
        )
        return

    resultado, error = calcular_limite(texto_funcion, texto_h)

    if error == "indeterminado":
        label_resultado.configure(
            text=" Límite Indeterminado\nPor favor ingresa nuevamente los datos.",
            text_color="orange"
        )
        resultado_para_grafica = None

    elif error and error.startswith("Error"):
        label_resultado.configure(
            text=f" {error}\nRevisa la función ingresada.",
            text_color="red"
        )
        resultado_para_grafica = None

    else:
        label_resultado.configure(
            text=f" Límite = {resultado}",
            text_color="lightgreen"
        )
        resultado_para_grafica = resultado

    hacer_grafica(ax, texto_funcion, texto_h, resultado_para_grafica)
    canvas.draw()

# Ventana 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ventana = ctk.CTk()
ventana.title("Calculadora de Límites")
ventana.geometry("950x580")
ventana.resizable(True, True)

# Panel izquierdo: entradas y botón
panel_izquierdo = ctk.CTkFrame(ventana, width=300,)
panel_izquierdo.pack(side="left", fill="y", padx=10, pady=10)
panel_izquierdo.pack_propagate(False)

ctk.CTkLabel(panel_izquierdo,
             text="Calculadora de Límites",
             font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))



ctk.CTkLabel(panel_izquierdo,
             text="Ingrese la funcion f(x)",
             font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(15, 3))

entrada_funcion = ctk.CTkEntry(panel_izquierdo,
                                
                                width=260, height=38,
                                font=ctk.CTkFont(size=13))
entrada_funcion.pack(padx=20, pady=(0, 15))

ctk.CTkLabel(panel_izquierdo,
             text="Ingrese el valor de h",
             font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(5, 3))

entrada_h = ctk.CTkEntry(panel_izquierdo,
                          
                          width=260, height=38,
                          font=ctk.CTkFont(size=13))
entrada_h.pack(padx=20, pady=(0, 20))

ctk.CTkButton(panel_izquierdo,
              text="Calcular Límite",
              command=boton_calcular,
              width=260, height=42,
              font=ctk.CTkFont(size=14, weight="bold"),
              fg_color="steelblue",
              hover_color="#1a5276").pack(padx=20, pady=(15, 10))

label_resultado = ctk.CTkLabel(panel_izquierdo,
                                text=" Resultado ",
                                font=ctk.CTkFont(size=13),
                                text_color="gray",
                                wraplength=260,
                                justify="center")
label_resultado.pack(padx=20, pady=(10, 10))

# Panel derecho: gráfico
panel_derecho = ctk.CTkFrame(ventana, corner_radius=1)
panel_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

figura, ax = plt.subplots(figsize=(6, 5), facecolor='#2b2b2b')
ax.set_facecolor('#1a1a2e')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')
for spine in ax.spines.values():
    spine.set_edgecolor('gray')


ax.set_title('Gráfica del Límite', color='white', fontsize=12)
figura.tight_layout(pad=1.5)

canvas = FigureCanvasTkAgg(figura, master=panel_derecho)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

ventana.mainloop() #mantiene la ventana abierta
