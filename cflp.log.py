import orloge
import csv

solvers = 'pulp_cbc', 'cplex', 'gurobi'
cut_name = {'gurobi': {
		'Clique':	'CLIQUE',
		'Cover':	'COVER',
		'Flow cover':	'FLOW',
		'Gomory':	'GOMORY',
		'MIR':	'MIR',
		'Zero half':	'ZERO_HALF',
		'Inf proof':	'OUTROS',#'INF_PROOF',
		'StrongCG':	'OUTROS',#'SCG',
		'Mod-K':	'OUTROS',#'MOD_K',
		'RLT':	'OUTROS',#'RLT',
		'Relax-and-lift':	'OUTROS'#'RELAX_LIFT'
	}, 'cplex': {
		'Clique':	'CLIQUE',
		'Cover':	'COVER',
		'Flow':	'FLOW',
		'Gomory fractional':	'GOMORY',
		'Mixed integer rounding':	'MIR',
		'Zero-half': 'ZERO_HALF',
		'Lift and project':	'OUTROS'#'LIFT_PROJECT'	
	}, 'cbc': {}
}

table = csv.writer(open('cflp.log.csv', 'w', encoding='UTF-8'), delimiter=';', quotechar="'")
concat = lambda v, p = '', sep = '': concat(v[1:], p + sep + v[0], '_') if len(v) else p
cols = [['capacity'],['code'],['solver'], 
	['time'], #['rootTime'], 
	
	
	['matrix','constraints'], 
	['matrix','variables'], 
	['matrix','nonzeros'],	# estranho 
	
	['matrix_post','constraints'],
	['matrix_post','variables'],
	['matrix_post','nonzeros'], # estranho

	['best_solution'],
	['best_bound'],
	['nodes'], # importante 
	#['first_relaxed'], ['first_solution', 'BestInteger'], ['first_solution', 'CutsBestBound'], 

	['cut_info', 'best_bound'],
	['cut_info', 'best_solution'],
	['cut_info', 'time']
	
#	['cut_info'],

	]



logs = []
cuts = {}

for cap in 10,20,30,40,50:
	print('\n\n',cap,end='')
	for cod in range(1,1 + 20):
		print('\n',cod,end='\t')
		for s in solvers:			
			log_file = f'resol/{cod}Cap{cap}.txt.{s}.sol.log'
			solver = s.split('_')[-1].upper()
			print('\t',end=solver)
			log = orloge.get_info_solver(log_file, solver)
			logs.append(log)
			log['code'] = cod
			log['capacity'] = cap
			
			#print(log['cut_info'])
			if 'cuts' in log['cut_info']:
				for c in log['cut_info']['cuts']:	

					if not cut_name[s][c] in log['cut_info']:
						log['cut_info'][cut_name[s][c]] = 0
					
					log['cut_info'][cut_name[s][c]] += log['cut_info']['cuts'][c]
					
					if not c in cuts:
						cuts[c] = set()
					cuts[c].add(s)
					

cuts_table = set()
for c in cuts:
	for s in cuts[c]:
		cuts_table.add(('cut_info', cut_name[s][c]))
cuts_table = list(cuts_table)
cuts_table.sort()
cols.extend(cuts_table)

h = [(c if type(c) == str else concat(c)) for c in cols]	
table.writerow(h)

print('\n')

for log in logs:			
	data = []
	print(log['solver'], '\t', log['capacity'], log['code'])
	for c in cols:
		l = log
		for c in c:			
			if l == None or not c in l:
				l = None
				break
			l = l[c]
		if type(l) == float:	
			l = str(l).replace('.',',')
		data.append(l)	
	#print(data)	
	table.writerow(data)	

table = None
rows = [ln.strip() for ln in open('cflp.log.csv', 'r', encoding='UTF-8').readlines()]		
table = open('cflp.log.csv', 'w', encoding='UTF-8')
for ln in rows:
	if len(ln):
		print(ln,file=table)			

print('\n',cuts)		
print('\n',cut_name)