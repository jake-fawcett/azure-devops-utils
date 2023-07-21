"""
Script to preview an Azure Pipeline template without needing to commit

Usage: pipeline-preview.py --pipeline-name ${pipelineName} --file-name ${fileName} --pat-token ${patToken} --organization ${organization} --project ${project}

Parameters:
- pipeline-name: Name of Pipeline within Azure DevOps
- file-name: Name of Pipeline .yaml file locally
- pat-token: Azure DevOps PAT Token
- organization: Name of Organization within Azure DevOps
- project: Name of Project within Azure DevOps
"""
import requests
import argparse
import json
import os


def get_file(file_name: str):
    with open(file_name, "rb") as file:
        return file.read().decode("utf-8")


def get_headers(pat_token: str):
    headers = {
        "Authorization": f"Basic {pat_token}",
        "Content-Type": "application/json",
    }
    return headers


def get_pipleine_id(organiation: str, project: str, pipeline_name: str, pat_token: str):
    url = f"https://dev.azure.com/{organiation}/{project}/_apis/pipelines?api-version=7.0"
    headers = get_headers(pat_token)
    for pipeline in requests.request("GET", url, headers=headers).json()["value"]:
        if pipeline["name"] == pipeline_name:
            return pipeline["id"]


def get_pipeline_preview(organiation: str, project: str, pipeline_id: str, file_name: str, pat_token: str):
    url = f"https://dev.azure.com/{organiation}/{project}/_apis/pipelines/{pipeline_id}/preview?api-version=7.0"
    payload = json.dumps({
        "previewRun": True,
        "yamlOverride": get_file(file_name)
    })
    headers = get_headers(pat_token)
    response = requests.request("POST", url, headers=headers, data=payload).json()

    if "finalYaml" in response:
        print("Pipeline validated successfully!")
    else:
        print(response["typeKey"], "\n", response["typeName"], "\n", response["message"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-name", type=str)
    parser.add_argument("--file-name", type=str)
    parser.add_argument("--pat-token", type=str, default=os.environ.get("PAT_TOKEN"))
    parser.add_argument("--organization", type=str)
    parser.add_argument("--project", type=str)
    args = parser.parse_args()

    pipeline_id = get_pipleine_id(args.organization, args.project, args.pipeline_name, args.pat_token)
    get_pipeline_preview(args.organization, args.project, pipeline_id, args.file_name, args.pat_token)

