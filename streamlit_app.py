import streamlit as st
import streamlit.components.v1 as components

import os
import glob
import shutil

import subprocess as sp
from bs4 import BeautifulSoup

from domato.grammar import Grammar

output_dir = "./domato/test_html_files"

def increment_html_file_num():
    if st.session_state.html_file_num < st.session_state.no_of_files-1:
        st.session_state.html_file_num += 1

def decrement_html_file_num():
    if st.session_state.html_file_num > 0:
        st.session_state.html_file_num -= 1

def disable_next_button():
    if st.session_state.html_file_num >= st.session_state.no_of_files-1:
        return True
    else:
        return False

def disable_prev_button():
    if st.session_state.html_file_num <= 0:
        return True
    else:
        return False

def load_html_file(path):
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup.decode_contents()

def main():

    st.title("Fuzzy DOMs with Domato! 🍅")
    
    no_of_files = st.number_input(
        label='How many HTML files would you like to generate?',
        min_value=0,
        max_value=None,
        value=10
        )
    st.session_state.no_of_files = no_of_files

    if 'tests_generated' not in st.session_state:
        st.session_state.tests_generated = False

    custom_grammar = st.checkbox(label="Use custom grammar?")

    if custom_grammar:
        custom_grammar_string = st.text_area(
            label="Copy and paste your custom grammar here:",
            value=
"""<html> = <lt>html<gt><head><body><lt>/html<gt>
<head> = <lt>head<gt>...<lt>/head<gt>
<body> = <lt>body<gt>...<lt>/body<gt>""",
            height=100,
            placeholder="Such empty :("
            )
        try:
            custom_grammar = Grammar()
            custom_grammar.parse_from_string(custom_grammar_string)
        except Exception as e:
            st.error("Could not parse your grammar file. Please see https://github.com/googleprojectzero/domato for examples of acceptable grammars.")
            st.exception(e)

    gen_button = st.button(label='Generate Tests')

    if gen_button:
        try:
            with st.spinner("Generating tests..."):
                if custom_grammar:
                    # generate tests with custom grammar
                    for i in range(no_of_files):
                        try:
                            test_file = custom_grammar.generate_root()
                        except Exception as e:
                            st.exception(e)
                        output_path = os.path.join(output_dir, "fuzz-" + repr(i) + ".html")
                        with open(output_path,"w") as f:
                            f.write(test_file)
                else:
                    # generate tests with default Domato grammar
                    cmd = 'python domato/generator.py'
                    cmd += ' --output_dir ' + output_dir
                    cmd += ' --no_of_files ' + repr(no_of_files)
                    sp.call(cmd, shell=True)

                shutil.make_archive('domato_test_suite', 'zip', output_dir)

            html_files = glob.glob(output_dir + '**/*.html', recursive=True)
            if 'html_files' not in st.session_state:
                st.session_state.html_files = html_files

            st.success("All html files generated!")
            # st.balloons()
            st.session_state.tests_generated = True
            if 'html_file_num' not in st.session_state:
                st.session_state.html_file_num = 0
            
        except Exception as e:
            st.error("Something went wrong!")
            st.exception(e)

    if st.session_state.tests_generated:

        st.header("Fuzzed HTML Files")

        html_string = load_html_file(st.session_state.html_files[st.session_state.html_file_num])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.button('Previous', on_click=decrement_html_file_num, disabled=disable_prev_button())
        with col3:
            with open('./domato_test_suite.zip', 'rb') as f:
                st.download_button('Download All', f, file_name='domato_test_suite.zip')
        with col5:
            st.button('Next', on_click=increment_html_file_num, disabled=disable_next_button())

        components.html(
                html=html_string,
                # width=600,
                height=400,
                scrolling=True
            )

        with st.expander("See the code..."):
            st.download_button(
                label='Download',
                data=html_string,
                file_name=st.session_state.html_files[st.session_state.html_file_num]
                )
            st.write(st.session_state.html_files[st.session_state.html_file_num])
            st.code(html_string, language='html')

if __name__ == '__main__':
    main()