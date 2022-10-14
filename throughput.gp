set terminal pdf
set output 'throughput.pdf'
set xlabel 'Shards'
set ylabel 'Throughput (Transactions/s)'
set title 'Vitess Throughput'
plot 'throughput.dat' using 1:2 notitle with linespoints
