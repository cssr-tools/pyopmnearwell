<%
import math as mt
def mainfold(x):
    return (x ** 2) / (dic['xcorc'][-1])
%>
% for j in range(2*dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{0 + mainfold(dic['xcor'][i]):E}"} ${f"{0 +mainfold(dic['xcor'][i+1]):E} "}\
% endfor
% endfor
% for k in range(dic['nocells'][2] - 1):
% for h in range(2):
% for j in range(2*dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] + mainfold(dic['xcor'][i]):E}"} ${f"{(k+1)*dic['dims'][2]/dic['nocells'][2] +mainfold(dic['xcor'][i+1]):E} "}\
% endfor
% endfor
% endfor
% endfor
% for j in range(2*dic['nocells'][1]):
% for i in range(dic['nocells'][0]):
${f"{dic['dims'][2] + mainfold(dic['xcor'][i]):E}"} ${f"{dic['dims'][2] +mainfold(dic['xcor'][i+1]):E} "}\
% endfor
% endfor