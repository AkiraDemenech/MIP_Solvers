from matplotlib import pyplot 
import pandas

csv = {}
#cbc_gap = {}
for csv_log, title in [
	('cflp.sobolev.log.csv',	'Sobolev single-source'),
	('cflp.beasley.ss.log.csv',	'Beasley single-source'),
	('cflp.beasley.ms.log.csv',	'Beasley multi-source'),
	('cflp.mess.ms.ci.log.csv',	'MESS multi-sources with customer incompatibilities')]:
	dados = pandas.read_csv(csv_log, sep=';', decimal=',')
	print(dados, '\n', csv_log)

	d = c = csv
	for k in csv_log.strip().lower().split('.')[1:-2]:					
		d = c
		if not k in c:	
			c[k] = {}
		c = c[k]	
		print(k)
	res = {}
	d[k] = dados, res, title		
	#cbc_gap[k] = 
	file_time_solver_gap = {}
	
	instances = len(set(dados['instance_source_file_name']))
	
	
	for row in range(len(dados)):
		solver = dados['solver'][row]
		file_name = dados['instance_source_file_name'][row]
		time_limit = dados['time_limit'][row]
		nodes = dados['nodes'][row] - (solver[0] == 'G') # gurobi conta a nó raiz
		gap = dados['gap'][row]
		
		if not file_name in file_time_solver_gap:
			file_time_solver_gap[file_name] = {}
		
		if not time_limit in file_time_solver_gap[file_name]:
			file_time_solver_gap[file_name][time_limit] = {}
		 	
		file_time_solver_gap[file_name][time_limit][solver] = dados['best_solution'][row]

		if not solver in res:
			res[solver] = {}
		if not time_limit in res[solver]:	
			res[solver][time_limit] = []

		res[solver][time_limit].append((gap, nodes, file_name))	

	#cbc_gap = [None] * len(dados)
	solver_time_file_gap = {}
	for file_name in file_time_solver_gap:
		for time_limit in file_time_solver_gap[file_name]:
			if not 'CBC' in file_time_solver_gap[file_name][time_limit]:
				print('CBC solver gap failed in', file_name, time_limit)
				continue 

			cbc_best = file_time_solver_gap[file_name][time_limit].pop('CBC')
			for solver in file_time_solver_gap[file_name][time_limit]:
				best = file_time_solver_gap[file_name][time_limit][solver]
				cbc_gap = file_time_solver_gap[file_name][time_limit][solver] = 100 * (cbc_best - best) / best

				if not solver in solver_time_file_gap:
					solver_time_file_gap[solver] = {}
				if not time_limit in solver_time_file_gap[solver]:
					solver_time_file_gap[solver][time_limit] = []	
				solver_time_file_gap[solver][time_limit].append((cbc_gap, file_name))	

	for solver in solver_time_file_gap:
		for time_limit in solver_time_file_gap[solver]:
			solver_time_file_gap[solver][time_limit].sort()

		times = list(solver_time_file_gap[solver])
		times.sort()
		minutes = [t/60 for t in times]

		cbc_gap_values = [[cbc_g for cbc_g, fn in solver_time_file_gap[solver][t] if len(fn) > 5 and cbc_g == cbc_g] for t in times]

		avg_cbc_gap = [sum(v) / len(v) for v in cbc_gap_values]

		print(solver, minutes, avg_cbc_gap, cbc_gap_values)
		pyplot.plot(minutes, avg_cbc_gap, label=solver, marker='.')
	pyplot.title(title + ' (average Cbc gap)')	
	pyplot.xlabel('Time limit (minutes)')
	pyplot.ylabel('Average percentage gap')
	pyplot.grid(True)
	pyplot.legend()
	pyplot.show()	

	avg_gap = {}
	for solver in res:
		for time_limit in res[solver]:
			res[solver][time_limit].sort()
		
		times = list(res[solver])	
		times.sort()
		minutes = [t/60 for t in times]

		optimal = [len({f for g,n,f in res[solver][t] if not g}) * 100 / instances for t in times]
	
		print('\n', solver)
		print(times)
		print(minutes)
		print(optimal)

	#	''' Average gap 
		avg_gap[solver] = [sum({(g if g == g else 100) for g,n,f in res[solver][t]}) / len(res[solver][t]) for t in times]	
		print(avg_gap[solver])
	#	print(avg_gap[solver][0] == avg_gap[solver][0])
	#	'''
		
	#	''' Optimal x Time 
		pyplot.plot(minutes, optimal, label=solver, marker='.')
	pyplot.title(title + ' (gap = 0)')	
	pyplot.xlabel('Time limit (minutes)')
	pyplot.ylabel('Percentage of optimal-solved instances')
	pyplot.grid(True)
	pyplot.legend()
	pyplot.show()
	#	'''

	''' Gap x Time (estranho)
	for solver in avg_gap:
		pyplot.plot(minutes, avg_gap[solver], label=solver, marker='.')
	pyplot.title(title + ' (average gap)')	
	pyplot.xlabel('Time limit (minutes)')
	pyplot.ylabel('Average percentage gap')
	pyplot.grid(True)
	pyplot.legend()
	pyplot.show()
#	'''


beasley_csv = csv['beasley']
print('Beasley CSV data')

for sources in beasley_csv:

	print(sources)
	dados, res, title = beasley_csv[sources]

	max_nodes = 0
	instances = set()
	cumulativos = {}
	for solver in res:
		for time_limit in res[solver]:
			if not time_limit in cumulativos:
				cumulativos[time_limit] = {}
			cumulativos[time_limit][solver] = {}	
			for gap, nodes, file_name in res[solver][time_limit]:	
				if not file_name[3].isalpha(): # somente considerar capa, capb e capc
					continue 
				instances.add(file_name)	
				if not nodes in cumulativos[time_limit][solver]:
					cumulativos[time_limit][solver][nodes] = []
				max_nodes = max(max_nodes, nodes)
			#	print(file_name, solver, '\t', nodes, gap)	
				cumulativos[time_limit][solver][nodes].append((gap, file_name))	

	instances = len(instances)
	avg_gap = {}
	for time_limit in cumulativos:		
		avg_gap[time_limit] = {}
		for solver in cumulativos[time_limit]:			
			nodes = list(cumulativos[time_limit][solver])
			nodes.sort()
			if not max_nodes in nodes:	
				nodes.append(max_nodes)									
			 
			optimal = []
			values = []
			avg_gap[time_limit][solver] = list(nodes), values
			if not 0 in nodes:
				nodes.insert(0,0)
			s = l = ag = 0
			
			for n in nodes:
				if n in cumulativos[time_limit][solver]:
					ag += sum(g for g, f in cumulativos[time_limit][solver][n])	
					l += len(cumulativos[time_limit][solver][n])
					s += len({f for g, f in cumulativos[time_limit][solver][n] if not g}) 
				if l:	
					values.append(ag / l)								
				optimal.append(s * 100 / instances)
			''' Optimal x Nodes		
			pyplot.plot(nodes, optimal, label=solver, marker='.') 
		pyplot.title(f'{title} (gap = 0, time limit = {time_limit / 60} minutes)')	
		pyplot.xlabel('Maximum enumerated nodes')
		pyplot.ylabel('Percentage of optimal-solved instances')
		pyplot.grid(True)
		pyplot.legend()
		pyplot.show()
		#	'''

#	''' Gap x Nodes	
	for time_limit in avg_gap:
		for solver in avg_gap[time_limit]:
			nodes, values = avg_gap[time_limit][solver]
			pyplot.plot(nodes, values, label=solver, marker='.')
		pyplot.title(f'{title} (average gap, time limit = {time_limit / 60} minutes)')	
		pyplot.xlabel('Maximum enumerated nodes')
		pyplot.ylabel('Average percentage gap')
		pyplot.grid(True)
		pyplot.legend()
		pyplot.show()	
#	'''		
	
	avg_gap = {}
	for time_limit in cumulativos:
		for solver in cumulativos[time_limit]:
			if not solver in avg_gap:
				avg_gap[solver] = {}
			avg_gap[solver][time_limit] = [g for n in cumulativos[time_limit][solver] for g, f in cumulativos[time_limit][solver][n]] 	
	
	
	
	for solver in avg_gap:

		times = list(avg_gap[solver])	
		times.sort()
		minutes = [t/60 for t in times]

		gap = [sum(avg_gap[solver][time_limit]) / len(avg_gap[solver][time_limit]) for time_limit in avg_gap[solver]]
		
	#	''' Gap x Time		
		print('Gap x Time\t', solver)
		print(minutes)
		print(gap)
		pyplot.plot(minutes, gap, label=solver, marker='.') 
	pyplot.title(f'{title} (average gap)')	
	pyplot.xlabel('Time limit (minutes)')
	pyplot.ylabel('Average percentage gap')
	pyplot.grid(True)
	pyplot.legend()
	pyplot.show()
	#	'''		 


dados, res, title = csv['sobolev']
print('Sobolev CSV data')
max_nodes = 0
instances = set()
cumulativos = {}
for solver in res:
	for time_limit in res[solver]:
		if not time_limit in cumulativos:
			cumulativos[time_limit] = {}
		cumulativos[time_limit][solver] = {}	
		for gap, nodes, file_name in res[solver][time_limit]:	
			instances.add(file_name)	
			if not nodes in cumulativos[time_limit][solver]:
				cumulativos[time_limit][solver][nodes] = []
			max_nodes = max(max_nodes, nodes)
		#	print(file_name, solver, '\t', nodes, gap)	
			cumulativos[time_limit][solver][nodes].append((gap, file_name))	

instances = len(instances)
for time_limit in cumulativos:		
	for solver in cumulativos[time_limit]:			
		nodes = list(cumulativos[time_limit][solver])
		nodes.sort()
		if not max_nodes in nodes:	
			nodes.append(max_nodes)
		if not 0 in nodes:
			nodes.insert(0,0)
		
		optimal = []
		s = 0
			
		for n in nodes:
			if n in cumulativos[time_limit][solver]:
				s += len({f for g, f in cumulativos[time_limit][solver][n] if not g}) 
			optimal.append(s * 100 / instances)
		#	''' Optimal x Nodes		
		pyplot.plot(nodes, optimal, label=solver, marker='.') 
	pyplot.title(f'{title} (gap = 0, time limit = {time_limit / 60} minutes)')	
	pyplot.xlabel('Maximum enumerated nodes')
	pyplot.ylabel('Percentage of optimal-solved instances')
	pyplot.grid(True)
	pyplot.legend()
	pyplot.show()
	#	''' 