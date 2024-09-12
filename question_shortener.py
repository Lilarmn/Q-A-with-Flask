from langchain_openai import ChatOpenAI
import logging

bio_text_template = f"""
لطفا برای این سوال یک عنوان فارسی بده :  
"""
def questionShortener(text : str):
    logging.info(f"Starting bio analyzer...")
    base_url = "https://api.avalai.ir/v1"
    api_key = "AVALAI_API_KEY"
    model_name = "gpt-4o"

    llm = ChatOpenAI(
        base_url=base_url,
        name=model_name,
        api_key="aa-v1U0GVZfStI5LX6cirP51nEEmRKuLC8GaywCs43b79dtUNNN",
    )

    response = dict(llm.invoke(bio_text_template + text)).get('content',"timed out")
    return response