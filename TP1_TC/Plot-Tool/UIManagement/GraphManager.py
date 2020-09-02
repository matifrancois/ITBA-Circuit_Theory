from GraphFetching.MeasurementFetching import MeasurementFetching
from GraphFetching.SpiceFetching import SpiceFetching
from GraphFetching.TransferenceFetching import TransferenceFetching


# Clase GraphManager. Es una clase que almacena, agrega y elimina los valores y propiedades de los gráficos que se deben
# mostrar en pantalla.
# Las funciones de UIWindow llaman a funciones de esta clase para consultar que gráficos se deben mostrar,
# esconder, etc.
class GraphManager:
    def __init__(self, mainWindow):
        self.graphicsToShow = {}  # Diccionario de gráficos a mostrar. Contiene de donde son (Spice, med, H)
        # y los valores).
        self.parent = mainWindow
        self.transferenceKey = "transferenceKey"
        self.spiceKey = "spiceKey"
        self.medKey = "medKey"
        # Llamado a funciones que importen los valores de los gráficos. Se encuentran en la carpeta GraphFetching.
        self.measure = MeasurementFetching(self)
        self.spice = SpiceFetching(self)
        self.transfer = TransferenceFetching(self)
        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Posibles colores para los graficos

    # Toggle de los gráficos. Mostrar/Esconder.
    def spice_checked(self):
        self.__toggle_graphics__(self.spiceKey)

    # Toggle de los gráficos. Mostrar/Esconder.
    def transf_checked(self):
        self.__toggle_graphics__(self.transferenceKey)

    # Toggle de los gráficos. Mostrar/Esconder.
    def med_checked(self):
        self.__toggle_graphics__(self.medKey)

    # Togglea los graficos con un key determinado. Por ejemplo spiceKey.
    def __toggle_graphics__(self, key):
        if (len(self.graphicsToShow) > 0) and (key in self.graphicsToShow.keys()):
            for graph in self.graphicsToShow[key]:
                graph[0].activated = not graph[0].activated

        self.draw()

    # Agrega un gráfico. Parámetros: graphic_value, valore del gráfico (se debe pasar un objeto del tipo GraphValues
    # de la carpeta GraphStructures; key: de donde es (ej self.spiceKey, self.medKey, self.transferenceKey);
    # color: color del que se desea mostrar el gráfico (Se encuentran los posibles valores en self.colors)
    def add_graphic(self, graphic_value, key, color):

        if (len(self.graphicsToShow) == 0) or not (key in self.graphicsToShow.keys()) or \
                (self.graphicsToShow[key] is None) or (not isinstance(self.graphicsToShow[key], list)):
            self.graphicsToShow[key] = []

        self.graphicsToShow[key].append((graphic_value, color))

    # Remueve los graficos con un determinado key. Ej self.spiceKey. Se eliminarían todos los gráficos que
    # provengan de Spice.
    def remove_graphic(self, key):
        self.graphicsToShow.pop(key)

    # Remueve todos los graficos
    def remove_all_graphics(self):
        self.graphicsToShow.clear()
        self.draw()

    # Función asociada al botón de eliminar todos los graficos
    def delete_button_graph(self):
        self.remove_all_graphics()

    # Redibuja. Le pasa a la ventana padre una lista con los valores del diccionario de gráficos a mostrar y luego le
    # dice a la ventana padre que se actualice.
    def draw(self):
        self.parent.graphics = list(self.graphicsToShow.values())
        self.parent.__update_graph__()

    # Funciones asociadas a los botones de agregar gráficos desde distintos lugares (spice, med, H)
    def trans_button_graph(self):

        self.transfer.transference_plot()

    def med_button_graph(self):

        self.measure.measurement_plot()

    def spice_button_graph(self):

        self.spice.spice_plot()

    # Devuelve el siguiente valor de color que le toque al gráfico agregado.
    def get_next_color(self):
        self.colors.reverse()
        next_color = self.colors.pop()
        self.colors.reverse()
        self.colors.append(next_color)
        return next_color
