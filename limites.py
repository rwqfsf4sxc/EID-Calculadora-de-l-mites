# ============================================================
# CALCULADORA DE LÍMITES MATEMÁTICOS
# ============================================================
# PROYECTO E.I.D. CALCULO BASICO
# Catalina Ojeda, Tomas Mardones
# ============================================================



# Importamos las librerías que necesitamos
import customtkinter as ctk          # Para crear la ventana(interfaz) 
import matplotlib.pyplot as plt      # Para crear la gráfica
import sympy as sp                   # Para hacer los cálculos matemáticos


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Esto es para poner la gráfica de matplotlib dentro de nuestra ventana

# ============================================================
# FUNCIÓN 1: calcular_limite
# ¿Qué hace? Calcula el límite de una función matemática.
# ¿Cómo funciona? En vez de usar sp.limit directamente,
# calculamos el límite "a mano" usando series de Taylor o
# sustitución directa con valores muy muy cercanos al punto h. ( valores por la izquierda y derecha)
# ============================================================
def calcular_limite(funcion_texto, h_texto):
    """
    Esta función calcula el límite de f(x) cuando x tiende a h.
    
    ¿Cómo calculamos el límite sin usar sp.limit?
    -----------------------------------------------
    1. Primero intentamos sustituir x = h directamente en la función.
       Si da un número normal, ese ES el límite.
    
    2. Si al sustituir obtenemos algo raro (como 0/0 o infinito/infinito),
       se llama "indeterminación". En ese caso:
       - Usamos series de Taylor (sp.series) para expandir la función
         cerca del punto h y simplificar la expresión.
       - La serie de Taylor es como "aproximar" la función con una suma
         de términos más simples, lo que nos ayuda a resolver la indeterminación.
    
    3. Si el límite es hacia infinito (oo) o menos infinito (-oo),
       evaluamos la función con valores muy grandes o muy pequeños
       y vemos hacia dónde se dirige.
    """
    
    try:
        # Creamos la variable simbólica x (como en matemáticas)
        x = sp.Symbol('x')
        
        # Convertimos el texto que escribió el usuario en una fórmula matemática
        # Por ejemplo: "sin(x)/x" se convierte en una fórmula que sympy entiende
        funcion = sp.sympify(funcion_texto)
        
        # Revisamos si h es infinito o menos infinito
        h_texto_limpio = h_texto.strip().lower()
        
        if h_texto_limpio in ['inf', 'infinito', 'oo', '+inf', '+oo']:
            h = sp.oo  # Infinito positivo en sympy
        elif h_texto_limpio in ['-inf', '-infinito', '-oo']:
            h = -sp.oo  # Infinito negativo en sympy
        else:
            # Convertimos h a número
            h = sp.sympify(h_texto)
        
        # -------------------------------------------------------
        # PASO 1: Intentamos sustituir x = h directamente
        # -------------------------------------------------------
        resultado_directo = funcion.subs(x, h)
        resultado_simplificado = sp.simplify(resultado_directo)
        
        # Verificamos si el resultado es un número "normal" (no indeterminado)
        # sp.nan significa "no es un número" (NaN = Not a Number)
        if resultado_simplificado != sp.nan and resultado_simplificado.is_finite:
            return resultado_simplificado, None  # Retornamos el resultado
        
        # -------------------------------------------------------
        # PASO 2: Si hay indeterminación, usamos series de Taylor
        # Esto solo funciona cuando h es un número finito (no infinito)
        # -------------------------------------------------------
        if h != sp.oo and h != -sp.oo:
            try:
                # sp.series expande la función alrededor del punto h
                # Esto es como escribir f(x) ≈ a₀ + a₁(x-h) + a₂(x-h)² + ...
                # El orden=5 significa que tomamos hasta el 5to término
                serie = sp.series(funcion, x, h, 5)
                
                # Quitamos los términos con "O" (los de orden mayor)
                # y evaluamos en x = h
                serie_sin_o = serie.removeO()
                resultado_serie = serie_sin_o.subs(x, h)
                resultado_serie = sp.simplify(resultado_serie)
                
                if resultado_serie != sp.nan and resultado_serie.is_finite:
                    return resultado_serie, None
            except Exception:
                pass  # Si falla la serie, seguimos intentando
        
        # -------------------------------------------------------
        # PASO 3: Para límites al infinito, usamos sustitución
        # Hacemos el cambio de variable: t = 1/x, cuando x→∞, t→0
        # -------------------------------------------------------
        if h == sp.oo:
            t = sp.Symbol('t')
            funcion_cambiada = funcion.subs(x, 1/t)
            funcion_cambiada = sp.simplify(funcion_cambiada)
            resultado_inf = funcion_cambiada.subs(t, 0)
            resultado_inf = sp.simplify(resultado_inf)
            
            if resultado_inf != sp.nan and resultado_inf.is_finite:
                return resultado_inf, None
            
            # Si sigue sin funcionar, miramos el comportamiento de la serie
            try:
                serie_inf = sp.series(funcion_cambiada, t, 0, 3)
                coef_principal = serie_inf.removeO().subs(t, 0)
                if coef_principal != sp.nan:
                    return sp.simplify(coef_principal), None
            except Exception:
                pass
        
        # Para límites a menos infinito
        if h == -sp.oo:
            t = sp.Symbol('t')
            funcion_cambiada = funcion.subs(x, -1/t)
            funcion_cambiada = sp.simplify(funcion_cambiada)
            resultado_inf = funcion_cambiada.subs(t, 0)
            resultado_inf = sp.simplify(resultado_inf)
            
            if resultado_inf != sp.nan and resultado_inf.is_finite:
                return resultado_inf, None
            
            try:
                serie_inf = sp.series(funcion_cambiada, t, 0, 3)
                coef_principal = serie_inf.removeO().subs(t, 0)
                if coef_principal != sp.nan:
                    return sp.simplify(coef_principal), None
            except Exception:
                pass
        
        # Si llegamos aquí, el límite es indeterminado
        return None, "indeterminado"
    
    except Exception as e:
        # Si hubo algún error (como escribir mal la función)
        return None, f"Error: {str(e)}"


# ============================================================
# FUNCIÓN: hacer_grafica
# ¿Qué hace? Dibuja la gráfica de la función y marca el límite.
# ============================================================
def hacer_grafica(ax, funcion_texto, h_texto, resultado):
    """
    Esta función dibuja la gráfica de la función matemática.
    ax es el "lienzo" donde dibujamos la gráfica.
    """
    
    # Limpiamos la gráfica anterior (borramos lo que había)
    ax.clear()
    
    try:
        x = sp.Symbol('x')
        funcion = sp.sympify(funcion_texto)
        
        # Determinamos dónde graficar (el rango de x)
        h_texto_limpio = h_texto.strip().lower()
        es_infinito = h_texto_limpio in ['inf', 'infinito', 'oo', '+inf', '+oo',
                                          '-inf', '-infinito', '-oo']
        
        if es_infinito:
            # Si el límite es al infinito, mostramos valores grandes
            x_inicio = -20
            x_fin = 20
        else:
            h_num = float(sp.sympify(h_texto))
            # Mostramos un rango alrededor del punto h
            x_inicio = h_num - 5
            x_fin = h_num + 5
        
        # Creamos los puntos x donde vamos a evaluar la función
        # Usamos sympy para generar puntos (no numpy)
        # Hacemos 300 puntos entre x_inicio y x_fin
        paso = (x_fin - x_inicio) / 300
        puntos_x = []
        puntos_y = []
        
        # Vamos punto a punto calculando f(x)
        xi = x_inicio
        while xi <= x_fin:
            try:
                yi = funcion.subs(x, xi)
                yi_num = float(yi)
                
                # Solo guardamos el punto si el valor es razonable
                # (evitamos valores muy grandes que arruinen la gráfica)
                if abs(yi_num) < 1000:
                    puntos_x.append(xi)
                    puntos_y.append(yi_num)
                else:
                    # Si el valor es muy grande, ponemos un "hueco" en la gráfica
                    puntos_x.append(xi)
                    puntos_y.append(float('nan'))
            except Exception:
                # Si no se puede evaluar en este punto, lo saltamos
                puntos_x.append(xi)
                puntos_y.append(float('nan'))
            
            xi += paso
        
        # Dibujamos la función con una línea azul
        ax.plot(puntos_x, puntos_y, color='steelblue', linewidth=2, label=f'f(x) = {funcion_texto}')
        
        # Marcamos el punto del límite con un punto rojo
        if resultado is not None and not es_infinito:
            try:
                h_num = float(sp.sympify(h_texto))
                y_limite = float(resultado)
                
                # Dibujamos un punto rojo grande en el límite
                ax.plot(h_num, y_limite, 'ro', markersize=10, label=f'Límite = {resultado}', zorder=5)
                
                # Dibujamos líneas punteadas hacia los ejes (como en el libro)
                ax.axvline(x=h_num, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax.axhline(y=y_limite, color='red', linestyle='--', alpha=0.5, linewidth=1)
                
            except Exception:
                pass
        
        # Líneas de los ejes (x=0 y y=0)
        ax.axhline(y=0, color='black', linewidth=0.8)
        ax.axvline(x=0, color='black', linewidth=0.8)
        
        # Cuadrícula para que sea más fácil de leer
        ax.grid(True, alpha=0.3)
        
        # Títulos y etiquetas
        if resultado is not None:
            ax.set_title(f'lim f(x) = {resultado}  cuando x → {h_texto}', fontsize=11)
        else:
            ax.set_title(f'Gráfica de f(x) = {funcion_texto}', fontsize=11)
        
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.legend(loc='upper right', fontsize=9)
        
    except Exception as e:
        # Si hubo error al graficar, mostramos un mensaje en la gráfica
        ax.text(0.5, 0.5, f'No se pudo graficar\n{str(e)}',
                ha='center', va='center', transform=ax.transAxes, fontsize=10)
        ax.set_title('Error al graficar')


# ============================================================
# FUNCIÓN: al_presionar_calcular
# ¿Qué hace? Es la función que se ejecuta cuando el usuario
# presiona el botón "Calcular". Lee los datos, calcula el
# límite y actualiza la gráfica.
# ============================================================
def al_presionar_calcular():
    """
    Esta función "conecta" el botón con el cálculo y la gráfica.
    Se llama cada vez que el usuario hace clic en "Calcular".
    """
    
    # Leemos lo que el usuario escribió en los campos
    texto_funcion = entrada_funcion.get().strip()
    texto_h = entrada_h.get().strip()
    
    # Verificamos que no estén vacíos
    if texto_funcion == "" or texto_h == "":
        label_resultado.configure(text="⚠ Por favor ingresa la función y el valor de h",
                                   text_color="orange")
        return
    
    # Llamamos a la función que calcula el límite
    resultado, error = calcular_limite(texto_funcion, texto_h)
    
    # Mostramos el resultado en la pantalla
    if error == "indeterminado":
        # Si el límite es indeterminado, mostramos el mensaje
        label_resultado.configure(
            text="⚠ Límite Indeterminado\nPor favor ingresa nuevamente los datos.",
            text_color="orange"
        )
        resultado_para_grafica = None
        
    elif error is not None and error.startswith("Error"):
        # Si hubo un error (función mal escrita, etc.)
        label_resultado.configure(
            text=f"❌ {error}\nRevisa la función ingresada.",
            text_color="red"
        )
        resultado_para_grafica = None
        
    else:
        # Si el cálculo fue exitoso, mostramos el resultado
        label_resultado.configure(
            text=f"✓ Límite = {resultado}",
            text_color="lightgreen"
        )
        resultado_para_grafica = resultado
    
    # Actualizamos la gráfica con los nuevos datos
    hacer_grafica(ax, texto_funcion, texto_h, resultado_para_grafica)
    canvas.draw()  # Redibujamos el canvas para mostrar la nueva gráfica


# ============================================================
# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# Aquí creamos la ventana y todos sus componentes
# ============================================================

# Configuramos el tema de customtkinter (modo oscuro)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Creamos la ventana principal
ventana = ctk.CTk()
ventana.title("Calculadora de Límites")
ventana.geometry("950x580")
ventana.resizable(True, True)

# ============================================================
# PANEL IZQUIERDO: Campos de entrada y botón
# ============================================================
panel_izquierdo = ctk.CTkFrame(ventana, width=300, corner_radius=10)
panel_izquierdo.pack(side="left", fill="y", padx=10, pady=10)
panel_izquierdo.pack_propagate(False)  # Para que no cambie de tamaño

# Título del panel
titulo = ctk.CTkLabel(panel_izquierdo,
                       text="Calculadora de Límites",
                       font=ctk.CTkFont(size=16, weight="bold"))
titulo.pack(pady=(20, 5))

subtitulo = ctk.CTkLabel(panel_izquierdo,
                          text="Ingresa los datos y presiona Calcular",
                          font=ctk.CTkFont(size=11),
                          text_color="gray")
subtitulo.pack(pady=(0, 20))

# Separador visual
separador1 = ctk.CTkFrame(panel_izquierdo, height=2, fg_color="gray30")
separador1.pack(fill="x", padx=20, pady=5)

# Campo 1: Función f(x)
label_funcion = ctk.CTkLabel(panel_izquierdo,
                               text="Función f(x):",
                               font=ctk.CTkFont(size=13, weight="bold"))
label_funcion.pack(anchor="w", padx=20, pady=(15, 3))

# Pequeña ayuda para el usuario
hint_funcion = ctk.CTkLabel(panel_izquierdo,
                              text="Ejemplos: sin(x)/x, (x**2-1)/(x-1), exp(x)",
                              font=ctk.CTkFont(size=10),
                              text_color="gray",
                              wraplength=260)
hint_funcion.pack(anchor="w", padx=20, pady=(0, 5))

entrada_funcion = ctk.CTkEntry(panel_izquierdo,
                                placeholder_text="Escribe f(x) aquí...",
                                width=260,
                                height=38,
                                font=ctk.CTkFont(size=13))
entrada_funcion.pack(padx=20, pady=(0, 15))

# Campo 2: Valor de h
label_h = ctk.CTkLabel(panel_izquierdo,
                         text="x tiende a (h):",
                         font=ctk.CTkFont(size=13, weight="bold"))
label_h.pack(anchor="w", padx=20, pady=(5, 3))

hint_h = ctk.CTkLabel(panel_izquierdo,
                        text="Usa: 0, 1, -2, pi, oo, -oo",
                        font=ctk.CTkFont(size=10),
                        text_color="gray")
hint_h.pack(anchor="w", padx=20, pady=(0, 5))

entrada_h = ctk.CTkEntry(panel_izquierdo,
                          placeholder_text="Valor de h...",
                          width=260,
                          height=38,
                          font=ctk.CTkFont(size=13))
entrada_h.pack(padx=20, pady=(0, 20))

# Separador visual
separador2 = ctk.CTkFrame(panel_izquierdo, height=2, fg_color="gray30")
separador2.pack(fill="x", padx=20, pady=5)

# Botón de calcular
boton_calcular = ctk.CTkButton(panel_izquierdo,
                                text="Calcular Límite",
                                command=al_presionar_calcular,
                                width=260,
                                height=42,
                                font=ctk.CTkFont(size=14, weight="bold"),
                                fg_color="steelblue",
                                hover_color="#1a5276")
boton_calcular.pack(padx=20, pady=(15, 10))

# Área donde mostramos el resultado
label_resultado = ctk.CTkLabel(panel_izquierdo,
                                text=" Resultado ",
                                font=ctk.CTkFont(size=13),
                                text_color="gray",
                                wraplength=260,
                                justify="center")
label_resultado.pack(padx=20, pady=(10, 10))


# ============================================================
# PANEL DERECHO: Gráfica de matplotlib
# ============================================================
panel_derecho = ctk.CTkFrame(ventana, corner_radius=10)
panel_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Creamos la figura de matplotlib (el "papel" donde se dibuja)
# Fondo oscuro para que combine con customtkinter
figura, ax = plt.subplots(figsize=(6, 5), facecolor='#2b2b2b')
ax.set_facecolor('#1a1a2e')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')
for spine in ax.spines.values():
    spine.set_edgecolor('gray')

# Mensaje inicial en la gráfica
ax.text(0.5, 0.5, 'Ingresa una función y el valor de h, presiona\n"Calcular Límite" para ver la gráfica',
        ha='center', va='center', transform=ax.transAxes,
        fontsize=12, color='gray', style='italic')
ax.set_title('Gráfica del Límite', color='white', fontsize=12)

# Ajustamos los márgenes de la figura
figura.tight_layout(pad=1.5)

# "Pegamos" la gráfica de matplotlib dentro de nuestra ventana de customtkinter
canvas = FigureCanvasTkAgg(figura, master=panel_derecho)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

# ============================================================
# INICIAMOS LA APLICACIÓN
# Esta línea hace que la ventana aparezca y se quede abierta
# hasta que el usuario la cierre.
# ============================================================
ventana.mainloop()
