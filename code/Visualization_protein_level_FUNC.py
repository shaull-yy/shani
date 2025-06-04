#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  5 16:43:03 2025

@author: shanilifshitz
"""

import matplotlib.pyplot as plt


def vis_protein_mut(mutation_position, strain, phenotype, ax):
	
	protein_length = 905
	mutation_label = str(mutation_position)
	
# conserved domains: list of (start, end, name)
	domains = [
		(832, 886, "zf-H2C2_2"),
		(645, 888, "STE12")
	]
	
	# Define colors per domain
	domain_colors = {
		"zf-H2C2_2": ("skyblue", 0.7),
		"STE12": ("lightgreen", 0.3)
	}
	
	
	# Plot setup
# 	fig, ax = plt.subplots(figsize=(10, 2))
	
	
	
	ax.set_xlim(0, protein_length)
	ax.set_ylim(0, 1)
	#plt.title(f"{strain}, {phenotype}")
	ax.set_title(f"{strain}, {phenotype}")

	
	ax.set_xlabel("Amino acid position")
	
	# Draw the protein backbone
	ax.hlines(0.5, 0, protein_length, color="black", linewidth=5)
	
	
	
	# Draw conserved domains with distinct colors
	for start, end, name in domains:
		color, alpha = domain_colors.get(name, ("gray", 0.6))  # default to gray if not specified
		ax.add_patch(plt.Rectangle((start, 0.3), end-start, 0.4, color=color, edgecolor="black", alpha=alpha))
		ax.text((start+end)//2, 0.75, name, ha="center", fontsize=9)
	
	
	
	# Mark the mutation
	ax.plot(mutation_position, 0.5, marker="v", color="red", markersize=10)
	ax.text(mutation_position, 0.1, mutation_label, color="red", ha="center")
	
# plt.tight_layout()
# plt.show()


if __name__ == "__main__":
	vis_protein_mut(768,"","")








