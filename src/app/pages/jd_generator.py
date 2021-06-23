# flake8: noqa

import json
import sqlite3
from pathlib import Path
from time import perf_counter
from typing import Dict

import openai
import streamlit as st
import yaml
from app.app_config import DATASETS, GPT3_CONFIG_PATH, MODELS, PARAMS
from loguru import logger
from openai.openai_object import OpenAIObject

JOB_DESCRIPTION = """
### Requirements:
You’re an engineer who gets excited about turning ideas into reliable production code. You appreciate clear code that can be read by others and yourself 6 months down the line. You enjoy collaborating with other developers and get excited about thousands of people experiencing a feature you shipped just minutes ago. You thrive on fast feedback loops & iterative development cycles.​ You’ve got experience working in a test-driven development environment and can help us adopt this approach at Smile.​

**What we’re seeking**:

* Prior experience (5-10 years) improving the reliability of a SaaS product
* 5+ years of technical experience in software architecture/systems design
* A capable engineer, with previous background building web or mobile applications
* Experienced in full-stack development and software architecture patterns, able to understand how a wide variety of technologies and systems interact with each other
* The ability to build software systems given a set of technical designs
* An ability to adapt to shifting priorities, demands, and timelines
* A great communicator, comfortable explaining complex concepts to both technical and non-technical audiences

**Traits or experience we’d love to see (you don’t need them all to apply)**:

- Comfortable writing code in a few of our primary deployment languages (Ruby on Rails, Ember.js, React) and enjoys learning new languages and technologies
- Thrives in a cross-functional, collaborative environment
- Knowledge of secure coding practices and test-driven development approach
- Interested in solving open-ended business problems with a combination of technology and creative thinking"""

@st.cache(allow_output_mutation=True)
def db_conn():
    DB_PATH = Path(__file__).parents[3] / "db" / "results.db"
    logger.info(f"Connecting to DB: {str(DB_PATH)}")
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def jd_generator() -> None:
    debug = st.sidebar.selectbox("Debug mode:", [False, True])
    select_option = st.sidebar.radio(
        "Set API key:", ["Add your own", "Load local config"]
    )
    if select_option == "Add your own":
        key_added = st.sidebar.text_area("Add OpenAI key *")
        key_submit = st.sidebar.button("Submit key")
        if key_submit:
            openai.api_key = key_added
            st.write("(OpenAI key loaded)")
    elif select_option == "Load local config":
        load_local = st.sidebar.button("Load local config")
        if load_local:
            load_openai_key()
            st.write("(OpenAI key loaded)")

    PARAMS["engine"] = st.sidebar.selectbox("Select OpenAI model(`engine`):", MODELS)
    st.markdown(f"Model selected: `{PARAMS['engine']}`")

    company_name = st.text_input("Company Name", value="CrewScale")
    company_website = st.text_input("Company Website", value="https://crewscale.com")

    role = st.selectbox("Role", ["Frontend Engineer", "Backend Engineer", "DevOps Engineer", "Data Scientist"])

    experience = st.selectbox("Experience", ["< 1 year", "1 - 3 years", "< 5 years", " > 5 years"])

    PARAMS["max_tokens"] = st.sidebar.number_input(
        "Max Tokens to generate(`max_tokens`):", min_value=1, max_value=2048, step=1
    )
    PARAMS["best_of"] = st.sidebar.number_input(
        "Max number of completions(`best_of`):", min_value=1, max_value=2048, step=1
    )
    randomness = st.sidebar.radio("Randomness param:", ["temperature", "top_n"])
    if randomness == "temperature":
        PARAMS["temperature"] = st.sidebar.number_input(
            "Temperature", min_value=0.0, max_value=1.0
        )
    elif randomness == "top_n":
        PARAMS["top_p"] = st.sidebar.number_input(
            "Top P (Alternative sampling to `temperature`)", min_value=0.0, max_value=1.0
        )

    PARAMS["stream"] = st.sidebar.selectbox("Stream output?(`stream`)", [False, True])
    # show_input_ds = st.selectbox("Show Input?", [False, True])
    PARAMS["stop"] = "\n"
    PARAMS["presence_penalty"] = st.sidebar.number_input(
        "Presence penalty(`presence_penalty`)", min_value=0.0, max_value=1.0
    )
    PARAMS["frequency_penalty"] = st.sidebar.number_input(
        "Frequency penalty(`frequence_penalty`)", min_value=0.0, max_value=1.0
    )

    logprobs = st.sidebar.selectbox("Include Log probabilites?", [False, True])
    if logprobs:
        st.write(logprobs)
        PARAMS["logprobs"] = st.sidebar.number_input(
            "Log probabilities(`logprobs`):", min_value=1, max_value=2048, step=1
        )
    PARAMS["echo"] = st.sidebar.selectbox("Echo:", [False, True])

    # try:
    dataset = []
    # prime_type = st.radio("Select dataset", ["Examples", "Upload own"])
    # if prime_type == "Examples":
    #     prime = st.selectbox("Select dataset:", list(DATASETS.keys()))
    #     dataset = load_primes(prime=prime)
    # elif prime_type == "Upload own":
    #     file_string = st.file_uploader("Upload dataset", type=["yaml", "yml"])
    #     dataset = yaml.safe_load(file_string)
    #     st.success("Uploaded successfully")
    # prompt = st.text_area("Enter your prompt(`prompt`)", value="Enter just the text...")
    submit = st.button("Submit")
    stop = st.button("Stop request")
    # parsed_primes = "".join(list(dataset["dataset"].values()))

    # if show_input_ds:
    #     st.info(f"{parsed_primes}\n\n{dataset['input']}:{prompt}\n{dataset['output']}:")

    # PARAMS[
    #     "prompt"
    # ] = f"{parsed_primes}\n\n{dataset['input']}:{prompt}\n{dataset['output']}:"
    if debug:
        st.write(PARAMS)

    if submit:
        st.text_area("Job Description", value=JOB_DESCRIPTION, height=1000)

        # with st.spinner("Requesting completion..."):
        #     ts_start = perf_counter()
        #     request = openai.Completion.create(**PARAMS)
        #     ts_end = perf_counter()
        # if debug:
        #     st.write(request)
        # st.write([choice["text"] for choice in request["choices"]])
        # st.error(f"Took {round(ts_end - ts_start, 3)} secs to get completion/s")
        # save_results(
        #     experiment_name=experiment_name,
        #     result=request,
        #     time_in_secs=round(ts_end - ts_start, 3),
        #     og_dataset=dataset,
        #     api_params=PARAMS,
        # )
    if stop:
        st.error("Process stopped")
        st.stop()
    # except Exception as err:
    #     st.error(f"[ERROR]:: {err}")


def load_primes(prime: str) -> Dict:
    with open(DATASETS[prime], "r") as file_handle:
        dataset = yaml.safe_load(file_handle)

    return dataset


def load_openai_key() -> None:
    with open(GPT3_CONFIG_PATH, "r") as file_handle:
        openai.api_key = yaml.safe_load(file_handle)["GPT3_API"]


def save_results(
    experiment_name: str,
    result: OpenAIObject,
    time_in_secs: float,
    og_dataset: Dict,
    api_params: Dict,
):
    cursor = db_conn().cursor()
    query = f"""
        INSERT INTO gpt3_results (result_id, experiment_name, api_params, response_time, output_response, language, nlp_task, error_msg)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """
    logger.info(f"Query to be executed:\n{query}")
    cursor.execute(
        query,
        [
            result["id"],
            experiment_name,
            json.dumps(api_params),
            time_in_secs,
            ", ".join([choice["text"] for choice in result["choices"]]),
            og_dataset["language"],
            og_dataset["nlp_task"],
            "",
        ],
    )
    db_conn().commit()
    st.write("Saved successfully to DB")
