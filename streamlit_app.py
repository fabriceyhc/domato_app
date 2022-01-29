import streamlit as st
import streamlit.components.v1 as components

import subprocess as sp
from bs4 import BeautifulSoup
import glob

output_dir = "./domato/test_html_files"

st.text('How many html files would you like to generate with Domato?')

no_of_files = st.number_input(
	label='Number of html files',
	min_value=0,
	max_value=None,
	value=10
	)

tests_generated = False
if st.button(label='Generate Tests'):
	try:
		with st.spinner("Generating tests..."):
			# generate tests
			cmd = 'python domato/generator.py'
			cmd += ' --output_dir ' + output_dir
			cmd += ' --no_of_files ' + repr(no_of_files)
			sp.call(cmd, shell=True)

			html_files = glob.glob(output_dir + '**/*.html', recursive=True)

			html_strings = []
			for html_file in html_files:
			    with open(html_file) as fp:
			        soup = BeautifulSoup(fp, 'html.parser')
			        html_strings.append(soup.decode_contents())
		st.success("All html files generated!")
		st.balloons()
		tests_generated=True
		

	except Exception as e:
		st.error("Something went wrong!")
		st.exception(e)

if tests_generated:
	components.html(
		html=html_strings[0],
		width=500,
		height=500,
		scrolling=True
	)