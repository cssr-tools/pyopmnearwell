#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${flow} --enable-tuning=true --enable-opm-rst-file=true --relaxed-max-pv-fraction=0 --newton-min-iterations=1"

#Set the model parameters
model = "co2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "base" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 60 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 1000 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [200] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
xfac = 2 #Exponential factor for the telescopic x-gridding (0 to use an equidistant partition)
diameter = 0.1 #Well diameter [m]
pressure = 10 #Pressure [Bar] on the top 
temperature = [40,40] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting) 
pvmult = 1e5 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
hysteresis = "Killough" #Add hysteresis (Killough or Carlson, 0 by default, i.e., no hysteresis)
zxy = "20-20*mt.cos((2*mt.pi*x/250)) + 200*(x/1000)**2" #The function for the reservoir surface

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-], 7) nkrn [-],
#8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog) (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.14,0.1,1,1,8655e-5,2,2,2,1e-4,0],
[0.12,0.1,1,1,6120e-5,2,2,2,1e-4,0],
[0.12,0.1,1,1,3871e-5,2,2,2,1e-4,0],
[0.12,0.1,1,1,3060e-5,2,2,2,1e-4,0],
[0.14,0.2,1,1,8655e-5,2,3,2,1e-4,0],
[0.12,0.2,1,1,6120e-5,2,3,2,1e-4,0],
[0.12,0.2,1,1,3871e-5,2,3,2,1e-4,0],
[0.12,0.2,1,1,3060e-5,2,3,2,1e-4,0]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[101.324,10.1324,0.2,15,15],[202.650,20.2650,0.2,15,15],[506.625,50.6625,0.2,15,15],[1013.25,101.325,0.25,15,15]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day]
inj = [
% for i,control in enumerate(schedule):
% if i == len(schedule)-1:
[${tperiod},${tperiod},1,${control},1440000]]
% else:
[${tperiod},${tperiod},1,${control},1440000],
% endif
% endfor