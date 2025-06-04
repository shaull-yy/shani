from Bio import SeqIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
import subprocess
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

class CreatePDF:
	def __init__(self, output_path, background_ind = False):
		self.width, self.height = letter
		self.line_height = 16 
		self.image_height = 100
		self.image_width = 500
		self.y_last_written_line = self.height - 50 + self.line_height #self.y_last_written_line: keep last y coordinate fo rnext line written to the pdf
		self.font_size = 12  # Font size
		self.c = canvas.Canvas(output_path, pagesize=letter)
		self.background_ind = background_ind
		self.available_colors = {
			"red": colors.red,
			"yellow": colors.yellow,
			"blue": colors.blue,
			"green": colors.green,
			"black": colors.black,
			"white": colors.white,
			"purple": colors.purple,
			"cyan": colors.cyan,
			"magenta": colors.magenta,
			"orange": colors.orange,
			"pink": colors.pink,
			"brown": colors.brown,
			"gray": colors.gray,
			"lightgray": colors.lightgrey,
			"darkgray": colors.darkgrey,
		}
	
	def handle_position_arg(self, highlight_positions):
	#accept only list or integer as argument
		if not (isinstance(highlight_positions, list) or isinstance(highlight_positions, int)):
			print(f'Aborting - The "highlight_positions" arguments is invalid, it should be a list or an integer. \nArgument value is {highlight_positions} \n Argument type is {type(highlight_positions)}')
			sys.exit(1)
		else:
			if isinstance(highlight_positions, int):
				highlight_positions = [highlight_positions]
	#Reduce 1 from each position since python index starts from 0 not 1
		tmp_lst= []
		for num in highlight_positions:
			tmp_num = num - 1
			tmp_lst.append(tmp_num)
		return tmp_lst

	def print_string_to_pdf(self, text, highlight_positions, image_ind=False):
		x, y = 50, self.y_last_written_line
		if image_ind:
			y = y - self.image_height # - self.height 
			if y < 50:  # Start a new page if reaching bottom margin
					self.c.showPage()
					x, y = 50, self.height - 50 - self.image_height
			self.y_last_written_line = y
			image = ImageReader(plot_image_temp_file)  # Reload the image
			self.c.drawImage(image, x, y, width=self.image_width, height=self.image_height)
		else:
			highlight_positions = self.handle_position_arg(highlight_positions)
			y -= self.line_height  # advance to the next line
			if y < 50:  # Start a new page if reaching bottom margin
					self.c.showPage()
					x, y = 50, self.height - 50
					self.y_last_written_line = y
			
			font = pdfmetrics.getFont("Helvetica")
			self.c.setFont("Helvetica", self.font_size)
			
			for i, char in enumerate(text):
				if x > self.width - 50:  # Wrap text to the next line
					x = 50
					y -= self.line_height
				
				if y < 50:  # Start a new page if reaching bottom margin
					self.c.showPage()
					x, y = 50, self.height - 50
				
				char_width = self.c.stringWidth(char, "Helvetica", self.font_size)
				font_ascent = font.face.ascent * (self.font_size / 1000)  # Scale ascent by font size
				font_descent = font.face.descent * (self.font_size / 1000)  # Scale descent by font size
				char_height = font_ascent - font_descent  # Approximate character height
				#char_height = self.c._font.fontHeight(char)
				
				if i in highlight_positions:
					if self.background_ind:
						# Adjusted yellow rectangle alignment and dimensions
						self.c.setFillColor(self.available_colors["yellow"])
						rect_padding = 1
						rect_height = char_height # self.font_size # + rect_padding # * 2
						self.c.rect(
							x - rect_padding, 
							y - rect_padding, 
							char_width + rect_padding * 2, 
							rect_height, 
							fill=1, 
							stroke=0
						)
					
					self.c.setFillColor(self.available_colors["red"])
					self.c.setFont("Helvetica-Bold", self.font_size)
				else:
					self.c.setFillColor(self.available_colors["black"])
					self.c.setFont("Helvetica", self.font_size)
				
				self.c.drawString(x, y, char)
				x += char_width
			
			self.y_last_written_line = y
				
	def save_pdf(self):
		self.c.save()
	
def replace_chars(dna_seq, pos, alternate):
	if pos < 1 or pos > len(dna_seq):
		print(f'invalid postion - position value {pos} is invalid')
		return '', ''
	pos = pos - 1
#Build new string
	rslt = dna_seq[:pos] + alternate + dna_seq[pos + 1:]

# Handle the positions to be highlight (in case 'alternate' made of several chars)
	alternate_len = len(alternate)
	if alternate_len == 1:
		pos_list = pos + 1
	else:
		pos_list = []
		for k in range(1, alternate_len + 1):
			pos_list.append(pos + k)

	return rslt, pos_list


def plot_protein_vis_to_pdf(row, pdf_filename):

	# Constants
	protein_length = 905
	domains = [
		(832, 886, "zf-H2C2_2"),
		(645, 888, "STE12")
	]
	domain_colors = {
		"zf-H2C2_2": ("skyblue", 0.7),
		"STE12": ("lightgreen", 0.3)
	}
	
	# Set up plot
	fig, ax = plt.subplots(figsize=(10, 2))
	ax.set_xlim(0, protein_length)
	ax.set_ylim(0, 1)
	ax.set_xlabel("Amino acid position")
	ax.set_title("MNL1 Protein Domain Map with Mutation")
	
	# Protein backbone
	ax.hlines(0.5, 0, protein_length, color="black", linewidth=5)

	# Draw domains
	for start, end, name in domains:
		color, alpha = domain_colors.get(name, ("gray", 0.6))
		ax.add_patch(
			plt.Rectangle((start, 0.3), end-start, 0.4,color=color, edgecolor="black", alpha=alpha)
			)
		ax.text((start+end)//2, 0.75, name, ha="center", fontsize=9)

	# Mark mutation
	ax.plot(row['aa_position_protein'], 0.5, marker="v", color="red", markersize=10)
	ax.text(row['aa_position_protein'], 0.1, row['aa_position_protein'], color="red", ha="center")

	plt.tight_layout()
	#plt.show()
	print(f"Saving figure to {pdf_filename}")
#	with PdfPages(pdf_filename) as pdf:
#		pdf.savefig(fig)  # Save the figure to the PDF
#		plt.close()  # Close the plot to avoid display
	
	plt.savefig(plot_image_temp_file)
	plt.close()
	



def main_vis_func(row, plot_image_temp_file):
	sequence_title1 = f">>> Strain: {row['strain']}:"
	sequence_title2 = f">>> Has {row['SNP/indel']} mutation at position: {row['gene_position']}."
	sequence_title3 = f">>> Refence genome: {row['reference_genome']} and was changed to {row['alternative']}."
	changed_dna_sequence , highlight_positions = replace_chars(dna_sequence, row['gene_position'], row['alternative'])
	# Print DNA sequence to PDF
	create_pdf.print_string_to_pdf(' ', [])
	create_pdf.print_string_to_pdf(sequence_title1, [])
	create_pdf.print_string_to_pdf(sequence_title2, [])
	create_pdf.print_string_to_pdf(sequence_title3, [])
	create_pdf.print_string_to_pdf(changed_dna_sequence, highlight_positions)
	
	# Print Protein domain visualization to PDF
	plot_protein_vis_to_pdf(row, plot_image_temp_file)
	create_pdf.print_string_to_pdf('', [], True)

# ------------ Main  --------
pdf_output_file = "highlighted_text_by_position_dna_file.pdf"
plot_image_temp_file = "plot_temp_image.png"
input_param_file = 'C:/_Shaul/Python/_Shani/params/HIGH_IMPACT_INDLES_SNPs.xlsx'
input_dna_seq_file = 'C:/_Shaul/Python/_Shani/data/mnl1_sc5314_nt_seq.fasta'
for record in SeqIO.parse(input_dna_seq_file, "fasta"):
	rec_id = record.id
	description = record.description
	dna_sequence = record.seq

pos_df = pd.read_excel(input_param_file)

create_pdf = CreatePDF(pdf_output_file, True)
#pos_df.apply(main_vis_func, axis=1)

pos_df.apply(lambda row: main_vis_func(row, plot_image_temp_file), axis=1)

create_pdf.save_pdf()

if sys.platform.startswith("darwin"):
	subprocess.run(["open", pdf_output_file])
else:
	os.startfile(pdf_output_file)
