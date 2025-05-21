import requests
from Bio import Entrez

# Set your email for NCBI API access
Entrez.email = "your_email@example.com"

def search_ncbi(sequence):
    """Search the NCBI protein database for the sequence."""
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "protein",
        "term": sequence,
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    return response.text

def analyze_sequence(sequence):
    """Analyze conserved domains and sequence length."""
    # Step 1: Search the sequence in NCBI
    search_results = search_ncbi(sequence)
    if "<Count>0</Count>" in search_results:
        print("Sequence not found in NCBI database. Proceeding with de novo analysis.")
    else:
        print("Sequence found in NCBI database.")

    # Step 2: Submit sequence to BLAST for conserved domains
    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    params = {
        "CMD": "Put",
        "DATABASE": "cdd",
        "PROGRAM": "blastp",
        "QUERY": sequence,
    }
    response = requests.post(blast_url, data=params)
    response.raise_for_status()

    # Extract RID (request ID) for follow-up
    rid = None
    for line in response.text.splitlines():
        if "RID" in line:
            rid = line.split("=")[-1].strip()
            break

    if not rid:
        raise ValueError("Failed to obtain RID for CDD search.")

    # Wait and retrieve results
    params = {
        "CMD": "Get",
        "RID": rid,
        "FORMAT_TYPE": "XML",
    }
    while True:
        response = requests.get(blast_url, params=params)
        if "Status=WAITING" not in response.text:
            break

    # Parse results
    results = response.text
    conserved_domains = []
    for line in results.splitlines():
        if "<Hit_def>" in line:
            conserved_domains.append(line.strip())

    return {
        "sequence_length": len(sequence),
        "conserved_domains": conserved_domains,
    }

# Example protein sequence (replace with your own)
sequence = "ATGGATTCACATAATAACATTGACCAATCTGTATCAGAATTGCTTCTGGATCCAGCATCA"
info = analyze_sequence(sequence)
print("Sequence Length:", info["sequence_length"])
print("Conserved Domains:", info["conserved_domains"])
