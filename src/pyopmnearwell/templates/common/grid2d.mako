<%
import math as mt
def mainfold(x):
    return (x ** 2) / (dic['xcorc'][-1])
%>

-- Copyright (C) 2023 NORCE

SPECGRID
${dic['noCells'][0]} ${dic['noCells'][1]} ${dic['noCells'][2]} 1 F
/

COORD
% for i in range(dic['noCells'][0] + 1):
${f"{dic['xcor'][i] : E}"} ${f"{-0*0.5*dic['xcor'][1]-dic['xcor'][i]*dic['slope'] : E}"} 0 ${f"{dic['xcor'][i] : E}"} ${f"{-0*0.5*dic['xcor'][1]-dic['xcor'][i]*dic['slope'] : E}"} ${f"{dic['dims'][2]  : E}"}
% endfor
% for i in range(dic['noCells'][0] + 1):
${f"{dic['xcor'][i] : E}"} ${f"{0*0.5*dic['xcor'][1]+dic['xcor'][i]*dic['slope'] : E}"} 0 ${f"{dic['xcor'][i] : E}"} ${f"{0*0.5*dic['xcor'][1]+dic['xcor'][i]*dic['slope'] : E}"} ${f"{dic['dims'][2]  : E}"}
% endfor
/

ZCORN
% for j in range(2*dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{0 + mainfold(dic['xcor'][i]): E}"} ${f"{0 +mainfold(dic['xcor'][i+1]): E}"}
% endfor
% endfor
% for k in range(dic['noCells'][2] - 1):
% for h in range(2):
% for j in range(2*dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] + mainfold(dic['xcor'][i]): E}"} ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] +mainfold(dic['xcor'][i+1]): E}"}
% endfor
% endfor
% endfor
% endfor
% for j in range(2*dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{dic['dims'][2] + mainfold(dic['xcor'][i]): E}"} ${f"{dic['dims'][2] +mainfold(dic['xcor'][i+1]): E}"}
% endfor
% endfor
/