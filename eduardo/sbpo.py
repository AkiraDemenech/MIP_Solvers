import csv
from matplotlib import pyplot, rc
rc('xtick', labelsize=18) 
rc('ytick', labelsize=18)
rc('font', size=20)

arq_graph_txt = open('sbpo.txt', 'w')

LABELS = (
	('Time', '(seconds)'),
	('Nodes', ''),
	('Gap', '(%)')
	)

GUROBI = 'GUROBI'
CPLEX = 'CPLEX'
CBC = 'CBC'

formato = 'pdf'

cores = {
	CBC:('#eeb10f', '#ff9900'),
	CPLEX:('#0c6ec1','#0066cc'),
	GUROBI:('#c61814','#cc0000')
}

for arq, cod, nome, fontes, incompatibilidade, qtd in [('mess.msi.cflp.log.csv','mess.ms.ci','MESS','MS-','-CI',20),
	('mess.ms.cflp.log.csv','mess.ms','MESS','MS-','', 20),
	('mess.ss.cflp.log.csv','mess.ss','MESS','SS-','', 20),
	
	('beasley.large.ms.cflp.log.csv','beasley.large.ms','Beasley (large)','MS-','', 12),
	('beasley.large.ss.cflp.log.csv','beasley.large.ss','Beasley (large)','SS-','', 12),
	
	('beasley.small.ms.cflp.log.csv','beasley.small.ms','Beasley (small)','MS-','', 24),
	('beasley.small.ss.cflp.log.csv','beasley.small.ss','Beasley (small)','SS-','', 24),
	
	('holmberg.ms.cflp.log.csv','holmberg.ms','Holmberg','MS-','', 71),
	('holmberg.ss.cflp.log.csv','holmberg.ss','Holmberg','SS-','', 71),
		
	('sobolev.ss.cflp.log.csv','sobolev.ss','Sobolev','SS-','', 100)]:
	
	dados = {}
	
	tab = []
	print('\n',arq)
	print(arq, '\t', cod, '\t', nome, fontes + incompatibilidade, file=arq_graph_txt)
	for ln in csv.reader(open(arq,'r'),delimiter=';'):		
		linha = []		
		
		for col in ln:
			
			if col:
				
				if col.isdigit():
					linha.append(int(col))
				
				else:	
					
					if sum(c.isalpha() for c in col):
						linha.append(col)
					
					else: 
						linha.append(float(col.replace(',','.')))
					
				
			else:	
				linha.append(None)
		 		
		if len(tab):
			
			solver = linha[SOLVER]
			time_limit = linha[TIME_LIMIT] / 60
			if time_limit.is_integer():
				time_limit = int(time_limit)
			
			time = linha[TIME]
			gap = 0 if linha[GAP] == None else linha[GAP]
			nodes = 0 if linha[NODES] == None else (linha[NODES] - (solver == GUROBI)) 
			
			
			if not time_limit in dados:
				dados[time_limit] = {}
				
			if not solver in dados[time_limit]:	
				dados[time_limit][solver] = [0,0,0, 0,0,0]
				
			dados[time_limit][solver][0] += 1	
			if time != None:
			#	print(linha)
				dados[time_limit][solver][1] += 1	
				dados[time_limit][solver][2] += (gap == 0)	
				
				dados[time_limit][solver][3] += time
				dados[time_limit][solver][4] += nodes
				dados[time_limit][solver][5] += gap
			
		else:
			cab = linha
			
			SOLVER = cab.index('solver')
			TIME_LIMIT = cab.index('time_limit')
			
			TIME = cab.index('time')	
			NODES = cab.index('nodes')
			GAP = cab.index('gap')
		#	print(cab)
			
		tab.append(linha)	
		
	limits = list(dados)
	limits.sort()	
	
	graf = {}
	for tl in limits:	
		solvers = list(dados[tl])
		solvers.sort()
		for solver in solvers:
			i,k,opt, time,nodes,gap = dados[tl][solver]
			if not solver in graf:
				graf[solver] = [], ([],[],[])
			if i < qtd:	
				print(solver,tl,'\t',i,'/',qtd,end='\t')
				if k < i:
					print('Somente',k,'factíveis',end='')
				print()	
			graf[solver][0].append((100*i/qtd,100*k/qtd,100*opt/qtd))	
			graf[solver][1][0].append(time/k)
			graf[solver][1][1].append(nodes/k)
			graf[solver][1][2].append(gap/k)
			
	solvers = list(graf)		
	solvers.sort(reverse=True)
	largura = 1 / (1 + len(solvers))
	

	arq_graph = f'Instances {cod}.{formato}'
	#arq_graph_txt = open(arq_graph + '.txt', 'w')
	print('\n', *solvers, '\t', *limits, '\n', arq_graph, file=arq_graph_txt)
	print(arq_graph, '\n', *solvers, '\t', *limits)
	t = range(len(limits))
	barras = []
	legenda = []
	for s in solvers:
	#	if sum(i > k for i,k,o in graf[s][0]): 
	#		pyplot.bar(t, [i for i,k,o in graf[s][0]], width=largura*0.6, color=cores[s][1], label=f'{s} run', hatch='//', alpha=.99)
		if sum(k > o for i,k,o in graf[s][0]): 	
			inst_descr = f'{s} fact'
			fact = [k for i,k,o in graf[s][0]]
			pyplot.bar(t, fact, width=largura*0.8, color=cores[s][1], label=inst_descr, hatch='\\', alpha=.99)
			print(end='  ',file=arq_graph_txt)
			print(inst_descr,*fact,sep='\n\t',file=arq_graph_txt)
		opt = [o for i,k,o in graf[s][0]]
		if sum(opt):
			inst_descr = f'{s} opt'
			pyplot.bar(t, opt, width=largura, color=cores[s][0], label=inst_descr)						
			print(end='  ',file=arq_graph_txt)
			print(inst_descr,*opt,sep='\n\t',file=arq_graph_txt)
		
		t = [x + largura for x in t]
	pyplot.ylabel('Instances (%)')	
	pyplot.xlabel('Time limit (minutes)')
	pyplot.xticks([t + largura * (len(solvers) - 1)/2 for t in range(len(limits))], limits)	
	pyplot.legend(loc='upper left', bbox_to_anchor=(1, 1))	
	pyplot.title(f'{fontes}CFLP{incompatibilidade} {nome} instances')
	
	pyplot.savefig(arq_graph, format=formato, bbox_inches='tight')	
	#pyplot.show()	
	pyplot.clf()
	
	for i in range(len(LABELS)):
		label, unit = LABELS[i]
		print('\t',label)

		arq_graph = f'{label} {cod}.{formato}'		
		#arq_graph_txt = open(arq_graph + '.txt', 'w')
		print('\n', arq_graph, file=arq_graph_txt)
		
		t = range(len(limits))
		
		for s in solvers:
			if sum(graf[s][1][i]):
				pyplot.bar(t, graf[s][1][i], width=largura, label=s, color=cores[s][0])
			
				#print(s,label.lower(),'\t',*graf[s][1][i], file=arq_graph_txt)
				print(end='\n  ', file=arq_graph_txt)
				print(s, *graf[s][1][i], ' ', sep='\n\t', file=arq_graph_txt)
				
				
			t = [x + largura for x in t]
		pyplot.xticks([t + largura * (len(solvers) - 1)/2 for t in range(len(limits))], limits)	
		pyplot.xlabel('Time limit (minutes)')
		pyplot.ylabel(f'{label} {unit}')
		pyplot.title(f'{fontes}CFLP{incompatibilidade} {nome} {label.lower()}')
		pyplot.legend(loc='upper left', bbox_to_anchor=(1, 1))
		pyplot.savefig(arq_graph, format=formato, bbox_inches='tight')
	#	pyplot.show()
		pyplot.clf()
		
		