from matplotlib import pyplot 
import pandas

comma = lambda x: int(x) if type(x) == int or x.is_integer() else ('%.02f' %x).replace('.',',')

def avg (data):
	num = [d for d in data if d == d]
	if not len(num):
		return {'Média': '--', 'Mediana': '--'}#None, None		

	j = len(num) >> 1
	i = j - (not (len(num) & 1))	
	num.sort()

	return {'Média':(sum(num) / len(num)), 'Mediana':((num[i] + num[j]) / 2)}

def open_table (f, sol, tlim):	

	tabular = len(sol) * ('|' + (len(tlim) * 'l')) 

	print(file=f, end='''
% Please add the following required packages to your document preamble:
% \\usepackage{adjustbox}
% \\usepackage{multirow}
\\begin{table}[]
	\\begin{adjustbox}{angle=90}
	\\begin{tabular}{cll''' + tabular + '''}
	& & &''')			
	print(*[' \\multicolumn{' + str(len(tlim)) + '}{c}{\\textbf{' + s + '}} ' for s in sol], sep='&', end='\t\\\\', file=f)

	print(file=f, end='Instâncias & & ')
	for s in sol:
		for t in tlim:
			print(file=f, end='& \\textbf{'+str(t)+'} ')
			
	print('\\\\', file=f)
	#print('\\hline', file=f)
def table_instance (f, sol, tlim, inst, dat):	
	width = (3 + (len(sol) * len(tlim)))
	multirow = str(sum(len(d) if type(d) == dict else 1 for d in dat))
	print('\\hline', file=f)
	print(file=f, end='\\multirow{'+multirow+'}{*}{\\textbf{'+inst+'}}')

	for d in dat:
		print(d)
		if sum((type(m) == str) for m in dat[d]): 
			print(file=f, end=' & \\multirow{'+str(len(dat[d]))+'}{*}{\\textbf{'+d.title()+'}}')	

			pref = ''
			for m in dat[d]:
				print(pref, file=f, end=' & \\textbf{'+m+'}')

				for s in sol:
					for t in tlim:
						print(end=f' & {comma(dat[d][m][s,t])}', file=f)


				print(' \\\\', file=f)
				pref = ' &'
			print('\\cline{2-'+str(width)+'}', file=f)	
		else:		
			print(file=f, end=' & \\textbf{'+ d +'} & ')	
			for s in sol:
				for t in tlim:
					print(end=f'& {comma(dat[d][s, t])} ', file=f)
			print('\\\\', file=f)		
	#print('\\hline ' * 2, file=f)	

def close_table (f):	
	print('\t\\end{tabular}\n\t\\end{adjustbox}\n\\end{table}\n',file=f)

	




csv = {}
#cbc_gap = {}
csv_file_list = []
csv_file_dir = 'eduardo'
for source_type, source_type_label in [
	('ss', 'single-source'),
	('ms', 'multi-source')
]:
	for instance_type, instance_type_label in [
		('sobolev', 'Sobolev'),
		('holmberg', 'Holmberg et al.'),
		('beasley.small', 'Beasley small'),

		('beasley.large', 'Beasley large'),
		('mess', 'MESS')				
		#('beasley', 'Beasley'),						
	]:	
		csv_file_list.append((f'{csv_file_dir}/{instance_type}.{source_type}.cflp.log.csv', f'{instance_type_label} {source_type_label}', f'{instance_type}.{source_type}'))

table = open('cflp.table.tex', 'w', encoding='UTF-8')
time_limits_subln = solvers_ln = []
tn = 0
open_table(table, solvers_ln, time_limits_subln)

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

	tn += 1

	if solvers != solvers_ln or time_limits != time_limits_subln or tn > 2:
		solvers_ln = solvers 
		time_limits_subln = time_limits
		close_table(table)
		open_table(table, solvers, time_limits)
		tn = 0
	

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

	dados = {}	

	for s in stats:
		for tl in stats[s]:

			print('\n',s,'\t',tl)

			for c in stats[s][tl]:
				print('\t',c.title(),'\t',stats[s][tl][c])
				if not c in dados:
					dados[c] = {}
				for m in stats[s][tl][c]:	
					if not m in dados[c]:	
						dados[c][m] = {}
					dados[c][m][s,tl] = stats[s][tl][c][m]	
			for d in ('\\#Opt', '\\#Fact', '\\#OfM', '\\#Total'):  		
				if not d in dados:
					dados[d] = {}
	
			dados['\\#Opt'][s, tl] = opt = sum((gap == 0) for gap in med['gap'][s, tl])
			dados['\\#Fact'][s, tl] = fact = sum((gap == gap) for gap in med['gap'][s, tl])
			dados['\\#OfM'][s, tl] = sol = sum((t != t) for t in med['time'][s, tl])
			dados['\\#Total'][s, tl] = total = len(med['time'][s, tl])
			

			print('\t#Opt\t', opt) # otimalidade
			print('\t#Fact\t', fact) # não são NaN (existe gap, existe solução)
			print('\t#OfM\t', sol) # travou nesses 
			print('\t#Total\t', total)
	#if len({dados['\\#Total'][st] for st in dados['\\#Total']}) <= 1:
	#	dados.pop('\\#Total') # excluir a linha de total se forem todos iguais 				
	#print(dados)

	table_instance(table, solvers, time_limits, instance_source_type_code, dados)			
close_table(table)
		

	 