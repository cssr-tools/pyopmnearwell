-- Copyright (C) 2023 NORCE

SPECGRID
${dic['noCells'][0]} ${dic['noCells'][1]} ${dic['noCells'][2]} 1 F
/

COORD
% for j in range(dic['noCells'][1] + 1):
% for i in range(dic['noCells'][0] + 1):
${f"{dic['xcorc'][i] : E}"} ${f"{dic['xcorc'][j] : E}"} 0 ${f"{dic['xcorc'][i] : E}"} ${f"{dic['xcorc'][j] : E}"} ${f"{dic['dims'][2]  : E}"}
% endfor
% endfor
/

ZCORN
% for j in range(dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{0 + (dic['xcorc'][i] ** 2 + dic['xcorc'][j] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{0 + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% for i in range(dic['noCells'][0]):
 ${f"{0 + (dic['xcorc'][i] ** 2 + dic['xcorc'][j+1] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{0 + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j+1] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% endfor
% for k in range(dic['noCells'][2] - 1):
% for h in range(2):
% for j in range(dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] + (dic['xcorc'][i] ** 2 + dic['xcorc'][j] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j] ** 2)/ (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% for i in range(dic['noCells'][0]):
 ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] + (dic['xcorc'][i] ** 2 + dic['xcorc'][j+1] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{(k+1)*dic['dims'][2]/dic['noCells'][2] + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j+1] ** 2)/ (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% endfor
% endfor
% endfor
% for j in range(dic['noCells'][1]):
% for i in range(dic['noCells'][0]):
 ${f"{dic['dims'][2] + (dic['xcorc'][i] ** 2 + dic['xcorc'][j] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{dic['dims'][2] + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% for i in range(dic['noCells'][0]):
 ${f"{dic['dims'][2] + (dic['xcorc'][i] ** 2 + dic['xcorc'][j+1] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"} ${f"{dic['dims'][2] + (dic['xcorc'][i + 1] ** 2 + dic['xcorc'][j+1] ** 2) / (dic['xcorc'][-1]+dic['xcorc'][-1]): E}"}
% endfor
% endfor
/