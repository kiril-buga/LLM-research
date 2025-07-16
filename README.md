# LLM Research: Text-to-SQL

This repository contains research and experiments on using Large Language Models (LLMs) to convert natural language questions into SQL queries, execute them, and return a natural language answer (Text-to-SQL-to-Text).

The primary experiments are conducted in the `Experiment_setup.ipynb` notebook.

## Core Idea

The project explores a Text-to-SQL-to-Text pipeline:
1.  A user asks a question in natural language.
2.  An LLM generates the corresponding SQL query.
3.  The SQL query is executed against a database.
4.  The results are used to generate a final natural language answer for the user.
5.  Experiment results, including the question, generated SQL, and final answer, are logged to an Excel file for analysis.
