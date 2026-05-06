# Changing Functions

This pipeline was written and tested in [code workspaces](https://www.palantir.com/docs/foundry/code-workspaces/overview) in [Palantir Foundry](https://www.palantir.com/platforms/foundry/). It has since been adapted to run locally.

As such, two functions written within `src/processing.py` will need to be adapted if you plan on using this pipeline on another platform or locally.

## 1. `call_llm`

The `call_llm` function is the single abstraction layer between the pipeline and the language model provider.

If you wish to use a different LLM provider (e.g., OpenAI, Azure, Anthropic, a local model, etc.), you should modify only the internal implementation of this function, while keeping its interface unchanged.

Maintaining the same inputs and outputs is essential for ensuring that the rest of the pipeline continues to function correctly.

**Inputs**

| Parameter      | Type                | Description                                                                                       |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| `prompt`       | `str`               | The latest user prompt to send to the model.                                                      |
| `model`        | object              | A handle or identifier for the model to use. The exact format can vary depending on the provider. |
| `temp`         | `float`             | Sampling temperature controlling output randomness.                                               |
| `max_attempts` | `int`               | Number of retry attempts if the request fails.                                                    |
| `chat_history` | `list[str] \| None` | Optional alternating conversation history: `[user_0, assistant_0, user_1, assistant_1, ...]`.     |

**Outputs**

Required Output

The function must return a `String`.

Specifically:

- The raw text content produced by the LLM.
- If all retries fail, the function should return `None`.
- No other return types should be introduced.

**Behavioral Requirements**

Any replacement implementation should preserve the following behavior:

1. Prompt Handling

- The prompt must always be appended as the latest user message.
  
2. Chat History Formatting

- `chat_history` is provided as an alternating list of user and assistant messages.
- Implementations must convert this into the format required by the chosen LLM API.
  
3. Retry Logic

- The function should retry failed calls up to `max_attempts`.
- Errors should be logged or printed for debugging.
  
4. Temperature Control

The temp parameter must be passed through to the provider if supported.

5. Graceful Failure

If all attempts fail, the function should:

- log the failure
- return None.

**Example Function for working in the FDP**

```python

from foundry.transforms import Dataset
from language_model_service_api.languagemodelservice_api_completion_v3 import GptChatCompletionRequest
from language_model_service_api.languagemodelservice_api import ChatMessage, ChatMessageRole
from palantir_models.models import OpenAiGptChatLanguageModel

def call_llm(prompt: str, model: str = "GPT_4o", temp: float = 0.7, max_attempts: int = 3, chat_history = None) -> str:
    """
    Send a prompt to a chat-based LLM and return the model's text response.

    Builds a chat completion request using the provided prompt and optional
    conversation history, calls the model, and returns the raw response text.
    If the request fails, it retries up to `max_attempts` times.

    Parameters
    ----------
    prompt : str
        The user prompt appended as the latest message in the conversation.

    model : object
        Model client implementing `create_chat_completion(request)`.

    temp : float, default=0.7
        Sampling temperature controlling response randomness.

    max_attempts : int, default=3
        Number of retry attempts if the LLM call fails.

    chat_history : list[str] | None, default=None
        Optional alternating list of messages:
        [user_0, assistant_0, user_1, assistant_1, ...].
        The prompt is added as the final user message.

    Returns
    -------
    str
        Raw text content from the model response, or None if all attempts fail.
    """
    try:
        model = OpenAiGptChatLanguageModel.get(model)
    except:
        raise Exception(f"No model called {model}")
    
    if not chat_history:
        request = GptChatCompletionRequest([
            ChatMessage(ChatMessageRole.USER, prompt)
        ], temperature = temp)
    else:
        history = [ChatMessage(ChatMessageRole.USER, chat_history[i]) if i%2 == 0 else ChatMessage(ChatMessageRole.ASSISTANT, chat_history[i]) for i in range(len(chat_history))]
        request = GptChatCompletionRequest(
            history + [ChatMessage(ChatMessageRole.USER, prompt)],
            temperature = temp)
        
    # Call the LLM
    for attempt in range(max_attempts):
        try:
            response = model.create_chat_completion(request)
            raw_content = response.choices[0].message.content
        except Exception as e:
            print(f"LLM call failed with error: {e} on attempt {attempt + 1}/{max_attempts}. Retrying...")
            time.sleep(1)
        else:
            return raw_content
    else:
        print (f"Failed after {max_attempts} attempts.")
```

## 2. `read_write_data`

The `read_write_data` function acts as the abstraction layer between the pipeline and the underlying data storage system.

Currently, it uses the `Dataset` API to read and write tables. If you wish to use a different storage system (e.g., local files, SQL databases, cloud storage, or another data platform), you should modify only the internal implementation of this function while keeping the function interface unchanged.

Maintaining the same inputs and outputs ensures the rest of the pipeline continues to work without modification.

**Inputs**

| Parameter       | Type                   | Description                                                                                                                                       |
| --------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `table_name`    | `str`                  | Identifier of the dataset to read from or write to. The interpretation of this name depends on the storage backend (table name, file path, etc.). |
| `read_or_write` | `str`                  | Operation to perform. Must be `"read"` or `"write"`.                                                                                              |
| `data`          | `pd.DataFrame \| None` | DataFrame to write when `read_or_write="write"`. Ignored when reading. |

**Outputs**

The function must return:

- `pd.DataFrame` when `read_or_write == "read"`
- `None` when `read_or_write == "write"`

The pipeline assumes these exact return behaviors.

**Behavioral Requirements**

Any replacement implementation should preserve the following behavior:

1. Read Operation

- When `read_or_write == "read"`, the function must retrieve the dataset identified by `table_name`.
- The returned object must be a pandas DataFrame.

2. Write Operation

- When `read_or_write == "write"`, the function must write the provided DataFrame to the dataset.
- The function should return None.

3. Validation

- If `read_or_write` is not `"read"` or `"write"`, the function should raise an exception.
- If `read_or_write == "write"` but `data` is `None`, an exception should also be raised.

4. DataFrame Compatibility

- All reads must return data in a pandas DataFrame format, even if the underlying system uses a different structure (e.g., Arrow tables or SQL query results).

**Example Function for working in the FDP**

```python

from foundry.transforms import Dataset
from language_model_service_api.languagemodelservice_api_completion_v3 import GptChatCompletionRequest
from language_model_service_api.languagemodelservice_api import ChatMessage, ChatMessageRole
from palantir_models.models import OpenAiGptChatLanguageModel


def read_write_data(table_name: str, read_or_write: str, data: pd.DataFrame = None) -> pd.DataFrame:
    """
    Read from or write a pandas DataFrame to a dataset table.

    Depending on `read_or_write`, this function either retrieves a table
    as a pandas DataFrame or writes the provided DataFrame to the table.

    Parameters
    ----------
    table_name : str
        Name of the dataset table to read from or write to.

    read_or_write : str
        Operation to perform: either `"read"` or `"write"`.

    data : pd.DataFrame | None, default=None
        DataFrame to write when `read_or_write="write"`. Ignored for reads.

    Returns
    -------
    pd.DataFrame | None
        Returns the table as a pandas DataFrame when reading.
        Returns None when writing.

    Raises
    ------
    Exception
        If `read_or_write` is not `"read"` or `"write"`, or if writing
        without providing `data`.
    """

    if read_or_write == "read":
        return Dataset.get(table_name).read_table(format="pandas")
    elif read_or_write == "write" and data is not None:
        Dataset.get(table_name).write_table(data)
    else:
        raise Exception("Error: Check read_or_write is one of 'read' or 'write' and data is not None")

    return None
```