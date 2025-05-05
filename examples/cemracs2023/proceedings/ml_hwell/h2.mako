<%
import math as mt
%>#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${flow} --relaxed-max-pv-fraction=0 --enable-opm-rst-file=true --newton-min-iterations=1 --enable-tuning=true"

#Set the model parameters
model = "h2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "hwell" #Template file (see src/pyopmnearwell/templates/)
grid = "cartesian2d" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 10 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 10 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [10] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
diameter = 0.15 #Well diameter [m]
pressure = 40 #Pressure [Bar] on the top 
temperature = [50,50] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting)
pvmult = 1e7 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
hysteresis = "Killough" #Add hysteresis (Killough or Carlson, 0 by default, i.e., no hysteresis)

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-],
#7) nkrn [-], 8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog)
#11) npoints [-] (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.2,0.05,1,0.75,4,2,2,1.2,1e-2,0],[0.2,0.3,1,0.75,4,2,4,1.2,1e-2,0]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[700.15,70.015,0.15,100,100]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day] (for h2store, 6) minimum BHP for producer [Bar])
inj = [
% if time == 0:
% for j in range(nseason):
% for i in range(mt.floor(timep/(tperiodi + tperiodp + tperiods))):
[${tperiodi},${tsample},1,1,${qi}],
[${tperiodi},${tsample},1,1,${qi}],
[${tperiods},${tsample},1,1,0],
% endfor
% if j == nseason - 1:
[${tperiode},${tsample},1,1,${-qp},${bhp}]]
% else:
[${tperiode},${tsample},1,1,${-qp},${bhp}],
% endif
% endfor
% else:
% for j in range(nseason-1):
% for i in range(mt.floor(timep/(tperiodi + tperiodp + tperiods))):
[${tperiodi},${tsample},1,1,${qi}],
[${tperiodi},${tsample},1,1,${qi}],
[${tperiods},${tsample},1,1,0],
% endfor
[${tperiode},${tperiodp},1,1,${-qp},${bhp}],
% endfor
% for i in range(mt.floor(time/(tperiodi + tperiodp + tperiods))):
[${tperiodi},${tsample},1,1,${qi}],
[${tperiodi},${tsample},1,1,${qi}],
% if i == mt.floor(time/(tperiodi + tperiodp + tperiods)) - 1:
[${tperiods},${tsample},1,1,0]]
% else:
[${tperiods},${tsample},1,1,0],
% endif
% endfor
% endif