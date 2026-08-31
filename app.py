import streamlit as st
import plotly.express as px
from src.agent import DataAnalystAgent
from src.db import init_demo_db, get_schema, run_readonly_sql

st.set_page_config(page_title='AI Data Analyst', page_icon='🤖', layout='wide')
st.title('🤖 AI Data Analyst Agent')
st.caption('Ask questions about sales data in plain English. Gemini generates SQL, executes it safely, and explains the result.')

init_demo_db()

with st.sidebar:
    st.header('Database')
    if st.button('Reset demo database'):
        init_demo_db(force=True)
        st.rerun()

schema = get_schema()

with st.expander('View database schema'):
    st.code(schema, language='text')

question = st.text_input('Ask a data question', placeholder='Example: What are the top 5 products by revenue?')

if st.button('Analyze', type='primary', disabled=not question.strip()):
    try:
        agent = DataAnalystAgent(schema)
        with st.spinner('Generating SQL...'):
            sql = agent.generate_sql(question)
        st.subheader('Generated SQL')
        st.code(sql, language='sql')

        with st.spinner('Executing query...'):
            df = run_readonly_sql(sql)
        if df.empty:
            st.warning('The query returned no rows.')
        else:
            st.subheader('Results')
            st.dataframe(df, use_container_width=True)

            numeric = df.select_dtypes(include='number').columns.tolist()
            categorical = [c for c in df.columns if c not in numeric]
            if len(df) > 1 and numeric and categorical:
                c1, c2 = st.columns(2)
                with c1:
                    xcol = st.selectbox('Category', categorical)
                with c2:
                    ycol = st.selectbox('Value', numeric)
                fig = px.bar(df, x=xcol, y=ycol, title=f'{ycol} by {xcol}')
                st.plotly_chart(fig, use_container_width=True)

            with st.spinner('Interpreting results...'):
                insight = agent.explain_results(question, sql, df)
            st.subheader('AI Insight')
            st.write(insight)
    except Exception as e:
        st.error(str(e))

st.divider()
st.subheader('Try these questions')
for q in [
    'What are the top 5 products by revenue?',
    'Which region generated the most revenue?',
    'Show monthly revenue.',
    'Which product category sold the most units?',
    'What is the average order value by region?',
]:
    st.write('• ' + q)
