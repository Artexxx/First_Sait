def search4letters(phrase:str, letters:str="aeuoi")-> set:
	"""Return the set of 'letters' found in 'phrase' ."""
	return set(set(letters).intersection(set(phrase)))
