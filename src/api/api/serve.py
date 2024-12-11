from fastapi import FastAPI, HTTPException
import polars as pl
from pathlib import Path

df_path = Path("data/NIST.tsv")
variants_df = pl.read_csv(df_path, separator="\t")
variants_df = variants_df.sort("freq",nulls_last=True)

tags_metadata = [
    {
        "name": "filter",
        "description": "Operations with filtering.",
    },
    {
        "name": "items",
        "description": "Operations using the entire dataset",
    },
]

description = f"""
# API for the {df_path.stem} sample

This API is designed to be used for accessing and filtering the variants in the sample.
"""

app = FastAPI(
    openapi_tags=tags_metadata,
    title=df_path.stem,
    description=description,
    summary=f"API for the {df_path.stem} sample",
    version="0.0.1",
)

@app.get(
    "/",
    summary="Retrieves information about the API and the sample", 
    description="Retrieves information about the API and the sample",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def read_root():
    return {
        "info": f"Serving API for the {df_path.stem} sample",
        "sample": df_path.stem,
        "num_SNPs": len(variants_df),
    }

@app.get(
    "/meta",
    summary="Retrieves meta from the entire dataset", 
    description="Retrieves meta from the entire dataset",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def meta():
    return {
        "num_SNPs": len(variants_df),
        "dp": [variants_df["dp"].min(), variants_df["dp"].max()],
        "freq": [variants_df["freq"].min(), variants_df["freq"].max()],
        "male_freq": [variants_df["male_freq"].min(), variants_df["male_freq"].max()],
        "female_freq": [variants_df["female_freq"].min(), variants_df["female_freq"].max()],
    }

@app.get(
    "/variants",
    summary="Retrieves the entire dataset", 
    description="Retrieves the entire dataset",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def get_variants():
    return variants_df.to_dicts()

@app.get(
    "/filter/{parameter}/{operator}/{value}",
    summary="Filters the dataset", 
    description="Filters the dataset using the specified parameter, based on the specified operator and value",
    tags=["filter"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
        400: {"description": "User mistake on the query"},
    },
)
def filter_variants(parameter: str, operator: str, value: float):
    # hgvs	rsid	genes	freq	male_freq	female_freq	dp
    accepted_columns = ["freq", "male_freq", "female_freq", "dp"]
    accepted_params = ["gt", "lt", "eq"]
    if parameter not in accepted_columns:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {parameter}. Must be one of: {accepted_columns}")

    if operator not in accepted_params:
        raise HTTPException(status_code=400, detail=f"Invalid operator. Must be one of: {accepted_params}")
    if value < 0 or value > variants_df[parameter].max():
        raise HTTPException(status_code=400, detail=f"Value {value} is out of range for parameter: {parameter}")
    
    if operator == "eq":
        filtered_variants = variants_df.filter(pl.col(parameter) == value)
    elif operator == "gt":
        filtered_variants = variants_df.filter(pl.col(parameter) > value)
    elif operator == "lt":
        filtered_variants = variants_df.filter(pl.col(parameter) < value)

    return filtered_variants.to_dicts()
