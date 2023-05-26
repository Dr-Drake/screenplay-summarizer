from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

async def llm_summarize(screenplay_text: str, light: bool = False):
    # Initialize our OpenAI LLM Wrapper
    llm = OpenAI(temperature=0, model_name = 'text-davinci-003')

    # Initialize our text splitter
    text_splitter = CharacterTextSplitter(
        chunk_size = 3500,
        chunk_overlap = 500,
    )

    # Split the texts into chunks
    texts = text_splitter.split_text(screenplay_text)

    # Write our custom propmt for the first chain
    prompt_template = """You are an expert screenwriter with an expertise in summarizing screenplays:
    Write a summary for the screenplay below.
    The summary should include a title and genre.
    The summary should also include a section which lists the main characters and their description.
    It should also include a section called synopsis, which is an actual synopsis.
    A logline should follow after.
    The summary should also include sections for Act 1, Act 2, and Act 3. 
    Act 1 introduces the characters and the main conflict that drives the story. 
    Act 2, which is the conflict itself, shows the plot twists and conflicts the characters face. 
    Act 3 shows how the main conflict ends and what happens to the characters. 


    {text}

    FULL SUMMARY:
    """

    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["text"]
    )

    # Create multisummary chain
    multisummary_chain = LLMChain(llm = llm, prompt = PROMPT)

    #TODO - If light optimize chunk array length
    print("Size of texts is: ", len(texts))
    # if light and len(texts) > 15:
    #     texts

    ## Step 1 - Run llm chains on each chunk
    print("Running chains...")
    llm_chain_input = [{'text': t} for t in texts]
    results = multisummary_chain.apply(llm_chain_input)
    print ("Results returned, of length: ", len(results))

    # We only need to select a few of the returned summaries
    # Why? Because in the second chain, we are using a chat model which has a
    # limited token size
    summaries: list[str] = [e['text'] for e in results]
    if len(summaries) == 1:
        return {
            "multi_summary": summaries[0],
            "merged_summary": summaries[0]
        }
        

    # Select strategic summaries to combine
    arrLength = len(summaries) - 1
    
    firstIndex = 0 # The first summary
    secondIndex = round(arrLength/3) # A summary around the beginning
    thirdIndex = round(arrLength/2) # A summary around the middle
    fourthIndex = round(arrLength/3) * 2 # A summary around the end
    lastIndex = arrLength # A summary at the end

    selectedSummaries = [
        summaries[firstIndex], 
        summaries[secondIndex], 
        summaries[thirdIndex], 
        summaries[fourthIndex], 
        summaries[lastIndex]
    ]

    # Concatenate the selected summaries into one string
    multisummary = ''
    for t in selectedSummaries:
        multisummary += "\n" + t


    ## Step 2 - Prompt ChatOpenAI to merge summaries

    # Initialize our chat model
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)

    # Generate System Prompt
    template="You are an expert screenwriter with an expertise in summarizing screenplays."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    # Generate Human Prompt
    human_template="""
    Below is a group of summaries for a screen play. 
    Merge the group of summaries into one comprehensive summary
    Each summary is supposed to include a Title, Genre, Main Characters, a logline, and synopsis.
    The merged summary should also include  sections for Act 1, Act 2, and Act 3. 
    Act 1 should represent an introduction to the characters and the main conflict that drives the story. 
    Act 2 should represent the conflict itself, showing the plot twists and conflicts the characters face. 
    Act 3 should represent how the main conflict ends and what happens to the characters.

    {text}

    """
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Generate Chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    # Generate merged summary from chat ai
    print("Chat model...")
    final_summary = chat(chat_prompt.format_prompt(text=multisummary).to_messages())
    print("Chat model result returned")

    return {
        "multi_summary": multisummary,
        "merged_summary": final_summary.content
    }


    


    
    
        