from matplotlib import pyplot 
import pandas

def avg (data):
	num = [d for d in data if d == d]
	if not len(num):
		return None, None		

	j = len(num) >> 1
	i = j - (not (len(num) & 1))	
	num.sort()

	return (sum(num) / len(num)), ((num[i] + num[j]) / 2)

table = open('cflp.table.tex', 'w', encoding='UTF-8')
print('''
\\begin{table}[h]
	\\centering
		\\begin{tabular}{lllllllll}	
''', file=table)

csv = {}
#cbc_gap = {}
csv_file_list = []
csv_file_dir = 'eduardo'
for source_type, source_type_label in [
	('ss', 'single-source'),
	('ms', 'multi-source')
]:
	for instance_type, instance_type_label in [
		('mess', 'MESS'),
		('sobolev', 'Sobolev'),
		('holmberg', 'Holmberg et al.'),
		('beasley', 'Beasley'),
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

	stats = {s: 
	  			{tl: 
       				{col: 
	    				avg(med[col][s, tl]) 
					for col in med} 
				for tl in time_limits} 
			for s in solvers}
		
	for s in stats:
		for tl in stats[s]:

			print('\n',s,'\t',tl)

			for c in stats[s][tl]:
				print('\t',c.title(),'\t',*stats[s][tl][c])
	
			opt = sum((gap == 0) for gap in med['gap'][s, tl])
			fact = sum((gap == gap) for gap in med['gap'][s, tl])
			sol = sum((t == t) for t in med['time'][s, tl])
			total = len(med['time'][s, tl])

			print('\t#Opt\t', opt) # otimalidade
			print('\t#Fact\t', fact) # não são NaN (existe gap, existe solução)
			print('\t#Sol\t', sol)
			print('\t#Total\t', total)
			
print('''
		\\end{tabular}	
	\\caption{Legenda}				
	\\label{tab:cflp}
\\end{table}			
''', file=table)
		

	 