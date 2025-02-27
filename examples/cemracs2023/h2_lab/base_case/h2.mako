#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${flow} --enable-tuning=true --enable-opm-rst-file=true --relaxed-max-pv-fraction=0 --newton-min-iterations=1"

#Set the model parameters
model = "h2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "nodissolution" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 60 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 2500 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [250] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
diameter = 0.25 #Well diameter [m]
pressure = 40 #Pressure [Bar] on the top 
temperature = [50,50] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting)
pvmult = 1e4 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-], 7) nkrn [-],
#8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog) (entry per layer, if hysteresis, additional entries per layer)
safu = [[0,0,1,1,0,2,2,1.2,1e-4,0]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[700.15,700.15,0.25,20,10]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day] (for h2store, 6) minimum BHP for producer [Bar])
inj = [[365,365,10,1,${200000. / 6}],
[90,90,10,1,0],
% for _,control in enumerate(schedule):
[${tperiod},${tperiod},0.1,1,${-1*qrate if control == 0 else qrate}${',3.6e1],' if control == 0 else '],'}
% endfor
[730,730,10,1,${-200000. / 6},3.6e1]]