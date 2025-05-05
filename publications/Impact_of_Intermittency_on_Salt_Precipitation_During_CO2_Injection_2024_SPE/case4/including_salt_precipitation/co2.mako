#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "flow --newton-min-iterations=1 --relaxed-max-pv-fraction=0 --enable-tuning=true --enable-opm-rst-file=true --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99"

#Set the model parameters
model = "saltprec" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "base" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 60 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 10000 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [150] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
xfac = 7.1 #Grid cake/radial/cartesian2d/cartesian/cpg3d: exponential factor for the telescopic x-gridding (0 to use an equidistant partition)
diameter = 0.1 #Well diameter [m] 
pressure = 213 #Pressure [Bar] on the top 
temperature = [40,40] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting)
pvmult = -1 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
hysteresis = "Killough" #Add hysteresis (Killough or Carlson, 0 by default, i.e., no hysteresis)
rockcomp = 8.5e-5 #Rock compressibility [1/Bar]
saltprops = [138,268,2153] #Initial salt concentration [kg/m3], salt solubility limit [kg/m3], and precipitated salt density [kg/m3]
pcfact = 0.5 #Exponent for the capillary pressure factor (Leveret J-function) [-]

#Set the saturation functions
krw = "((sw - swi) / (1.0 - swi - sni)) ** 4.0" #Wetting rel perm saturation function [-]
krn = "(1-((sw - swi) / (1.0 - swi - sni)) ** 2.0) * (1-(sw - swi) / (1.0 - swi - sni)) ** 2" #Non-wetting rel perm saturation function [-]
pcap = "pen * (((sw - swi) / (1. - swi)) ** (-(1./npen)) - 1.) ** (1. - npen)" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-],
#7) nkrn [-], 8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog)
#11) npoints [-] (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.14,0.1,1,1,8655e-5,0.457,0.457,0.457,6e-4,0.28,10000],
[0.12,0.1,1,1,6120e-5,0.457,0.457,0.457,6e-4,0.23,10000],
[0.12,0.1,1,1,3871e-5,0.457,0.457,0.457,6e-4,0.215,10000],
[0.12,0.1,1,1,3060e-5,0.457,0.457,0.457,6e-4,0.205,10000],
[0.14,0.15,1,1,8655e-5,0.457,0.457,0.457,6e-4,0.28,10000],
[0.12,0.15,1,1,6120e-5,0.457,0.457,0.457,6e-4,0.23,10000],
[0.12,0.15,1,1,3871e-5,0.457,0.457,0.457,6e-4,0.215,10000],
[0.12,0.15,1,1,3060e-5,0.457,0.457,0.457,6e-4,0.205,10000]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[101.324,10.1324,0.2,25,25],[202.650,20.2650,0.2,25,25],[506.625,50.6625,0.2,25,25],[1013.25,101.325,0.25,25,25]]

#Set the poro-perm relationship as a function of the porosity fraction (pofa) and the properties (entry per layer)
poroperm = "((pofa - (phr - thr)) / (1 - (phr - thr))) ** gam"
popevals = [[["phr",0.35],["gam",1.75],["thr",1e-2],["npoints",1001]],
            [["phr",0.35],["gam",1.75],["thr",1e-2],["npoints",1001]],
            [["phr",0.35],["gam",1.75],["thr",1e-2],["npoints",1001]],
            [["phr",0.35],["gam",1.75],["thr",1e-2],["npoints",1001]]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day]
inj = [[5,5,0.005,1,144000],
[360,360,0.5,1,144000],
% for i,control in enumerate(schedule[1:]):
% if i == len(schedule[1:])-1:
[${tperiod},${tperiod},${0.5 if control==1 else 5},1,${control*144000.0}]]
% else:
[${tperiod},${tperiod},${0.5 if control==1 else 5},1,${control*144000.0}],
% endif
% endfor