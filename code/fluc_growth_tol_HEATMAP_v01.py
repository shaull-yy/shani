import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('C:/_Shaul/Python/_Shani/data/fluc_growth_tol.csv')
tol_phenotype = ['Fluconazole_MIC','Fluconazole_SMG','SC_fluconazole_100uM_normalized_to_media','Fluconazole_Tolerance']
relevant_strains = ['SC5314','CEC3558', 'CEC3536', 'CEC3607', 'ext_L29358-1_P21-F7_S67', 'ext_L25759-1_P2-E2_S50', 'CEC3607',
                    'CEC2018', 'ext_L29368-1_P21-G5_S77', 'ext_L25776-1_P2-F7_S67', 'ext_L25554-1_P1-C9_S33', 'CEC3536','ext_L25971-1_P4-F10_S70','ext_L27644-1_P16-H2_S86', 'CEC3602','CEC3619', 'ext_L25894-1_P3-H5_S97']
control_strain = 'SC5314'

df_filtered_strains = df[df['file.name'].isin(relevant_strains)].set_index('file.name')

# Create subplots
fig, axes = plt.subplots(nrows=len(tol_phenotype), figsize=(10, len(tol_phenotype) * 3))

# Loop through each phenotype and create a heatmap
for i, phenotype in enumerate(tol_phenotype):
    heatmap_data = df_filtered_strains.select_dtypes(include='number')[[phenotype]]
    
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', cbar_kws={'label': phenotype}, ax=axes[i])
    
    axes[i].set_title(f'Heatmap of {phenotype}')
    axes[i].set_xlabel('Tolerance Phenotype')
    axes[i].set_ylabel('Strain')

# Adjust layout to prevent overlapping labels
plt.tight_layout()
plt.show()
