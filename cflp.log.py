import orloge
import csv
import os 

solvers = 'pulp_cbc', 'cplex', 'gurobi'
cut_name = {'GUROBI': {
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
	}, 'CPLEX': {
		'Clique':	'CLIQUE',
		'Cover':	'COVER',
		'Flow':	'FLOW',
		'Gomory fractional':	'GOMORY',
		'Mixed integer rounding':	'MIR',
	#	'Lift and project':	'OUTROS',#'LIFT_PROJECT',		
		'Zero-half': 'ZERO_HALF'
	
	}, 'CBC': {}
}

table = csv.writer(open('cflp.log.csv', 'w', encoding='UTF-8'), delimiter=';', quotechar="'")
concat = lambda v, p = '', sep = '': concat(v[1:], p + sep + v[0], '_') if len(v) else p
cols = [['solver'], ['instance_source_file_name'],['time_limit'],
	['time'], #['rootTime'], 
	
	
	['matrix','constraints'], 
	['matrix','variables'], 
	['matrix','nonzeros'],	 
	
	['matrix_post','constraints'],
	['matrix_post','variables'],
	['matrix_post','nonzeros'], 

	['best_solution'],
	['best_bound'],
	['gap'],
	['nodes'], # importante 
	['first_relaxed'], ['first_solution', 'BestInteger'], ['first_solution', 'CutsBestBound'], 

	['cut_info', 'best_bound'],
	['cut_info', 'best_solution'],
	['cut_info', 'time']
	
#	['cut_info'],

	]

dir = 'res'

logs = []
cuts = {}

last_index = lambda string, substring, prev_index=-1: prev_index if string.find(substring,prev_index+1) < 0 else last_index(string, substring, string.find(substring, prev_index + 1))
int_end = lambda string, end: int_end(string, end + 1) if end < len(string) and string[end].isdigit() else end
int_start = lambda string, start=0: int_start(string, start + 1) if start < len(string) and not string[start].isdigit() else start 
to_int = lambda string: int(string) if len(string) > 0 else 0
files = [(a[:int_start(a)], to_int(a[int_start(a): int_end(a, int_start(a))]), a[:last_index(a,'(')], to_int(a.split('.')[-4].split('(')[-1].split(')')[0]), a.split('.')[-3], a) for a in os.listdir(dir) if a.endswith('.sol.log')]
files.sort()

for instance_type, instance_num, file_name, time_limit, sol, log_file in files:
	
	print(repr(instance_type), instance_num, '\t', time_limit,'\t',file_name,'\t',sol)
	#log_file = f'resol/{cod}Cap{cap}.txt.{s}.sol.log'
	solver = sol.split('_')[-1].upper()
	if not solver in cut_name:
		continue 
	#print('\t',end=solver)
	log = orloge.get_info_solver(dir + '/' + log_file, solver)
	logs.append(log)
	log['instance_source_file_name'] = file_name
	log['time_limit'] = time_limit#cod
	#log['capacity'] = cap
			
	#print(log['cut_info'])
	if log['cut_info'] != None and 'cuts' in log['cut_info']:
		for c in log['cut_info']['cuts']:	

			if not c in cut_name[solver]:
				cut_name[solver][c] = c.strip().upper().replace('\t',' ').replace(' ','-').replace('-','_')
				print(solver,'Cut',c,'included!')
			
			if not cut_name[solver][c] in log['cut_info']:
				log['cut_info'][cut_name[solver][c]] = 0
					
			log['cut_info'][cut_name[solver][c]] += log['cut_info']['cuts'][c]
					
			if not c in cuts:
				cuts[c] = set()
			cuts[c].add(solver)
					

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
	print(log['solver'], '\t', log['instance_source_file_name'], log['time_limit'])
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