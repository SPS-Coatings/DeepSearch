# import os
# import asyncio
# import streamlit as st
# from dotenv import load_dotenv
# from agno.agent import Agent
# from composio_agno import ComposioToolSet, Action
# from agno.models.together import Together

# # Load environment variables
# load_dotenv()

# # ─────────────────────────────────────────────────────────────────────────────
# #  Page config
# # ─────────────────────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="AI DeepResearch Agent",
#     page_icon="🔍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ─────────────────────────────────────────────────────────────────────────────
# #  Sidebar – API keys & info
# # ─────────────────────────────────────────────────────────────────────────────
# st.sidebar.header("⚙️ Configuration")

# together_api_key = st.sidebar.text_input(
#     "Together AI API Key",
#     value=os.getenv("TOGETHER_API_KEY", ""),
#     type="password",
#     help="Get your API key from https://together.ai"
# )

# composio_api_key = st.sidebar.text_input(
#     "Composio API Key",
#     value=os.getenv("COMPOSIO_API_KEY", ""),
#     type="password",
#     help="Get your API key from https://composio.ai"
# )

# st.sidebar.markdown("---")
# st.sidebar.markdown("### About")
# st.sidebar.info(
#     "This AI DeepResearch Agent uses Together AI's Qwen model and Composio tools to perform comprehensive research on any topic. "
#     "It generates research questions, finds answers, and compiles a professional report."
# )

# st.sidebar.markdown("### Tools Used")
# st.sidebar.markdown("- 🔍 Tavily Search")
# st.sidebar.markdown("- 🧠 Perplexity AI")
# st.sidebar.markdown("- 📄 Google Docs Integration")

# # ─────────────────────────────────────────────────────────────────────────────
# #  Session state
# # ─────────────────────────────────────────────────────────────────────────────
# if 'questions' not in st.session_state:
#     st.session_state.questions = []
# if 'question_answers' not in st.session_state:
#     st.session_state.question_answers = []
# if 'report_content' not in st.session_state:
#     st.session_state.report_content = ""
# if 'research_complete' not in st.session_state:
#     st.session_state.research_complete = False

# # ─────────────────────────────────────────────────────────────────────────────
# #  Title
# # ─────────────────────────────────────────────────────────────────────────────
# st.title("🔍 AI DeepResearch Agent with Agno and Composio")

# # ─────────────────────────────────────────────────────────────────────────────
# #  Helper functions
# # ─────────────────────────────────────────────────────────────────────────────
# def initialize_agents(together_key, composio_key):
#     llm = Together(id="Qwen/Qwen3-235B-A22B-fp8-tput", api_key=together_key)

#     toolset = ComposioToolSet(api_key=composio_key)
#     composio_tools = toolset.get_tools(actions=[
#         Action.COMPOSIO_SEARCH_TAVILY_SEARCH,
#         Action.PERPLEXITYAI_PERPLEXITY_AI_SEARCH,
#         Action.GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN
#     ])
#     return llm, composio_tools


# def create_agents(llm, composio_tools):
#     return Agent(
#         name="Question Generator",
#         model=llm,
#         instructions="""
#         You are an expert at breaking down research topics into specific questions.
#         Generate exactly 5 specific yes/no research questions about the given topic in the specified domain.
#         Respond ONLY with the text of the 5 questions formatted as a numbered list, and NOTHING ELSE.
#         """
#     )


# def extract_questions_after_think(text: str) -> str:
#     if "</think>" in text:
#         return text.split("</think>", 1)[1].strip()
#     return text.strip()


# def generate_questions(llm, composio_tools, topic, domain):
#     question_generator = create_agents(llm, composio_tools)
#     with st.spinner("🤖 Generating research questions..."):
#         questions_task = question_generator.run(
#             f"Generate exactly 5 specific yes/no research questions about the topic '{topic}' in the domain '{domain}'."
#         )
#         questions_text = questions_task.content
#         questions_only = extract_questions_after_think(questions_text)
#         questions_list = [q.strip() for q in questions_only.split('\n') if q.strip()]
#         st.session_state.questions = questions_list
#         return questions_list


# def research_question(llm, composio_tools, topic, domain, question):
#     research_task = Agent(
#         model=llm,
#         tools=[composio_tools],
#         instructions=(
#             f"You are a sophisticated research assistant. Answer the following research question "
#             f"about the topic '{topic}' in the domain '{domain}':\n\n{question}\n\n"
#             "Use the PERPLEXITYAI_PERPLEXITY_AI_SEARCH and COMPOSIO_SEARCH_TAVILY_SEARCH tools "
#             "to provide a concise, well-sourced answer."
#         )
#     )
#     research_result = research_task.run()
#     return research_result.content


# def compile_report(llm, composio_tools, topic, domain, question_answers):
#     with st.spinner("📝 Compiling final report and creating Google Doc..."):
#         qa_sections = "\n".join(
#             f"<h2>{idx+1}. {qa['question']}</h2>\n<p>{qa['answer']}</p>"
#             for idx, qa in enumerate(question_answers)
#         )
#         compile_report_task = Agent(
#             name="Report Compiler",
#             model=llm,
#             tools=[composio_tools],
#             instructions=f"""
#             You are a sophisticated research assistant. Compile the following research findings into a professional, McKinsey-style report. The report should be structured as follows:

#             1. Executive Summary/Introduction: Briefly introduce the topic and domain, and summarize the key findings.
#             2. Research Analysis: For each research question, create a section with a clear heading and provide a detailed, analytical answer. Do NOT use a Q&A format; instead, weave the answer into a narrative and analytical style.
#             3. Conclusion/Implications: Summarize the overall insights and implications of the research.

#             Use clear, structured HTML for the report.

#             Topic: {topic}
#             Domain: {domain}

#             Research Questions and Findings (for your reference):
#             {qa_sections}

#             Use the GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN tool to create a Google Doc with the report. The text should be in HTML format. You have to create the google document with all the compiled info. You have to do it.
#             """
#         )
#         compile_result = compile_report_task.run()
#         st.session_state.report_content = compile_result.content
#         st.session_state.research_complete = True
#         return compile_result.content

# # ─────────────────────────────────────────────────────────────────────────────
# #  Main app logic
# # ─────────────────────────────────────────────────────────────────────────────
# if together_api_key and composio_api_key:
#     llm, composio_tools = initialize_agents(together_api_key, composio_api_key)

#     st.header("Research Topic")

#     col1, col2 = st.columns(2)
#     with col1:
#         topic = st.text_input("What topic would you like to research?", placeholder="American Tariffs")
#     with col2:
#         domain = st.text_input("What domain is this topic in?", placeholder="Politics, Economics, Technology, etc.")

#     if topic and domain and st.button("Generate Research Questions", key="generate_questions"):
#         questions = generate_questions(llm, composio_tools, topic, domain)
#         st.header("Research Questions")
#         for i, question in enumerate(questions):
#             st.markdown(f"**{i+1}. {question}**")

#     if st.session_state.questions and st.button("Start Research", key="start_research"):
#         st.header("Research Results")
#         question_answers = []
#         progress_bar = st.progress(0)

#         for i, question in enumerate(st.session_state.questions):
#             progress_bar.progress(i / len(st.session_state.questions))
#             with st.spinner(f"🔍 Researching question {i+1}..."):
#                 answer = research_question(llm, composio_tools, topic, domain, question)
#                 question_answers.append({"question": question, "answer": answer})

#             st.subheader(f"Question {i+1}:")
#             st.markdown(f"**{question}**")
#             st.markdown(answer)
#             progress_bar.progress((i + 1) / len(st.session_state.questions))

#         st.session_state.question_answers = question_answers

#         if st.button("Compile Final Report", key="compile_report"):
#             report_content = compile_report(llm, composio_tools, topic, domain, question_answers)
#             st.header("Final Report")
#             st.success("Your report has been compiled and a Google Doc has been created.")

#             with st.expander("View Full Report Content", expanded=True):
#                 st.markdown(report_content, unsafe_allow_html=True)   # ← render HTML

#     if len(st.session_state.question_answers) > 0 and not st.session_state.research_complete:
#         st.header("Previous Research Results")
#         for i, qa in enumerate(st.session_state.question_answers):
#             with st.expander(f"Question {i+1}: {qa['question']}"):
#                 st.markdown(qa['answer'])

#     if st.session_state.research_complete and st.session_state.report_content:
#         st.header("Final Report")
#         st.success("Your report has been compiled and a Google Doc has been created.")
#         with st.expander("View Full Report Content", expanded=True):
#             st.markdown(st.session_state.report_content, unsafe_allow_html=True)  # ← render HTML

# else:
#     st.warning("⚠️ Please enter your Together AI and Composio API keys in the sidebar to get started.")

#     st.header("How It Works")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.subheader("1️⃣ Define Topic")
#         st.write("Enter your research topic and domain to begin the research process.")
#     with col2:
#         st.subheader("2️⃣ Generate Questions")
#         st.write("The AI generates specific research questions to explore your topic in depth.")
#     with col3:
#         st.subheader("3️⃣ Compile Report")
#         st.write("Research findings are compiled into a professional report and saved to Google Docs.")








# import os
# import asyncio
# import streamlit as st
# from dotenv import load_dotenv
# from agno.agent import Agent
# from composio_agno import ComposioToolSet, Action
# from agno.models.together import Together

# # Load environment variables
# load_dotenv()

# # ─────────────────────────────────────────────────────────────────────────────
# #  Page config
# # ─────────────────────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="AI DeepResearch Agent",
#     page_icon="🔍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ─────────────────────────────────────────────────────────────────────────────
# #  Sidebar – API keys & info
# # ─────────────────────────────────────────────────────────────────────────────
# st.sidebar.header("⚙️ Configuration")

# together_api_key = st.sidebar.text_input(
#     "Together AI API Key",
#     value=os.getenv("TOGETHER_API_KEY", ""),
#     type="password",
#     help="Get your API key from https://together.ai"
# )

# composio_api_key = st.sidebar.text_input(
#     "Composio API Key",
#     value=os.getenv("COMPOSIO_API_KEY", ""),
#     type="password",
#     help="Get your API key from https://composio.ai"
# )

# st.sidebar.markdown("---")
# st.sidebar.markdown("### About")
# st.sidebar.info(
#     "This AI DeepResearch Agent uses Together AI's Qwen model and Composio tools to perform comprehensive research on any topic. "
#     "It generates research questions, finds answers, and compiles a professional report."
# )

# st.sidebar.markdown("### Tools Used")
# st.sidebar.markdown("- 🔍 Tavily Search")
# st.sidebar.markdown("- 🧠 Perplexity AI")
# st.sidebar.markdown("- 📄 Google Docs Integration")

# # ─────────────────────────────────────────────────────────────────────────────
# #  Session state
# # ─────────────────────────────────────────────────────────────────────────────
# if 'questions' not in st.session_state:
#     st.session_state.questions = []
# if 'question_answers' not in st.session_state:
#     st.session_state.question_answers = []
# if 'report_content' not in st.session_state:
#     st.session_state.report_content = ""
# if 'research_complete' not in st.session_state:
#     st.session_state.research_complete = False
# if 'summary_content' not in st.session_state:                       # ← new
#     st.session_state.summary_content = ""

# # ─────────────────────────────────────────────────────────────────────────────
# #  Title
# # ─────────────────────────────────────────────────────────────────────────────
# st.title("🔍 AI DeepResearch Agent with Agno and Composio")

# # ─────────────────────────────────────────────────────────────────────────────
# #  Helper functions
# # ─────────────────────────────────────────────────────────────────────────────
# def initialize_agents(together_key, composio_key):
#     llm = Together(id="Qwen/Qwen3-235B-A22B-fp8-tput", api_key=together_key)

#     toolset = ComposioToolSet(api_key=composio_key)
#     composio_tools = toolset.get_tools(actions=[
#         Action.COMPOSIO_SEARCH_TAVILY_SEARCH,
#         Action.PERPLEXITYAI_PERPLEXITY_AI_SEARCH,
#         Action.GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN
#     ])
#     return llm, composio_tools


# def create_agents(llm, composio_tools):
#     return Agent(
#         name="Question Generator",
#         model=llm,
#         instructions="""
#         You are an expert at breaking down research topics into specific questions.
#         Generate exactly 5 specific yes/no research questions about the given topic in the specified domain.
#         Respond ONLY with the text of the 5 questions formatted as a numbered list, and NOTHING ELSE.
#         """
#     )


# def extract_questions_after_think(text: str) -> str:
#     if "</think>" in text:
#         return text.split("</think>", 1)[1].strip()
#     return text.strip()


# def generate_questions(llm, composio_tools, topic, domain):
#     question_generator = create_agents(llm, composio_tools)
#     with st.spinner("🤖 Generating research questions..."):
#         questions_task = question_generator.run(
#             f"Generate exactly 5 specific yes/no research questions about the topic '{topic}' in the domain '{domain}'."
#         )
#         questions_text = questions_task.content
#         questions_only = extract_questions_after_think(questions_text)
#         questions_list = [q.strip() for q in questions_only.split('\n') if q.strip()]
#         st.session_state.questions = questions_list
#         return questions_list


# def research_question(llm, composio_tools, topic, domain, question):
#     research_task = Agent(
#         model=llm,
#         tools=[composio_tools],
#         instructions=(
#             f"You are a sophisticated research assistant. Answer the following research question "
#             f"about the topic '{topic}' in the domain '{domain}':\n\n{question}\n\n"
#             "Use the PERPLEXITYAI_PERPLEXITY_AI_SEARCH and COMPOSIO_SEARCH_TAVILY_SEARCH tools "
#             "to provide a concise, well-sourced answer."
#         )
#     )
#     research_result = research_task.run()
#     return research_result.content


# # ────────────────────────── NEW: Search-Summary Agent helper ─────────────────
# def generate_summary(llm, topic, domain, question_answers):
#     summary_agent = Agent(
#         name="Search Summary Agent",
#         model=llm,
#         instructions=(
#             "You are a senior research editor. You will be given a set of question–answer pairs "
#             "spanning a topic and domain. Write a cohesive executive summary (≈300-400 words) "
#             "that synthesises key insights, avoids Q&A formatting, and reads like a polished memo. "
#             "Use markdown—paragraphs plus bullet points where useful."
#         )
#     )
#     qa_blob = "\n\n".join(
#         f"Q: {qa['question']}\nA: {qa['answer']}" for qa in question_answers
#     )
#     summary_result = summary_agent.run(
#         f"Topic: {topic}\nDomain: {domain}\n\n{qa_blob}"
#     )
#     return summary_result.content
# # ─────────────────────────────────────────────────────────────────────────────


# def compile_report(llm, composio_tools, topic, domain, question_answers):
#     with st.spinner("📝 Compiling final report and creating Google Doc..."):
#         qa_sections = "\n".join(
#             f"<h2>{idx+1}. {qa['question']}</h2>\n<p>{qa['answer']}</p>"
#             for idx, qa in enumerate(question_answers)
#         )
#         compile_report_task = Agent(
#             name="Report Compiler",
#             model=llm,
#             tools=[composio_tools],
#             instructions=f"""
#             You are a sophisticated research assistant. Compile the following research findings into a professional, McKinsey-style report. The report should be structured as follows:

#             1. Executive Summary/Introduction: Briefly introduce the topic and domain, and summarize the key findings.
#             2. Research Analysis: For each research question, create a section with a clear heading and provide a detailed, analytical answer. Do NOT use a Q&A format; instead, weave the answer into a narrative and analytical style.
#             3. Conclusion/Implications: Summarize the overall insights and implications of the research.

#             Use clear, structured HTML for the report.

#             Topic: {topic}
#             Domain: {domain}

#             Research Questions and Findings (for your reference):
#             {qa_sections}

#             Use the GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN tool to create a Google Doc with the report. The text should be in HTML format. You have to create the google document with all the compiled info. You have to do it.
#             """
#         )
#         compile_result = compile_report_task.run()
#         st.session_state.report_content = compile_result.content
#         st.session_state.research_complete = True
#         return compile_result.content

# # ─────────────────────────────────────────────────────────────────────────────
# #  Main app logic
# # ─────────────────────────────────────────────────────────────────────────────
# if together_api_key and composio_api_key:
#     llm, composio_tools = initialize_agents(together_api_key, composio_api_key)

#     st.header("Research Topic")

#     col1, col2 = st.columns(2)
#     with col1:
#         topic = st.text_input("What topic would you like to research?", placeholder="American Tariffs")
#     with col2:
#         domain = st.text_input("What domain is this topic in?", placeholder="Politics, Economics, Technology, etc.")

#     if topic and domain and st.button("Generate Research Questions", key="generate_questions"):
#         questions = generate_questions(llm, composio_tools, topic, domain)
#         st.header("Research Questions")
#         for i, question in enumerate(questions):
#             st.markdown(f"**{i+1}. {question}**")

#     if st.session_state.questions and st.button("Start Research", key="start_research"):
#         st.header("Research Results")
#         question_answers = []
#         progress_bar = st.progress(0)

#         for i, question in enumerate(st.session_state.questions):
#             progress_bar.progress(i / len(st.session_state.questions))
#             with st.spinner(f"🔍 Researching question {i+1}..."):
#                 answer = research_question(llm, composio_tools, topic, domain, question)
#                 question_answers.append({"question": question, "answer": answer})

#             st.subheader(f"Question {i+1}:")
#             st.markdown(f"**{question}**")
#             st.markdown(answer)
#             progress_bar.progress((i + 1) / len(st.session_state.questions))

#         st.session_state.question_answers = question_answers

#         # ──────────────── call Search-Summary Agent & display ────────────────
#         summary = generate_summary(llm, topic, domain, question_answers)
#         st.session_state.summary_content = summary
#         st.markdown("---")
#         st.subheader("🔎 Search Summary")
#         st.markdown(summary, unsafe_allow_html=True)
#         # ─────────────────────────────────────────────────────────────────────

#         if st.button("Compile Final Report", key="compile_report"):
#             report_content = compile_report(llm, composio_tools, topic, domain, question_answers)
#             st.header("Final Report")
#             st.success("Your report has been compiled and a Google Doc has been created.")

#             with st.expander("View Full Report Content", expanded=True):
#                 st.markdown(report_content, unsafe_allow_html=True)   # ← render HTML

#     if len(st.session_state.question_answers) > 0 and not st.session_state.research_complete:
#         st.header("Previous Research Results")
#         for i, qa in enumerate(st.session_state.question_answers):
#             with st.expander(f"Question {i+1}: {qa['question']}"):
#                 st.markdown(qa['answer'])
#         if st.session_state.summary_content:
#             st.subheader("🔎 Search Summary")
#             st.markdown(st.session_state.summary_content, unsafe_allow_html=True)

#     if st.session_state.research_complete and st.session_state.report_content:
#         st.header("Final Report")
#         st.success("Your report has been compiled and a Google Doc has been created.")
#         with st.expander("View Full Report Content", expanded=True):
#             st.markdown(st.session_state.report_content, unsafe_allow_html=True)  # ← render HTML

# else:
#     st.warning("⚠️ Please enter your Together AI and Composio API keys in the sidebar to get started.")

#     st.header("How It Works")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.subheader("1️⃣ Define Topic")
#         st.write("Enter your research topic and domain to begin the research process.")
#     with col2:
#         st.subheader("2️⃣ Generate Questions")
#         st.write("The AI generates specific research questions to explore your topic in depth.")
#     with col3:
#         st.subheader("3️⃣ Compile Report")
#         st.write("Research findings are compiled into a professional report and saved to Google Docs.")





# ai_deepresearch_agent.py  –  run with:  streamlit run ai_deepresearch_agent.py
import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.together import Together
from composio_openai import ComposioToolSet, Action

# ─────────────────────────────────────────────────────────────────────────────
#  .env
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  Streamlit page
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI DeepResearch Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar – keys & status
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️  Keys & Integrations")

together_api_key = st.sidebar.text_input(
    "Together AI API Key",
    value=os.getenv("TOGETHER_API_KEY", ""),
    type="password"
)
composio_api_key = st.sidebar.text_input(
    "Composio API Key",
    value=os.getenv("COMPOSIO_API_KEY", ""),
    type="password"
)
perplexity_api_key = st.sidebar.text_input(
    "Perplexity API Key",
    value=os.getenv("PERPLEXITY_API_KEY", ""),
    type="password"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Connected Accounts")

# ─────────────────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────────────────
if "entity_id" not in st.session_state:
    st.session_state.entity_id = str(uuid.uuid4())

for k, v in {
    "googledocs_connected": False,
    "perplexity_connected": False,
    "questions": [],
    "question_answers": [],
    "report_content": "",
    "research_complete": False,
}.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────────────────────────────────────
#  Initialise Composio + LLM
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_toolset(api_key: str) -> ComposioToolSet:
    return ComposioToolSet(api_key=api_key)

def get_llm(api_key: str) -> Together:
    return Together(id="Qwen/Qwen3-235B-A22B-fp8-tput", api_key=api_key)

if not (together_api_key and composio_api_key):
    st.warning("Enter both Together AI and Composio API keys to continue.")
    st.stop()

toolset = get_toolset(composio_api_key)
llm = get_llm(together_api_key)

# ─────────────────────────────────────────────────────────────────────────────
#  IDs of the two dashboard integrations you created earlier
# ─────────────────────────────────────────────────────────────────────────────
GOOGLEDOCS_INTEGRATION_ID   = os.getenv("COMPOSIO_GOOGLEDOCS_INTEGRATION_ID", "ac_iowEpJV9xQVo")
PERPLEXITY_INTEGRATION_ID   = os.getenv("COMPOSIO_PERPLEXITY_INTEGRATION_ID", "ac_i-K3yDdWz_4C")

# ─────────────────────────────────────────────────────────────────────────────
#  OAuth helper (Google Docs)
# ─────────────────────────────────────────────────────────────────────────────
def connect_google_docs():
    try:
        req = toolset.initiate_connection(
            integration_id=GOOGLEDOCS_INTEGRATION_ID,
            entity_id=st.session_state.entity_id
        )
    except Exception as e:
        st.error(f"Could not start Google OAuth: {e}")
        return False

    st.markdown(f"[Click here to authorise Google Docs]({req.redirectUrl})")
    with st.spinner("Waiting for Google consent…"):
        try:
            req.wait_until_active(client=toolset.client, timeout=180)
        except Exception as e:
            st.error(f"Authorisation failed: {e}")
            return False
    st.success("Google Docs connected ✓")
    return True

# ─────────────────────────────────────────────────────────────────────────────
#  **NEW** helper for Perplexity (API-Key auth)
# ─────────────────────────────────────────────────────────────────────────────
def connect_perplexity(user_key: str):
    try:
        req = toolset.initiate_connection(
            integration_id=PERPLEXITY_INTEGRATION_ID,
            entity_id=st.session_state.entity_id,
            auth_scheme="API_KEY",               # token-style auth
            connected_account_params={           # field names come from `get_expected_params_for_user`
                "api_key": user_key
            }
        )
        # Key apps activate instantly; no redirect
        if req.connectionStatus != "ACTIVE":
            req.wait_until_active(client=toolset.client, timeout=30)
    except Exception as e:
        st.error(f"Perplexity connection failed: {e}")
        return False

    st.success("Perplexity connected ✓")
    return True

# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar buttons
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    if not st.session_state.googledocs_connected:
        if st.button("Connect Google Docs", use_container_width=True):
            st.session_state.googledocs_connected = connect_google_docs()
    else:
        st.success("Google Docs ✔️")

    if not st.session_state.perplexity_connected:
        if perplexity_api_key and st.button("Save Perplexity Key", use_container_width=True):
            st.session_state.perplexity_connected = connect_perplexity(perplexity_api_key)
    else:
        st.success("Perplexity ✔️")

if not (st.session_state.googledocs_connected and st.session_state.perplexity_connected):
    st.info("Connect both integrations first.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  Fetch the three tools *after* connections are active
# ─────────────────────────────────────────────────────────────────────────────
composio_tools = toolset.get_tools(actions=[
    Action.COMPOSIO_SEARCH_TAVILY_SEARCH,
    Action.PERPLEXITYAI_PERPLEXITY_AI_SEARCH,
    Action.GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN
])

# ─────────────────────────────────────────────────────────────────────────────
#  Helper functions  (unchanged from previous version)
# ─────────────────────────────────────────────────────────────────────────────
def create_question_generator():
    return Agent(
        name="Question Generator",
        model=llm,
        instructions=(
            "You are an expert at breaking down research topics into specific questions.\n"
            "Generate exactly 5 specific yes/no research questions about the given topic in the specified domain.\n"
            "Respond ONLY with the text of the 5 questions formatted as a numbered list, and NOTHING ELSE."
        )
    )

def extract_questions(text: str) -> list[str]:
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return [q.strip() for q in text.strip().splitlines() if q.strip()]

def generate_questions(topic: str, domain: str):
    with st.spinner("🤖 Generating questions…"):
        agent = create_question_generator()
        resp = agent.run(f"Generate exactly 5 specific yes/no research questions about '{topic}' in '{domain}'.")
    st.session_state.questions = extract_questions(resp.content)

def answer_question(topic: str, domain: str, question: str) -> str:
    research_agent = Agent(
        model=llm,
        tools=[composio_tools],
        instructions=(
            f"You are a sophisticated research assistant. Answer the question below about '{topic}' in '{domain}'.\n"
            f"Question: {question}\n"
            "Use PERPLEXITYAI_PERPLEXITY_AI_SEARCH and COMPOSIO_SEARCH_TAVILY_SEARCH for sources. "
            "Return a concise answer with citations."
        )
    )
    return research_agent.run().content

def compile_report(topic: str, domain: str):
    qa_sections = "\n".join(
        f"<h2>{i+1}. {qa['question']}</h2>\n<p>{qa['answer']}</p>"
        for i, qa in enumerate(st.session_state.question_answers)
    )
    compiler = Agent(
        name="Report Compiler",
        model=llm,
        tools=[composio_tools],
        instructions=(
            "Compile the findings into a professional, McKinsey-style report in HTML, "
            "then call GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN to save it to Google Drive.\n\n"
            f"Topic: {topic}\nDomain: {domain}\n\n"
            f"Findings:\n{qa_sections}"
        )
    )
    with st.spinner("📝 Compiling HTML & creating Google Doc…"):
        st.session_state.report_content = compiler.run().content
        st.session_state.research_complete = True

# ─────────────────────────────────────────────────────────────────────────────
#  UI — Topic & Domain
# ─────────────────────────────────────────────────────────────────────────────
st.title("🔍 AI DeepResearch Agent")

st.header("Research Topic")

c1, c2 = st.columns(2)
with c1:
    topic  = st.text_input("Topic",  placeholder="American tariffs")
with c2:
    domain = st.text_input("Domain", placeholder="Politics, Economics, Technology…")

# ─────────────────────────────────────────────────────────────────────────────
#  Workflow buttons
# ─────────────────────────────────────────────────────────────────────────────
if topic and domain and st.button("Generate Research Questions"):
    generate_questions(topic, domain)

if st.session_state.questions:
    st.header("Questions")
    for i, q in enumerate(st.session_state.questions, 1):
        st.markdown(f"**{i}. {q}**")

    if st.button("Start Research"):
        st.header("Research Results")
        prog = st.progress(0.0)
        answers = []
        for i, q in enumerate(st.session_state.questions, 1):
            prog.progress((i-1)/len(st.session_state.questions))
            with st.spinner(f"Researching Q{i}…"):
                ans = answer_question(topic, domain, q)
            answers.append({"question": q, "answer": ans})
            st.subheader(f"Q{i}: {q}")
            st.markdown(ans)
            prog.progress(i/len(st.session_state.questions))
        st.session_state.question_answers = answers

    if st.session_state.question_answers and st.button("Compile Final Report"):
        compile_report(topic, domain)

# ─────────────────────────────────────────────────────────────────────────────
#  Show final result
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.research_complete:
    st.success("Report saved to Google Docs!")
    with st.expander("HTML sent to Docs"):
        st.markdown(st.session_state.report_content, unsafe_allow_html=True)
