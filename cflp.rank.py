from rank import rank 

rankings = {}
m = {0: {}, -1: {}}
score = {}

largura = 0

for inst in set(rank):
	for col in set(rank[inst]):
		for tl in set(rank[inst][col]):
			
			if not len(rank[inst][col][tl]):
				continue 
			r = n = []
			k = None
			rank[inst][col][tl].sort()
			for d, sol in rank[inst][col][tl]:
				if d == k:
					n.append(sol)
				else:	
					n = [sol]
					r.append(n)
				k = d	
			for n in r:
				n.sort()	
			r = tuple(tuple(n) for n in r)	
			if not r in rankings:
				print(col, tl, inst, '\t', *r)
				rankings[r] = {}
			rankings[r][col, tl, inst] = rank[inst][col][tl]

for r in rankings:			
	print('\n', *r)
	rk = list(rankings[r])
	rk.sort()
	for k in rk:
		print(*k, sep='\t')	
		
	for i in m:	
		if len(r) != 1:	
			for s in r[i]:
				if not s in m[i]:
					m[i][s] = {}
				m[i][s].update({(k[-1].split('.')[-1],) + k + ((len(r[i]),) * ((len(r[i]) > 1))): rankings[r][k] for k in rankings[r]})					

for i in m:
	print('\n\n',i)
	for sol in m[i]:
		if not sol in score:
			score[sol] = {}
		score[sol][i] = {}

		for k in m[i][sol]:
			l = len(str(k)) + len(k)
			if l > largura:
				largura = l
		print('\n\t',sol)
		rk = list(m[i][sol])
		rk.sort()
		for k in rk:
			print(*k, ' '*(largura - len(str(k))), '\t', m[i][sol][k])	
			if not k[:2] in score[sol][i]:
				score[sol][i][k[:2]] = {}
			score[sol][i][k[:2]][k[2:]] = m[i][sol][k] 	
			
for sol in score:
	for i in score[sol]:
		print()
		print(i,'\t',sol)
		colunas = list(score[sol][i])
		colunas.sort()
		for col in colunas:
			categorias = {}
			print(*col,'\t',len(score[sol][i][col]))
			for k in score[sol][i][col]:
				for c in range(len(k)):
					t = k[c]
					while type(t) == tuple and len(t) > 0:
						t = t[0]	
					if not (c, t) in categorias:
						categorias[c, t] = 0
					categorias[c, t] += 1
			cat = list(categorias)		
			cat.sort()
			for c, k in cat:			
				print(' ',k,'\t', categorias[c, k])
				pass 
