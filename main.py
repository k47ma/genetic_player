from algorithm import Algorithm

if __name__ == '__main__':
    algo = Algorithm(population_size=1000, mutation_rate=0.01, max_generation=10000)
    algo.start()
