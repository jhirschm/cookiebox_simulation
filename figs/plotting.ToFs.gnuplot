#!/usr/local/bin/gnuplot -persist
#
#    
#    	G N U P L O T
#    	Version 5.2 patchlevel 6    last modified 2019-01-01 
#    
#    	Copyright (C) 1986-1993, 1998, 2004, 2007-2018
#    	Thomas Williams, Colin Kelley and many others
#    
#    	gnuplot home:     http://www.gnuplot.info
#    	faq, bugs, etc:   type "help FAQ"
#    	immediate help:   type "help"  (plot window: hit 'h')
# set terminal x11 
# set output
unset clip points
set clip one
unset clip two
set errorbars front 1.000000 
set border 31 front lt black linewidth 1.000 dashtype solid
set zdata 
set ydata 
set xdata 
set y2data 
set x2data 
set boxwidth
set style fill  empty border
set style rectangle back fc  bgnd fillstyle   solid 1.00 border lt -1
set style circle radius graph 0.02 
set style ellipse size graph 0.05, 0.03 angle 0 units xy
set dummy t, y
set format x "% h" 
set format y "% h" 
set format x2 "% h" 
set format y2 "% h" 
set format z "% h" 
set format cb "% h" 
set format r "% h" 
set ttics format "% h"
set timefmt "%d/%m/%y,%H:%M"
set angles radians
set tics back
unset grid
set raxis
set theta counterclockwise right
set style parallel front  lt black linewidth 2.000 dashtype solid
set key title "" center
set key fixed right top vertical Right noreverse enhanced autotitle nobox
set key noinvert samplen 4 spacing 1 width 0 height 0 
set key maxcolumns 0 maxrows 0
set key noopaque
unset label
unset arrow
set style increment default
unset style line
unset style arrow
set style histogram clustered gap 2 title textcolor lt -1
unset object
set style textbox transparent margins  1.0,  1.0 border  lt -1 linewidth  1.0
set offsets 0, 0, 0, 0
set pointsize 1
set pointintervalbox 1
set encoding utf8
unset polar
unset parametric
unset decimalsign
unset micro
unset minussign
set view map scale 1
set rgbmax 255
set samples 100, 100
set isosamples 10, 10
set surface 
unset contour
set cntrlabel  format '%8.3g' font '' start 5 interval 20
set mapping cartesian
set datafile separator whitespace
unset hidden3d
set cntrparam order 4
set cntrparam linear
set cntrparam levels auto 5 unsorted
set cntrparam firstlinetype 0
set cntrparam points 5
set size ratio 0 1,1
set origin 0,0
set style data points
set style function lines
unset xzeroaxis
unset yzeroaxis
unset zzeroaxis
unset x2zeroaxis
unset y2zeroaxis
set xyplane relative 0.5
set tics scale  1, 0.5, 1, 1, 1
set mxtics default
set mytics default
set mztics default
set mx2tics default
set my2tics default
set mcbtics default
set mrtics default
set nomttics
set xtics border in scale 1,0.5 mirror norotate  autojustify
set xtics  norangelimit autofreq 
set ytics border in scale 1,0.5 mirror norotate  autojustify
set ytics  norangelimit autofreq 
set ztics border in scale 1,0.5 nomirror norotate  autojustify
set ztics  norangelimit autofreq 
unset x2tics
unset y2tics
set cbtics border in scale 1,0.5 mirror norotate  autojustify
set cbtics  norangelimit autofreq 
set rtics axis in scale 1,0.5 nomirror norotate  autojustify
set rtics  norangelimit autofreq 
unset ttics
set title "" 
set title  font "" norotate
set timestamp bottom 
set timestamp "" 
set timestamp  font "" norotate
set trange [ * : * ] noreverse nowriteback
set urange [ * : * ] noreverse nowriteback
set vrange [ * : * ] noreverse nowriteback
set xlabel "" 
set xlabel  font "" textcolor lt -1 norotate
set x2label "" 
set x2label  font "" textcolor lt -1 norotate
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "" 
set ylabel  font "" textcolor lt -1 rotate
set y2label "" 
set y2label  font "" textcolor lt -1 rotate
set yrange [ * : * ] noreverse writeback
set y2range [ * : * ] noreverse writeback
set zlabel "" 
set zlabel  font "" textcolor lt -1 norotate
set zrange [ * : * ] noreverse writeback
set cblabel "" 
set cblabel  font "" textcolor lt -1 rotate
set cbrange [ * : * ] noreverse writeback
set rlabel "" 
set rlabel  font "" textcolor lt -1 norotate
set rrange [ * : * ] noreverse writeback
unset logscale
unset jitter
set zero 1e-08
set lmargin  -1
set bmargin  -1
set rmargin  -1
set tmargin  -1
set locale "en_US.UTF-8"
set pm3d explicit at s
set pm3d scansautomatic
set pm3d interpolate 1,1 flush begin noftriangles noborder corners2color mean
set pm3d nolighting
set palette positive nops_allcF maxcolors 0 gamma 1.5 color model RGB 
set palette rgbformulae 7, 5, 15
set colorbox default
set colorbox vertical origin screen 0.9, 0.2 size screen 0.05, 0.6 front  noinvert bdefault
set style boxplot candles range  1.50 outliers pt 7 separation 1 labels auto unsorted
set loadpath 
set fontpath 
set psdir
set fit brief errorvariables nocovariancevariables errorscaling prescale nowrap v5
GNUTERM = "x11"
file = "data_fs/raw/CookieBox_ToFs.1pulses.image0044.dat"
x = 0.0
t = 0.0
## Last datafile plotted: "data_fs/raw/CookieBox_ToFs.2pulses.image0515.dat"
tof_file(n,i) = sprintf('../data_fs/raw/CookieBox_ToFs.%ipulses.image%04i.dat',n,i)
wave_file(n,i) = sprintf('../data_fs/raw/CookieBox_waveforms.%ipulses.image%04i.dat',n,i)
timeenergy_file(n,i) = sprintf('../data_fs/raw/CookieBox_timeenergy.%ipulses.image%04i.dat',n,i)
X(tof,theta) = tof*cos(theta*2.*pi/16)
Y(tof,theta) = tof*sin(theta*2.*pi/16)
set term png size 1200,1200
set output 'plotting.ToFs.log.png'
#set term post enhanced size 12in,12in color eps
#set output 'plotting.ToFs.eps'
set multiplot
set size .333,.333
set xlabel 'ToF [ns]'
set ylabel 'ToF [ns]'
set xrange [-900:900]
set yrange [-900:900]
set origin 0,.667
#set label 1 'individual electron hits' center at 500,800
set title 'individual electron hits'
plot tof_file(1,15) u (X(abs($3),$2)):(Y(abs($3),$2)) mat pt 7 notitle
set origin 0,.333
plot tof_file(2,36) u (X(abs($3),$2)):(Y(abs($3),$2)) mat pt 7 notitle
set origin 0,0
#plot tof_file(3,15) u (X(abs($3),$2)):(Y(abs($3),$2)) mat pt 7 notitle
plot tof_file(4,812) u (X(abs($3),$2)):(Y(abs($3),$2)) mat pt 7 notitle
set xrange [10:1e3]
set log x
set yrange [-.5:15.5]
set origin .667,.667
set xlabel 'ToF [ns]'
set ylabel 'channel'
unset label 1
#set label 2 'simulated waveforms' center at 800,14.5
set title 'simulated waveforms'
plot wave_file(1,15) u (($1-2e3)/10.):($2-$3) mat w lines lw 2 lc rgb 'black' notitle
set origin .667,.333
plot wave_file(2,36) u (($1-2e3)/10.):($2-$3) mat w lines lw 2 lc rgb 'black' notitle
set origin .667,0.
#plot wave_file(3,15) u (($1-2e3)/10.):($2-$3) mat w lines lw 2 lc rgb 'black' notitle
plot wave_file(4,812) u (($1-2e3)/10.):($2-$3) mat w lines lw 2 lc rgb 'black' notitle
unset log x
#set pm3d
#set view map
#set style data image
set origin .333,.667
set xlabel 'carrier scaled time [arb]'
set ylabel 'relative energy [arb]'
set cblabel 'relative intensity [arb]'
#splot timeenergy_file(1,15) mat
set style data points
set xrange [-1:8]
set yrange [-1:8]
set cbrange [0:30]
unset label 2
#set label 3 'multi-pulse energy distribution' center at 5.5,7
set title 'multi-pulse energy distribution'
plot timeenergy_file(1,15) mat u 1:(($3>2?$2:0./0)):($3/2.):3 palette pt 7 ps var notitle
set origin .333,.333
#splot timeenergy_file(2,36) mat
plot timeenergy_file(2,36) mat u 1:(($3>2?$2:0./0)):($3/2.):3 palette pt 7 ps var notitle
set origin .333,0.0
#splot timeenergy_file(3,15) mat
#plot timeenergy_file(3,15) mat u 1:(($3>2?$2:0./0)):($3/2.):3 palette pt 7 ps var notitle
plot timeenergy_file(4,812) mat u 1:(($3>2?$2:0./0)):($3/2.):3 palette pt 7 ps var notitle
unset multiplot
#    EOF
