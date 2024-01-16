height = 100
rhog = 636
m_u = 4.8e-5
l_c = 1
r_d = .15
m_r = 10.
perm = 101.324 / 1.01324997e15
phi = 0.2
p_e = 8654.99
n_ca1 = (m_u * m_r * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
print(n_ca1)
perm = 202.650 / 1.01324997e15
phi = 0.2
p_e = 6120.00
n_ca2 = (m_u * m_r * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
print(n_ca2)
perm = 506.625 / 1.01324997e15
phi = 0.2
p_e = 3870.63
n_ca3 = (m_u * m_r * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
print(n_ca3)
perm = 1013.25 / 1.01324997e15
phi = 0.25
p_e = 3060.00
n_ca4 = (m_u * m_r * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
print(n_ca4)
print(f"mean: {(n_ca1+n_ca2+n_ca3+n_ca4)/4.}")