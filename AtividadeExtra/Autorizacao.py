class Autorizacoes:
    def __init__(self):
        self._colaboradores = {
            123456789: "João Silva",
        }

    def verifica_tag(self, tag):
        return tag in self._colaboradores

    def obter_nome(self, tag):
        return self._colaboradores.get(tag)

    def adicionar_colaborador(self, tag, nome):
        self._colaboradores[tag] = nome

    def remover_colaborador(self, tag):
        if tag in self._colaboradores:
            del self._colaboradores[tag]
