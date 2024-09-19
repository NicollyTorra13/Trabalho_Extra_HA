class Negacoes:
    def __init__(self):
        self._colaboradores_negados = {
            223344556: "Pedro Santos",
        }

    def verifica_tag_negada(self, tag):
        return tag in self._colaboradores_negados

    def obter_nome_negado(self, tag):
        return self._colaboradores_negados.get(tag)

    def adicionar_negado(self, tag, nome):
        self._colaboradores_negados[tag] = nome

    def remover_negado(self, tag):
        if tag in self._colaboradores_negados:
            del self._colaboradores_negados[tag]
