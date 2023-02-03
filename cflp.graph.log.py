from matplotlib import pyplot 
import pandas

csv_log = 'cflp.sobolev.log.csv'
dados = pandas.read_csv(csv_log, sep=';', decimal=',')

print(dados, '\n', csv_log)

res = {}
for row in range(len(dados)):
	solver = dados['solver'][row]
	file_name = dados['instance_source_file_name'][row]
	time_limit = dados['time_limit'][row]
	nodes = dados['nodes'][row]
	gap = dados['gap'][row]
	

	if not solver in res:
		res[solver] = {}
	if not time_limit in res[solver]:	
		res[solver][time_limit] = []

	res[solver][time_limit].append((gap, nodes, file_name))	

for solver in res:
	for time_limit in res[solver]:
		res[solver][time_limit].sort()
	
	times = list(res[solver])	
	times.sort()

	optimal = [len({f for g,n,f in res[solver][t] if not g}) for t in times]
	print('\n', solver)
	print(times)
	print(optimal)
	
	pyplot.plot(times, optimal, label=solver, marker='.')
pyplot.title('Optimal')	
pyplot.xlabel('Time limit')
pyplot.ylabel('Gap = 0')
pyplot.grid(True)
pyplot.legend()
pyplot.show()
