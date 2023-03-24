



import pulp
import orloge
import sys
import time
import traceback

'''
if time.localtime()[3] >= 18:
	exit(1) if input('Continue?').strip().upper()[0] == 'N' else print('Continue....') # nice stop
# '''

def matrix_to_vector (M):
	V = []
	for ln in M:
		V.extend(ln)
	return V	

def scan (file=sys.stdin):
	for ln in file:
		if len(ln) > 0 and not ln.isspace():
			for s in ln.strip().split():
				yield s


def read_sobolev (file, prefix = 'CFLP', single_source = True): 
	
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
	x = {i: {j: pulp.LpVariable(f'x_{i}_{j}', 0, 1, pulp.LpBinary if single_source else pulp.LpContinuous) for j in J} for i in I}
	
	for i in p:					
		cflp += pulp.lpSum(x[i][j] * p[i][j] for j in p[i]) <= y[i] * fixed_capacity # a capacidade não é superada se a facilidade for aberta 				
		
	
	for j in J:			  
		cflp += pulp.lpSum(x[i][j] for i in I if j in p[i] and p[i][j] > 0) >= 1	# demanda atendida por pelo menos uma fonte	(fonte única, pois os custos serão minimizados)		
				
	
	'''
	if single_source:
		print('Single source version')
		for i in x:
			for j in x[i]:
				cflp += x[i][j] == pulp.LpVariable(f'b_{i}_{j}', cat=pulp.LpBinary)
	# '''			

	cflp += pulp.lpSum(fixed_cost * y[i] + pulp.lpSum(g[i][j] * x[i][j] for j in g[i]) for i in I) # função objetivo: minimizar os custos fixos das facilidades abertas e os custos de transporte para os clientes atendidos		
	
	return cflp, x, y
			
def read_mess (file, prefix = 'CFLP', single_source = False, incompatible_pairs = True):		

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

	

	prefix += '_' + file.name.split('/')[-1].split('\\')[-1].strip()	
	cflp = pulp.LpProblem(prefix, pulp.LpMinimize)

	f = matrix_to_vector(data['FIXEDCOST']) # custo de abertura da facilidade
	s = matrix_to_vector(data['CAPACITY']) # capacidade das facilidades
	d = matrix_to_vector(data['GOODS']) # demanda dos clientes 
	c = [ln for ln in data['SUPPLYCOST'] if len(ln) > 0] # custo por unidade de facilidade para cliente

	for ln in c:
		if len(ln) != len(s):
			print('Wrong line\t', ln)

	'''
	with open('instance.log', 'w') as instance_log:
		print('Capacity =', s, file=instance_log)		
		print('FixedCost =', f, file=instance_log)		
		print('Goods =', d, file=instance_log)
		print('SupplyCost =', *c, sep='\n\t', file=instance_log)
		print('\nIncompatiblePairs =', data['INCOMPATIBLEPAIRS'], file=instance_log)
	#	'''

	I = range(len(s)) # facilidades (Warehouses)
	J = range(len(d)) # clientes (Stores)

	# se a facilidade i está aberta
	y = {i: pulp.LpVariable(f'y_{i}', 0, 1, pulp.LpBinary) for i in I}

	# quantas unidades a facilidade i serve para o cliente j
	x = {i: {j: ((d[j] if single_source else 1) * pulp.LpVariable(f'x_{i}_{j}', 0, cat=pulp.LpBinary if single_source else pulp.LpInteger)) for j in J} for i in I}

	for i in I: # respeita as capacidades das facilidades abertas
		cflp += pulp.lpSum(x[i][j] for j in J) <= y[i] * s[i]

	for j in J:	# satisfaz as demandas  
		scale = d[j] if single_source else 1
		cflp += pulp.lpSum(x[i][j] for i in I)/scale >= d[j]/scale

	cflp += pulp.lpSum(c[j][i] * x[i][j] for i in I for j in J) + pulp.lpSum(f[i] * y[i] for i in I)

	
	
	if incompatible_pairs:
		
		k = 0
		for p in data['INCOMPATIBLEPAIRS']:
			if len(p) != 2:
				if len(p):
					print('Wrong incompatible pair:\t',p)	

				if len(p) <= 1:	
					print('Incompatibility',p,'ignored.')
					continue

			disj = {}			
			for j in p:
				j -= 1 # índice deve começar em 0
				for i in I:				 
					disj[j,i] = pulp.LpVariable(f'disj_{i}_{j}_{k}', cat=pulp.LpBinary)
					cflp += x[i][j] <= d[j] * disj[j, i] 
			for i in I:
				cflp += pulp.lpSum(disj[j - 1, i] for j in p) <= len(p) - 1		

			k += 1
	else:		
		print('Ignoring incompatible pairs')
		
	'''	
	if single_source:
		print('Single source version')
		for i in I:
			for j in J:
				cflp += x[i][j] == pulp.LpVariable(f'b_{i}_{j}', cat=pulp.LpBinary)  
	# '''			

				

	return cflp, x, y
	
def read_beasley (file, prefix = 'CFLP', single_source = False):

	 

	prefix += '_' + file.name.split('/')[-1].split('\\')[-1].strip()	
	cflp = pulp.LpProblem(prefix, pulp.LpMinimize)

	input = scan(file)			
	m = int(next(input)) # facilidades			
	n = int(next(input)) # clientes 

	I = range(1, 1 + m) 
	J = range(1, 1 + n)

	f = {} # custo fixo da facilidade
	s = {} # capacidade da facilidade
	d = {} # demanda do cliente 
	c = {} # custo de suprir toda a demanda 

	
	x = {} # se/quanto o cliente será suprido 
	y = {} # se a facilidade está aberta 

	for i in I:
	#	print('Facilidade',i)
		s[i] = float(next(input))
		f[i] = float(next(input))
	#	print('Capacidade:',s[i])
	#	print('Custo fixo:',f[i],'\n')

		y[i] = pulp.LpVariable(f'y_{i}', cat=pulp.LpBinary)
		x[i] = {}
		c[i] = {}
		

	for j in J: # as demandas de todos os clientes primeiro
		d[j] = float(next(input))	
	#	print('Cliente',j,'\tDemanda:',d[j])
	for i in I:
		for j in J:				
		
			c[i][j] = float(next(input))
			x[i][j] = pulp.LpVariable(f'x_{i}_{j}', 0, cat=(pulp.LpBinary if single_source else pulp.LpInteger)) * (d[j] if single_source else 1) #)

	for i in I: # respeita as capacidades das facilidades abertas
		cflp += pulp.lpSum(x[i][j] for j in J) <= y[i] * s[i]

	for j in J:	# satisfaz as demandas  
		cflp += pulp.lpSum(x[i][j] for i in I) == d[j]
		scale = d[j] if single_source else 1
		cflp += pulp.lpSum(x[i][j] for i in I)/scale == d[j]/scale

	'''
	if single_source:	
		print('Single source version')
		for i in I:
			for j in J:
				cflp += pulp.LpVariable(f'b_{i}_{j}', cat=pulp.LpBinary) * d[j] == x[i][j]
	# '''			

	

	cflp += pulp.lpSum(c[i][j] * x[i][j] / d[j] for i in I for j in J) + pulp.lpSum(f[i] * y[i] for i in I)
	
	#'''
	with open('istanze.log', 'w') as instance_log:
		print('Capacity/FixedCost = \n\t', {i:(s[i], f[i]) for i in I}, file=instance_log)		
				
		print('Goods =', d, file=instance_log)
		print('TotalSupplyCost = \n\t', {(j,i): c[i][j] for i in c for j in c[i]}, file=instance_log)
		
		print('\n\n', cflp, file=instance_log)
	#'''

	return cflp, x, y
	
	
	
file_format = {'SOBOLEV': read_sobolev, 
	       'BEASLEY': read_beasley, 'HOLMBERG': read_beasley, 
		   'MESS': read_mess}	
	
	
		

def solve (read, input, outdir='', output=sys.stdout, time_limit = None, **reading_args):
#	instances = problems()			
	file_name = input.split('/')[-1].split('\\')[-1]
	file_extension = file_name.split('.')[-1]
	now = time.localtime()
	print('\n[%d/%02d/%02d' %now[:3][::-1],'%02d:%02d:%02d]\tInstance reading.... \n ' %now[3:6],input,'\t',file_name,'\t',time_limit)
	
	
	
	
	print('[%d/%02d/%02d' %now[:3][::-1],'%02d:%02d:%02d]\tReading.... \n Instance file:\t' %now[3:6],input, '\n Extension:\t',file_extension.upper(), '\n Time limit:\t', time_limit, file=output)
	
	
	ti = time.time_ns()	
	pti = time.perf_counter_ns()
	instance, x, y = read(open(input,'r'), **reading_args)
	tf = time.time_ns()
	ptf = time.perf_counter_ns()

	dt = (tf - ti) / (10**9)
	pdt = (ptf - pti) / (1000**3)
	 

	now = time.localtime(tf / (10**9))
	print('[%d/%02d/%02d' %now[:3][::-1],'%02d:%02d:%02d]\tInstance ready' %now[3:6], f'({dt}s {pdt}s)\n')
	print('[%d/%02d/%02d' %now[:3][::-1],'%02d:%02d:%02d]\tInstance ready' %now[3:6], f'({dt}s {pdt}s)\n', file=output)

	#print(instance)
	instance_name = file_name
	if len(outdir) > 0 and not outdir.isspace():
		file_name = outdir + file_name
	file_name += f'({time_limit if time_limit else ""})'
	
	#instance.writeMPS('cflp.mps')
	#print(instance, file=open('cflp.model', 'w'))

	solvers = {
		'cplex': pulp.CPLEX_CMD(logPath=file_name + '.cplex.sol.log', msg=False, timeLimit=time_limit),
		'gurobi': pulp.GUROBI_CMD(logPath=file_name + '.gurobi.sol.log', msg=False, timeLimit=time_limit), 
		
		 		
	#	'scip': pulp.SCIP_CMD(options=['-l', './' + file_name + '.scip.sol.log'], msg=False, timeLimit=time_limit, path=r'C:/Program Files/SCIPOptSuite 8.0.1/bin/scip.exe'), # colocar o caminho exato do SCIP no dispositivo que for executar 
		'pulp_cbc': pulp.PULP_CBC_CMD(logPath= file_name + '.pulp_cbc.sol.log', msg=False, timeLimit=time_limit) # CBC precisa ser a parte final do nome do solver no dicionário e no log, sendo separado dos termos anteriores por _ ou -  
	}
	solver_logs = {}
	success = False 
		
	for s in solvers:
		file_log = file_name + '.' + s + '.res.log'
		solver_log = file_name + '.' + s + '.sol.log'
		solution_list = file_name + '.' + s + '.list.log'
		solution_matrix = file_name + '.' + s + '.matrix.log'
		sl = solver_logs[s] = {}
		now = time.localtime()
		print('\n[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6],s)
		print('\n[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6],s.upper(), 'at', file_log, file=output)
		log = open(file_log,'w')
		
		
		
		try:
			ti = time.time_ns()
			pti = time.perf_counter_ns()
			res = instance.solve(solvers[s])
			ptf = time.perf_counter_ns()
			tf = time.time_ns()
			dt = (tf - ti)/(1000**3)
			pdt = (ptf - pti)/(10**9)
			tf //= (10**9)
		except Exception as error:	
			now = time.localtime()
			print('\n[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6], type(error).__name__ + ':\t', str(error), error.args, '\n',repr(error),'\n', file=output)
			print(type(error).__name__ + ':\t',str(error),error.args,'\n',repr(error),'\n', file=log)

			traceback.print_exception(error, file=output)
			traceback.print_exception(error, file=log)

			print('\n[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6], type(error).__name__ + ':\t', str(error), error.args, '\n',repr(error),'\n')
			traceback.print_exception(error)

			continue 
		success += 1

		now = time.localtime(tf)
		
		print(pulp.LpStatus[res], 'objective function value:\t', pulp.value(instance.objective),'\n',dt, 's\t',pdt,'s\nTime:\t',instance.solutionTime, '\nCPU time:\t',instance.solutionCpuTime, file=log)		
		print('[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6], 
					dt,'s\t',pdt,'s', '\nTime:\t',instance.solutionTime,'\nCPU time:\t',instance.solutionCpuTime, '\nObjective function value:\t',pulp.value(instance.objective),'\n',pulp.LpStatus[res], file=output)
		
	
		facilities = [i for i in y if pulp.value(y[i])]
		facilities.sort()
		
		print('[%02d/%02d/%02d' %now[:3][::-1], '%02d:%02d:%02d]\t' %now[3:6],dt,pdt,instance.solutionTime,instance.solutionCpuTime,'\n\t',pulp.value(instance.objective), pulp.LpStatus[res],'\t',facilities)
		print(f'Facilities ({len(facilities)}):\t', facilities, '\n\tFacilities: assigned clients', file=output)			
		print(str(facilities).replace('[',f'Selected facilities ({len(facilities)}):\t').replace(']','\nFacilities: assigned clients'), file=log) 
		
		
		clients = {}
		supply = {}
		for i in facilities:
			print('\t ',i,end=f' ({pulp.value(y[i])}) :\t',file=output)
			print(' ', i, end=f' ({pulp.value(y[i])}) :\t',file=log)
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
		print('\n\tClients: assigned facilities', file=output)
		for j in J:			
			clients[j].sort()
			print('\t ',j,': \t',clients[j], file=output)
			print(str(clients[j]).replace('[',f' {j}: \t').replace(']',''), file=log)

		print('\nClients supply details:', file=log)
		print('\n\tClients supply details:', file=output)

		for j in J:			
			print('\t ',j,':',file=output)
			print(f' {j}: ',file=log)

			for i in clients[j]:
				print(f'  {i}: \t{pulp.value(x[i][j])}',file=log)
				print('\t  ',i, ': \t', pulp.value(x[i][j]), file=output)

		print('\nFacilities capacity details:', file=log)
		print('\n\tFacilities capacity details:', file=output)

		for i in facilities:			
			print('\t ',i,':',file=output)
			print(f' {i}: ',file=log)

			for j in supply[i]:
				print(f'  {j}: \t{pulp.value(x[i][j])}',file=log)
				print('\t  ',j, ': \t', pulp.value(x[i][j]), file=output)

		print('\n', file=log)		
		list_format = [(j + 1, i + 1, pulp.value(x[i][j]) if pulp.value(x[i][j]) == None or type(pulp.value(x[i][j])) == int or not pulp.value(x[i][j]).is_integer() else int(pulp.value(x[i][j]))) for i in x for j in x[i] if pulp.value(x[i][j])]
		sol_list = open(solution_list,'w')
		print(end='{', file=sol_list)
		print(*[str(t).replace(' ', '') for t in list_format], sep=', ', end='}', file=sol_list)
		sol_list.close()
		print('(Client + 1, Facility + 1, Supply) list at', solution_list, file=log)

		matrix_format = []
		for i in x:
			for j in x[i]:
				while j >= len(matrix_format):
					matrix_format.append([])
				while i >= len(matrix_format[j]): 	
					matrix_format[j].append(0)
				matrix_format[j][i] = pulp.value(x[i][j]) if pulp.value(x[i][j]) == None or type(pulp.value(x[i][j])) == int or not pulp.value(x[i][j]).is_integer() else int(pulp.value(x[i][j]))  	

		sol_matrix = open(solution_matrix,'w')
		print(file=sol_matrix,end='[')
		print(*[str(tuple(ln)).replace(' ','') for ln in matrix_format],file=sol_matrix,end=']',sep='\n')
		sol_matrix.close()
		print('(Client + 1) Supply from (Facility + 1) matrix at', solution_matrix, file=log)
								

		s = s.split('_')[-1].split('-')[-1].strip().upper()
		print('\n' + s, 'log at',solver_log,file=log)
		if s in dir(orloge.logFiles):
			sl.update(orloge.get_info_solver(solver_log, s))			
			dict_log(sl, log)
		else:	
			print(' orloge can not process\n',file=log)
		#	continue

		
		log.close()
		
	print('End',file=output)
	print('End\n')
		


	return instance, x, y, solvers, solver_logs, success		
		
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
		if log_dict[m] == None:
			continue 
		print('\t' + m.replace('_',' ').strip() + ':', file=log)	
		for k in log_dict[m]:
			print('\t',k.strip(), log_dict[m][k], file=log)


if __name__ == '__main__':	
	
	reading_format = sys.argv[True].upper()
	reading_method = file_format[reading_format]
	optional = {}
	source = pairs = ''
	if len(sys.argv) > 4: 
		source = sys.argv[4][0].upper()
		optional['single_source'] = source != 'M'
		if len(sys.argv) > 5:
			pairs = sys.argv[5][0].upper()
			optional['incompatible_pairs'] = pairs == 'P' 
	today = time.localtime()[:5]
	folder = 'res'
	'''
	import os
	c = 0
	d = 3
	while True:
		
		try:
			os.mkdir(folder)
		except FileExistsError:	
			print('DirectoryExist:\t',folder)
		except:	
			print('Unexpected directory error')
			folder = ''
			break
		else:	
			print(folder)

		folder += '/'	
		
		if c >= len(today):
			break 
		
		b = c 
		c += d
		d -= 1
		for a in range(b, c): 	
			folder += ('_' * (b != a)) + ('%02d' %today[a])
	#'''		

	
	folder += '/' * (len(folder) > 0 and not folder[-1] in '/\\')
	last_instance_file = f'Last_{reading_format}_{"" if len(sys.argv) <= 3 else sys.argv[3]}_{source}_{pairs}.log'
	print(end=repr(sys.argv[2]), file=open(last_instance_file, 'w', encoding='utf-8'))
	
	print(sys.argv, '\n', reading_method)
	i,x,y, solvers, logs, success = solve(reading_method, sys.argv[2], folder, open(folder + sys.argv[2].split('\\')[-1].split('/')[-1].strip() + ('' if len(sys.argv) <= 3 else '('+sys.argv[3]+')') + '.log', 'w'), None if len(sys.argv) <= 3 else int(sys.argv[3]), **optional)
		
	print(sys.argv,'successfully finished' if success == len(solvers) else (((success > 0) * 'partialy ') + 'failed'),'\t',success, ':', len(solvers), file=open('cflp.log','a',encoding='utf-8'))
	print(None, file=open(last_instance_file, 'w'))	
		
		
		