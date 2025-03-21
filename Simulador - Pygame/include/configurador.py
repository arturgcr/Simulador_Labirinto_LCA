import csv

class Configurador:

    @classmethod
    # Função para salvar a seed e o labirinto no CSV
    def save_seed(seed, filename='data/seeds.csv'):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Adiciona a seed à primeira coluna
            writer.writerow(seed)