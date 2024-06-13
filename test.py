from dotenv import load_dotenv
load_dotenv()
import os
api_key=os.getenv('OPENAI_API_KEY')
import openai
openai.api_key=api_key
import mlflow
import openai
import pandas as pd
import dagshub

dagshub.init(repo_owner='princegupta995643',repo_name='LMflow-project',mlflow=True)
mlflow.set_tracking_uri("https://dagshub.com/princegupta995643/MLflow-project.mlflow")

eval_data=pd.DataFrame(
    {
        "inputs":[
            "What is MLflow?",
            "What is Spark?",
        ],
        "ground_truth":[
            """MLflow is an open-source platform designed to manage the end-to-end machine learning lifecycle. It was developed by Databricks and provides a suite of tools to handle the various stages involved in building, deploying, and maintaining machine learning models.""" ,           
            """Apache Spark is an open-source unified analytics engine designed for large-scale data processing. It provides a comprehensive and efficient platform for big data processing, enabling users to perform both batch and streaming data analysis. Spark is known for its speed, ease of use, and versatility, making it a popular choice for data engineers and data scientists."""
        ]
    }
)

mlflow.set_experiment('LLM Evaluation')
with mlflow.start_run() as run:
    system_prompt="Answer the following question in two sentences"
    logged_model_info=mlflow.openai.log_model(
        model='gpt-4',
        task=openai.chat.completions,
        artifact_path='model',
        messages=[{'role':'system','content':system_prompt},
        {"role": "user", "content":"{question}"},
        ],
    )

#Use predefined question - answering metrics to evaluate our model.
results=mlflow.evaluate(
    logged_model_info.model_uri,
    eval_data,
    targets='ground_truth',
    model_type='question-answering',
    extra_metrics=[mlflow.metrics.toxicity(),mlflow.metrics.latency(),           mlflow.metrics.genai.answer_similarity()]
)

print(f'See aggregated evaluation results below:\n{results.metrics}')

#Evaluation result for each data record is abailable in table
eval_table=results.tables['eval_results_table']
df=pd.DataFrame(eval_table)
df.to_csv('eval.csv')
print(f'See evaluation table below:\n{eval_table}')