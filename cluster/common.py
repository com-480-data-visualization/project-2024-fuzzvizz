import os
import glob
import openai


workdir = os.path.dirname(os.path.abspath(__file__))


def prompt_single(content, schema, model="mistral"):
    if model == "mistral":
        with open(os.path.join(workdir, "anyscale_api_key")) as f:
            api_key = f.read().strip()

        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.endpoints.anyscale.com/v1",
        )

        chat_completion = client.chat.completions.create(
            seed=3407,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            response_format={"type": "json_object", "schema": schema},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                { "role": "user",
                    "content": content,
                },
            ],
        )
    elif model == "gpt4":
        with open(os.path.join(workdir, "openai_api_key")) as f:
            api_key = f.read().strip()

        client = openai.OpenAI(
            api_key=api_key
        )

        chat_completion = client.chat.completions.create(
            seed=3407,
            model="gpt-4-0125-preview",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": f"Your response must follow this JSON Schema:\n{schema}"
                },
                { "role": "user",
                    "content": content,
                },
            ],
        )
    else:
        raise ValueError("unsupported model")

    return chat_completion


def glob_basename(path):
    return {os.path.basename(p) for p in glob.glob(path)}


def glob_remaining(src: str, dst: str):
    return glob_basename(src) - glob_basename(dst)


def get_remaining(src: str, dst: str, target: str):
    srcp = os.path.join(src, target, "*.json")
    dstp = os.path.join(dst, target, "*.json")

    return glob_remaining(srcp, dstp)
