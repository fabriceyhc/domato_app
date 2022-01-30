import streamlit as st
import streamlit.components.v1 as components

import subprocess as sp
from bs4 import BeautifulSoup
import glob
import shutil

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

    st.title("Fuzzy DOMs with Domato!")

    st.text('How many HTML files would you like to generate?')
    no_of_files = st.number_input(
        label='Number of HTML files',
        min_value=0,
        max_value=None,
        value=10
        )
    st.session_state.no_of_files = no_of_files

    if 'tests_generated' not in st.session_state:
        st.session_state.tests_generated = False

    gen_button = st.button(label='Generate Tests')

    if gen_button:
        try:
            with st.spinner("Generating tests..."):
                # generate tests
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
        
        col1, col2 = st.columns([7, 1])
        with col1:
            components.html(
                html=html_string,
                width=600,
                height=400,
                scrolling=True
            )
        with col2:
            st.button('Next', on_click=increment_html_file_num, disabled=disable_next_button())
            st.button('Previous', on_click=decrement_html_file_num, disabled=disable_prev_button())
            with open('./domato_test_suite.zip', 'rb') as f:
                st.download_button('Download All', f, file_name='domato_test_suite.zip')

        with st.expander("See HTML Code"):
            st.download_button(
                label='Download',
                data=html_string,
                file_name=st.session_state.html_files[st.session_state.html_file_num]
            )
            st.write(st.session_state.html_files[st.session_state.html_file_num])
            st.code(html_string, language='html')

if __name__ == '__main__':
    main()