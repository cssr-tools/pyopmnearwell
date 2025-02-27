#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${flow} --enable-opm-rst-file=true --relaxed-max-pv-fraction=0 --newton-min-iterations=1"

#Set the model parameters
model = "co2eor" #Model (co2store/co2eor/foam/h2store/saltprec)
template = "bhpcontrol" #Template file (see src/pyopmnearwell/templates/)
grid = "cartesian" #Grid type (radial/cake/cartesian2d/cartesian/cave/coord2d/coord3d/tensor2d/tensor3d)
xdim = 3500 #Length [ft] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [7] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-] 
diameter = 0.5 #Well diameter [ft]
pressure = 4000 #Pressure [Psia] on the top
injbhp = 10000 #Injector max BHP [Psia]
probhp = 1000 #Producer min BHP [Psia]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [ft], and 5) no cells in the z dir [-] (entry per layer)
rock = [[250,25,0.3,20,3],[50,50,0.3,30,3],[200,25,0.3,50,3]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [stb/day]
inj = [
% for i,control in enumerate(schedule):
% if control == 0:
% if i == len(schedule) - 1:
[${tperiod},${tperiod},1,0,${qratew}]]
% else:
[${tperiod},${tperiod},1,0,${qratew}],
% endif
% else:
% if i == len(schedule) - 1:
[${tperiod},${tperiod},1,1,${qrateg}]]
% else:
[${tperiod},${tperiod},1,1,${qrateg}],
% endif
% endif
% endfor