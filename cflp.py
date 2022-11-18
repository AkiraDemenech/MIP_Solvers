
import pulp
import orloge
import sys
import time

def read_sobolev (file, prefix = 'CFLP'): 
	
	num = [ln for ln in [[(int if col.isdigit() else float)(col) for col in ln.strip().split() if not col.isalpha()] for ln in file if not ln.isspace()] if len(ln)]
	
	
				
	code = num.pop(0)[0] # primeira linha: código da instância 			
	print('\nCode:\t',code)
	dimension, fixed_cost, fixed_capacity = num.pop(0) # segunda linha
	print('Dimension:\t',dimension)
	print('Fixed cost:\t', fixed_cost)
	print('Fixed capacity:\t', fixed_capacity)
	
	I = J = range(1, 1 + dimension) # facilidades e clientes
	
	g = {i: {} for i in I} # matriz (dicionário) para os custos de transporte 
	p = {i: {} for i in I} # matriz (dicionário) para as demandas 
	
	for ln in num:
		if not len(ln):
			continue
		facility, client, transportation_cost, demand = ln
		g[facility][client] = transportation_cost
		p[facility][client] = demand
	
#	for i in I:	
	#	if len(g[i]) < len(I):
	#		print('len(g[',i,']) == ',len(g[i]))
	#	if len(p[i]) < len(I):
	#		print('len(p[',i,']) == ',len(p[i]))	
		
	prefix = f'{prefix}_{code}_{fixed_capacity}_{dimension}_{fixed_cost}'	
	cflp = pulp.LpProblem(prefix, pulp.LpMinimize)	
	
	# se a facilidade i está aberta
	y = dict((i, pulp.LpVariable(f'y_{i}', 0, 1, pulp.LpBinary)) for i in I)
	
	# se a facilidade i serve o cliente j
	x = {i: {j: pulp.LpVariable(f'x_{i}_{j}', 0, 1, pulp.LpBinary) for j in J} for i in I}
	
	for i in p:					
		cflp += pulp.lpSum(x[i][j] * p[i][j] for j in p[i]) <= y[i] * fixed_capacity # a capacidade não é superada se a facilidade for aberta 				
		
	
	for j in J:			  
		cflp += pulp.lpSum(x[i][j] for i in I if j in p[i] and p[i][j] > 0) >= 1	# demanda atendida por pelo menos uma fonte	(fonte única, pois os custos serão minimizados)		
				
	
	cflp += pulp.lpSum(fixed_cost * y[i] + pulp.lpSum(g[i][j] * x[i][j] for j in g[i]) for i in I) # função objetivo: minimizar os custos fixos das facilidades abertas e os custos de transporte para os clientes atendidos		
	
	return cflp, x, y
			
def read_mess (file, prefix = 'CFLP'):		

	data = {
			'Capacity'.upper(): [[]],
			'FixedCost'.upper(): [[]],

			'Goods'.upper(): [[]],
			'SupplyCost'.upper(): [[]],
			
			'IncompatiblePairs'.upper(): [[]]}

	key = 'Capacity'.upper()

	for ln in file:	

		lines = [k.strip() for k in ln.split(';') if len(k) > 0 and not k.isspace()] 							
		
		

		for ln in lines:

			if '=' in ln:

				key, ln = ln.split('=')
			#	print(key)
				key = key.strip().upper()

				if not key in data:
					data[key] = [[]]

			
			values = [[(int if v.strip().isdigit() else float)(v) 
				for v in ln.split('[')[-1].split(']')[0].split(',') 
				if len(v) > 0 and not v.isspace()]
					for ln in ln.split('|')]	
		#	print(values)		
			data[key][-1].extend(values.pop(0))
			data[key].extend(values)

	#print(data)		

	for k in data:
		data[k] = [ln for ln in data[k] if len(ln) > 0]

	prefix += '_' + file.name.split('/')[-1].split('\\')[-1].strip()	
	cflp = pulp.LpProblem(prefix, pulp.LpMinimize)

	f = data['FIXEDCOST'][0] # custo de abertura da facilidade
	s = data['CAPACITY'][0] # capacidade das facilidades
	d = data['GOODS'][0] # demanda dos clientes 
	c = data['SUPPLYCOST'] # custo por unidade de facilidade para cliente

	I = range(len(s)) # facilidades (Warehouses)
	J = range(len(d)) # clientes (Stores)

	# se a facilidade i está aberta
	y = {i: pulp.LpVariable(f'y_{i}', 0, 1, pulp.LpBinary) for i in I}

	# quantas unidades a facilidade i serve para o cliente j
	x = {i: {j: pulp.LpVariable(f'x_{i}_{j}', 0, cat=pulp.LpInteger) for j in J} for i in I}

	for i in I: # respeita as capacidades das facilidades abertas
		cflp += pulp.lpSum(x[i][j] for j in J) <= y[i] * s[i]

	for j in J:	# satisfaz as demandas  
		cflp += pulp.lpSum(x[i][j] for i in I) >= d[j]

	cflp += pulp.lpSum(c[j][i] * x[i][j] for i in I for j in J) + pulp.lpSum(f[i] * y[i] for i in I)

	for a, b in data['INCOMPATIBLEPAIRS']:
		a -= 1
		b -= 1
		for i in I: # disjunções 
			disj = pulp.LpVariable(f'disj_{a},{b}_{i}', cat=pulp.LpBinary)
			cflp += x[i][a] <= disj * d[j]
			cflp += x[i][b] <= (1 - disj) * d[j]

	return cflp, x, y
	


				
				

	
	
	
	
file_format = {'SOBOLEV': read_sobolev, 'MESS': read_mess}	
	
	
def problems (cap = {10, 20, 30, 40, 50}, code = range(1, 1 + 20)):				
	ilp = {} # http://www.math.nsc.ru/AP/benchmarks/CFLP/cflp_tabl-eng.html
	for ca in cap:
		ilp[ca] = {}
		for co in code:
			ilp[ca][co] = read(open(f'cap/{ca}/{co}Cap{ca}.txt','r'), open(f'Cap{ca}_{co}.py','w'))
	return ilp		

def solve (read, input, output=sys.stdout):
#	instances = problems()			
	file_name = input.split('/')[-1].split('\\')[-1]
	file_extension = file_name.split('.')[-1]
	print('\n',input,'\t',file_name)
	
	
	
	print('Instance file:\t',input, '\nExtension:\t',file_extension.lower(), file=output)
	
	
		
	instance, x, y = read(open(input,'r'))
	
	solvers = {
		'gurobi': pulp.GUROBI_CMD(logPath=file_name + '.gurobi.sol.log', msg=False), 
		'cplex': pulp.CPLEX_CMD(logPath=file_name + '.cplex.sol.log', msg=False), 		
		'scip': pulp.SCIP_CMD(options=['-l', './' + file_name + '.scip.sol.log'], msg=False, path=r'C:/Program Files/SCIPOptSuite 8.0.1/bin/scip.exe'), # colocar o caminho exato do SCIP no dispositivo que for executar 
		'pulp_cbc': pulp.PULP_CBC_CMD(logPath= file_name + '.pulp_cbc.sol.log', msg=False) # CBC precisa ser a parte final do nome do solver no dicionário e no log, sendo separado dos termos anteriores por _ ou -  
	}
	solver_logs = {}
		
	for s in solvers:
		file_log = file_name + '.' + s + '.res.log'
		solver_log = file_name + '.' + s + '.sol.log'
		sl = solver_logs[s] = {}
		print('\n\t',s)
		print('\n[%02d/%02d/%02d' %time.localtime()[:3][::-1], '%02d:%02d:%02d]\t' %time.localtime()[3:6],s.upper(), 'at', file_log, file=output)
		log = open(file_log,'w')
		
		
		ti = time.time_ns()
		pti = time.perf_counter_ns()
		res = instance.solve(solvers[s])
		ptf = time.perf_counter_ns()
		tf = time.time_ns()
		dt = (tf - ti)/(1000**3)
		pdt = (ptf - pti)/(10**9)
		tf //= (10**9)
		
		print(pulp.LpStatus[res], 'objective function value:\t', pulp.value(instance.objective),'\n',dt, 's\t',pdt,'s\nTime:\t',instance.solutionTime, '\nCPU time:\t',instance.solutionCpuTime, file=log)		
		print('[%02d/%02d/%02d' %time.localtime(tf)[:3][::-1], '%02d:%02d:%02d]\t' %time.localtime(tf)[3:6], 
					dt,'s\t',pdt,'s', '\nTime:\t',instance.solutionTime,'\nCPU time:\t',instance.solutionCpuTime, '\nObjective function value:\t',pulp.value(instance.objective),'\n',pulp.LpStatus[res], file=output)
		
	
		facilities = [i for i in y if pulp.value(y[i])]
		facilities.sort()
		
		print('\t',dt,pdt,instance.solutionTime,instance.solutionCpuTime,'\n\t',pulp.value(instance.objective), pulp.LpStatus[res],'\t',facilities)
		print(f'Facilities ({len(facilities)}):\t', facilities, '\nFacilities: assigned clients', file=output)			
		print(str(facilities).replace('[',f'Selected facilities ({len(facilities)}):\t').replace(']','\nFacilities: assigned clients'), file=log) 
		
		
		clients = {}
		supply = {}
		for i in facilities:
			print(' ',i,end=f' ({pulp.value(y[i])}) :\t',file=output)
			print(' ',i,end=f' ({pulp.value(y[i])}) :\t',file=log)
			c = []
			supply[i] = c
			for j in x[i]:
				if pulp.value(x[i][j]):
				#	print(f'x[{i}][{j}] = {pulp.value(x[i][j])}')
					if not j in clients:
						clients[j] = []
					clients[j].append(i)	
					c.append(j)						
			c.sort()		
			print(str(c).replace('[','').replace(']',''), file=log)		
			print(c, file=output)		
		J = list(clients)
		J.sort()
		print('\nClients: assigned facilities', file=log)
		print('\nClients: assigned facilities', file=output)
		for j in J:			
			clients[j].sort()
			print(' ',j,': \t',clients[j], file=output)
			print(str(clients[j]).replace('[',f' {j}: \t').replace(']',''), file=log)

		print('\nClients supply details:', file=log)
		print('\nClients supply details:', file=output)

		for j in J:			
			print(' ',j,':',file=output)
			print(f' {j}: ',file=log)

			for i in clients[j]:
				print(f'  {i}: \t{pulp.value(x[i][j])}',file=log)
				print('  ',i, ': \t', pulp.value(x[i][j]), file=output)

		print('\nFacilities capacity details:', file=log)
		print('\nFacilities capacity details:', file=output)

		for i in facilities:			
			print(' ',i,':',file=output)
			print(f' {i}: ',file=log)

			for j in supply[i]:
				print(f'  {j}: \t{pulp.value(x[i][j])}',file=log)
				print('  ',j, ': \t', pulp.value(x[i][j]), file=output)

		s = s.split('_')[-1].split('-')[-1].strip().upper()
		print('\n' + s, 'log at',solver_log,file=log)
		if s in dir(orloge.logFiles):
			sl.update(orloge.get_info_solver(solver_log, s))			
			dict_log(sl, log)
		else:	
			print(' orloge can not process\n',file=log)
		#	continue

		


	return instance, x, y, solvers, solver_logs		
		
def dict_log (log_dict, log=sys.stdout):

	print('\t' + log_dict['solver'], log_dict['version'], file=log)
	print('\t' + log_dict['status'].strip(),log_dict['status_code'],log_dict['sol_code'], file=log)
	print('\tTime:',log_dict['time'], file=log)
	print('\tRoot time:', log_dict['rootTime'], file=log)
	print('\tBest solution:', log_dict['best_solution'], file=log)
	print('\tBest bound:', log_dict['best_bound'], file=log)
	print('\tGap:',log_dict['gap'], file=log)
	print('\tNodes:',log_dict['nodes'], file=log)

	print('\tFirst relaxed:', log_dict['first_relaxed'], file=log)

	if log_dict['first_solution']:			
		print('\tFirst solution:', file=log)
		for k in log_dict['first_solution']:
			print('\t',k,':',log_dict['first_solution'][k], file=log)

	if log_dict['presolve']:			
		print('\tPresolve:', file=log)
		for k in log_dict['presolve']:
			print('\t',k,':',log_dict['presolve'][k], file=log)

	if log_dict['cut_info']:
		print('\tCut info:',file=log)
		for c in log_dict['cut_info']:
			if c == 'cuts':
				print('\t\tCuts:',file=log)
				for c in log_dict['cut_info']['cuts']:
					print('\t\t',c.strip(),':',log_dict['cut_info']['cuts'][c],file=log)
			else:
				print('\t\t' + (c.strip().replace('_',' ')) + ':\t', log_dict['cut_info'][c], file=log)

	for m in ('matrix','matrix_post'):
		if not m in log_dict:
			continue
		print('\t' + m.replace('_',' ').strip() + ':', file=log)	
		for k in log_dict[m]:
			print('\t',k.strip(), log_dict[m][k], file=log)


if __name__ == '__main__':	
	c = 2
	reading_method = file_format[sys.argv[True].upper()]
	while c < len(sys.argv):
		
		solve(reading_method, sys.argv[c], open(sys.argv[c].split('\\')[-1].split('/')[-1].strip() + '.log', 'w'))
		
		c += 1
		