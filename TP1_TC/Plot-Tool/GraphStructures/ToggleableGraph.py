# Conjunto de un GraphValues y un flag de activado.
# El flag de activado indica si el gráfico se debe mostrar o estar escondido.
# parámetro graph: objeto de GraphValues.
# parámetro activated: valor inicial del flag.

class ToggleableGraph:
    def __init__(self, graph, activated):
        self.activated = activated
        self.graph = graph
