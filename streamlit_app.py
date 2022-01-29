import streamlit as st
import streamlit.components.v1 as components

import subprocess as sp
from bs4 import BeautifulSoup
import glob

output_dir = "./domato/test_html_files"

def increment_html_file_num():
    if st.session_state.html_file_num < st.session_state.no_of_files:
        st.session_state.html_file_num += 1


def decrement_html_file_num():
    if st.session_state.html_file_num > 0:
        st.session_state.html_file_num -= 1

def main():

    st.title("Fuzzy DOMs with Domato!")

    st.text('How many HTML files would you like to generate with Domato?')
    no_of_files = st.number_input(
        label='Number of HTML files',
        min_value=0,
        max_value=None,
        value=10
        )
    st.session_state.no_of_files = no_of_files

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
            if 'html_file_num' not in st.session_state:
                st.session_state.html_file_num = 0
            
        except Exception as e:
            st.error("Something went wrong!")
            st.exception(e)

    if tests_generated:

        st.header("Fuzzed HTML Files")

        components.html(
            html=html_strings[0],
            width=500,
            height=500,
            scrolling=True
        )
        st.button('Next', on_click=increment_counter)
        st.button('Previous', on_click=decrement_counter)

        with st.expander("See HTML Code"):
            st.download_button(
                label='Download',
                data=html_strings[st.session_state.html_file_num],
                file_name=html_files[st.session_state.html_file_num]
            )
            st.code(html_strings[st.session_state.html_file_num])

if __name__ == '__main__':
    main()