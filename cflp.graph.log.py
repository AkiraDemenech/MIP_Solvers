from matplotlib import pyplot 
import pandas

def avg (data):
	num = [d for d in data if d == d]
	if not len(num):
		return None		

	j = len(num) >> 1
	i = j - (not (len(num) & 1))	
	num.sort()

	return (sum(num) / len(num))#, ((num[i] + num[j]) / 2)



csv = {}
#cbc_gap = {}
csv_file_list = []
csv_file_dir = 'eduardo'

latex_dir = 'doc'
img_dir = 'img'
latex = open(latex_dir + '/fig.tex', 'w')
ranking = open('rank.txt', 'w')		
rank = {}

for source_type, source_type_label in [
	('ss', 'single-source'),
	('ms', 'multi-source')
]:
	for instance_type, instance_type_label in [
		('mess', 'MESS'),
		('sobolev', 'Sobolev'),
		('holmberg', 'Holmberg et al.'),
	#	('beasley', 'Beasley'),
		('beasley.small', 'Beasley small'),
		('beasley.large', 'Beasley large')
	]:	
		csv_file_list.append((f'{csv_file_dir}/{instance_type}.{source_type}.cflp.log.csv', f'{instance_type_label} {source_type_label}', f'{instance_type}.{source_type}'))

for csv_log, title, instance_source_type_code in csv_file_list:
	print('\n', csv_log)

	try:
		dados = pandas.read_csv(open(csv_log, 'r'), sep=';', decimal=',')
	except:   	
		print('not found!')
		continue

	solvers = list(set(dados['solver']))
	solvers.sort()

	time_limits = list(set(dados['time_limit']))
	time_limits.sort()

	print('Solvers:\t', solvers, '\nTime limits:\t', time_limits)

	med = {col: {(s,t): [] for s in solvers for t in time_limits} for col in ('gap', 'time', 'nodes')}
	#print(med) #:	print('\n',col.title(),'\n', [ln for ln in dados[col] if ln != ln])						
	
	for row in range(len(dados)): 

		# nome do arquivo 
		file_name = dados['instance_source_file_name'][row]
		
		# nome do solver
		solver = dados['solver'][row]		

		# limite de tempo 
		time_limit = dados['time_limit'][row]

		# correção dos nós percorridos 		
		dados['nodes'][row] -= (solver[0] == 'G') # gurobi conta a nó raiz
		
		for col in med:
			med[col][solver, time_limit].append(dados[col][row]) 	

	rank[instance_source_type_code] = r = {} 
	print('\n',instance_source_type_code, file=ranking)

	#'''
	stats = {s: 
	  			{tl: 
       				{col: 
	    				avg(med[col][s, tl]) 
					for col in med} 
				for tl in time_limits} 
			for s in solvers}

	dados = {}	

	for s in stats:
		for tl in stats[s]:

			print(s,'\t',tl)

			for c in stats[s][tl]:
			#	print('\t',c.title(),'\t',stats[s][tl][c])
				if not c in dados:
					dados[c] = {}
				dados[c][s,tl] = stats[s][tl][c]	
			for d in ('#Opt', '#Fact', '#TL', '#OfM'):  		
				if not d in dados:
					dados[d] = {}
	
			dados['#Opt'][s, tl] = opt = sum((gap == 0) for gap in med['gap'][s, tl])
			dados['#Fact'][s, tl] = fact = sum((gap == gap) for gap in med['gap'][s, tl])
			dados['#OfM'][s, tl] = sol = sum((t != t) for t in med['time'][s, tl])
			dados['#TL'][s, tl] = tl = len(med['time'][s, tl]) - sol - fact
			

		#	print('\t#Opt\t', opt) # otimalidade
		#	print('\t#Fact\t', fact) # não são NaN (existe gap, existe solução)
		#	print('\t#TL\t', tl)
		#	print('\t#OfM\t', sol) # travou nesses	

	graph = {}
	for col in dados:
		graph[col] = g = {}	
		minutos = set()
		
		for s, tl in dados[col]:
			if not s in g:
				g[s] = {}				
			d = dados[col][s,tl]
			if d != None:
				m = tl		
				minutos.add(m)
				g[s][m] = d

		minutos = list(minutos)		
		minutos.sort()

		solvers = list(g)
		solvers.sort()

		cores = ['C2', 'C0', 'C1'] + [f'C{n}' for n in range(3,10)]

		phi = (1 + (5**.5)) / 2
		separa = 1.1

		largura = 0.2
		fig_l = 11
		fig_h = fig_l / phi#(2**.5)
		
		pyplot.figure(figsize=(fig_l,fig_h))
		for c in range(len(solvers)):	
			s = solvers[c]
			x = []
			y = []
			deslocamento = c * largura * separa
			for i in range(len(minutos)):
				m = minutos[i]
				x.append(i + deslocamento)
				y.append(g[s][m])				
			pyplot.bar_label(pyplot.bar(x, y, largura, label=s, color=cores[c]))	
		pyplot.title(f'{instance_source_type_code}: {col} x time limit (seconds)')	
		pyplot.ylabel(col)
		#pyplot.xlabel('Time limit (minutes)')
		pyplot.xticks([(j + (largura * separa)) for j in range(len(minutos))], minutos)
		#pyplot.grid(True)	
		pyplot.legend()
		#pyplot.show()	

		fig = f'res/{instance_source_type_code} - {col} x time.PDF'
		pyplot.savefig(latex_dir + '/' + img_dir + '/' + fig, bbox_inches='tight')
		pyplot.clf()

		print('\t\includegraphics[width=\\textwidth]{'+fig+'} ', file=latex)
	'''
		
	

	for col in med:
		r[col] = {}	

		for sol, tl in med[col]:			
			c = 0	
			for v in med[col][sol,tl]:				
				c += 1
				if v == v:
					if not (tl, c) in r[col]:
						r[col][tl,c] = []
					r[col][tl,c].append((v, sol))	

	
	'''
	for col in graph:
		r[col] = {}	

		for sol in graph[col]:
			for tl in graph[col][sol]:	
				if not tl in r[col]:
					r[col][tl] = []
				r[col][tl].append((graph[col][sol][tl], sol))	

		print('\n ',col,file=ranking)		
		for tl in r[col]:		
			r[col][tl].sort()
			print('\n ','\t',tl,file=ranking)
			for d, s in r[col][tl]:
				print(' ','\t\t',s,'\t',d, file=ranking)
	#	'''		


print('rank=', rank, file=open('rank.py', 'w'))					