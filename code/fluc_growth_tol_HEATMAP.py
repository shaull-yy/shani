#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 07:30:41 2025

@author: shanilifshitz
"""

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sys


sys.path.append('/Users/shanilifshitz/MSc/Shani lab work/Projects/Shira/MNL1')
import Visualization_protein_level_FUNC as func



def form_standout_df(heatmap_data, phenotype):
	global outstand_df
	max_value = (heatmap_data[phenotype].max())
	lower_value = 0.87 * max_value
	
	df_temp = heatmap_data[heatmap_data[phenotype] >= lower_value].copy()
	df_temp.loc[:,'Phenotype'] = phenotype
	df_temp.rename(columns={phenotype: "Phenotype_Val"}, inplace=True)
# 	print('------------------')
# 	print(df_temp)
	outstand_df = pd.concat([outstand_df,df_temp], ignore_index=False)
# 	print('-+-+--+-+--+-+--+-+--+-+--+-+--+-+-')

# 	print(outstand_df)

outstand_df = pd.DataFrame(None)

df = pd.read_csv('/Users/shanilifshitz/MSc/Shani lab work/Projects/Shira/MNL1/FLUC_tolerance_heatmap/fluc_growth_tol.csv').set_index('file.name')


tol_phenotype =['Fluconazole_MIC',
				'Fluconazole_SMG',
				'SC_fluconazole_100uM_normalized_to_media',
				'Fluconazole_Tolerance'
				]

relevant_strains = ['SC5314', 'CEC3558', 'CEC3536', 'CEC3607', 'ext_L29358-1_P21-F7_S67', 'ext_L25759-1_P2-E2_S50', 'CEC3607',
				'CEC2018', 'ext_L29368-1_P21-G5_S77', 'ext_L25776-1_P2-F7_S67', 'ext_L25554-1_P1-C9_S33', 'CEC3536',
				'ext_L25971-1_P4-F10_S70','ext_L27644-1_P16-H2_S86', 'CEC3602','CEC3619', 'ext_L25894-1_P3-H5_S97']
control_strain = 'SC5314'


df_filtered_strains = df.loc[relevant_strains]
df_rest_strains = df.loc[~df.index.isin(relevant_strains)]
rest_means = df_rest_strains.select_dtypes(include='number')[tol_phenotype].mean()

#create new index order
new_order = [control_strain] + [s for s in df_filtered_strains.index if s != control_strain]  #why do you need to add ['file.name'] again?
df_filtered_strains = df_filtered_strains.reindex(new_order)


#creat subplots
fig, axes = plt.subplots(nrows=len(tol_phenotype), figsize=(5, len(tol_phenotype) * 3))

#generate heatmap for each phenotype
for i, phenotype in enumerate(tol_phenotype):
	heatmap_data = df_filtered_strains.select_dtypes(include='number')[[phenotype]]
	form_standout_df(heatmap_data, phenotype)
	rest_mean_value = rest_means[phenotype]
	heatmap_data.loc['REST_AVERAGE'] = rest_mean_value
	sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', cbar_kws={'label': phenotype}, ax=axes[i], yticklabels=True)
	axes[i].set_title(f'Heatmap of {phenotype}')
	axes[i].set_ylabel('Strain')

plt.tight_layout()
plt.show()


print(outstand_df)
mnl1_var_df = pd.read_excel('/Users/shanilifshitz/MSc/Shani lab work/Projects/Shira/MNL1/HIGH_IMPACT_INDLES_SNPs.xlsx')
print(mnl1_var_df.head())
outstand_df = pd.merge(outstand_df, mnl1_var_df, how="inner", left_on="file.name", right_on="strain")
print(outstand_df)
outstand_df['aa_position_protein'].apply(func.vis_protein_mut)








