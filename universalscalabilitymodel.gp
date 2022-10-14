#lambda = 995.6487801145
#delta = 0.0267159441
#kappa = 0.0007690939
lambda = 43.0622518371
delta = 1.4624384287 
kappa = 0.2373241306 
f(x) = lambda * x / (1 + delta*(x-1)+kappa*x*(x-1))
set terminal pdf
set output 'universalscalabilitymodel.pdf'
set xlabel 'N'
set ylabel 'X(N)'
#set xrange[0:32]
set xrange[0:5]
set title 'Universal Scalability Model'
plot f(x) notitle with lines
