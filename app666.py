"""
NoBrokerage AI Home Finder - main Streamlit app

This app is purposely robust: it falls back to a bundled sample dataset if no CSVs
are provided, explains parsed filters, and displays ranked results as cards.
"""

import os
import streamlit as st
from src.ui_components import (
    set_page_config,
    render_header,
    render_example_prompts,
    render_property_card,
    render_filter_explanations,
    render_results_summary,
    render_csv_uploader,
)
from src.nlp_parser import PropertyQueryParser
from src.search_engine import PropertySearchEngine


def main():
    set_page_config()

    st.sidebar.markdown("### NoBrokerage AI Home Finder — Developer")

    # initialize engine
    if 'engine' not in st.session_state:
        st.session_state.engine = PropertySearchEngine()

    # CSV uploader or sample
    csv_source = render_csv_uploader()
    if csv_source:
        try:
            if isinstance(csv_source, str):
                # sample path relative to app
                sample_path = os.path.join(os.path.dirname(__file__), csv_source)
                st.session_state.engine.load_csv(sample_path)
            else:
                # uploaded file-like
                st.session_state.engine.load_csv(csv_source)
        except Exception as e:
            st.sidebar.error(f"Failed to load CSV: {e}")

    render_header()

    # example prompts
    example = render_example_prompts()
    if example:
        st.session_state.user_query = example

    query = st.chat_input("Ask like — '3 BHK in Pune near Baner under 1.5 cr'")

    # also allow pressing Enter in a text_input if chat_input isn't suitable for some users
    if 'user_query' not in st.session_state:
        st.session_state.user_query = ''

    if query:
        st.session_state.user_query = query

    user_q = st.session_state.get('user_query', '')

    if user_q:
        parser = PropertyQueryParser()
        filters = parser.parse_query(user_q)

        # show how we interpreted it
        render_filter_explanations(parser.explain_filters(filters))

        # run the search
        results = st.session_state.engine.search(filters)

        # summary
        summary = st.session_state.engine.summarize_results(results, filters)
        render_results_summary(summary)

        if results:
            for r in results:
                render_property_card(r)
        else:
            st.info("No properties found. Try broader criteria or enable the sample dataset in the sidebar.")


if __name__ == '__main__':
    main()
