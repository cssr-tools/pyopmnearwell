<%
import math as mt
def mainfold(x, y):
    return (x ** 2 + y ** 1) / (dic['xcorc'][-1]+dic['xcorc'][-1])
%>
% if dic["model"] in ["co2eor", "foam"]:
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{0 + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{0 + mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{0 + mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{0 + mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% for k in range(dic['nocells'][2] - 1):
% for h in range(2):
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{dic['zcords'][k+1] + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{dic['zcords'][k+1] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{dic['zcords'][k+1] + mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{dic['zcords'][k+1] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% endfor
% endfor
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{dic['dims'][2] + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% else:
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{0 + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{0 + mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{0 + mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{0 + mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% for k in range(dic['nocells'][2] - 1):
% for h in range(2):
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] + mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% endfor
% endfor
% for j in range(dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{dic['dims'][2] + mainfold(dic['xcorc'][i], dic['xcorc'][j]):E}"} ${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j]):E} "}\
% endfor
% for i in range(dic['nocells'][0]):
${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i], dic['xcorc'][j+1]):E}"} ${f"{dic['dims'][2] +  mainfold(dic['xcorc'][i+1], dic['xcorc'][j+1]):E} "}\
% endfor
% endfor
% endif