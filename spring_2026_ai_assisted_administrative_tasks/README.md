# AI-Assisted Administrative Tasks - Transforming Summaries of Scientific Work

## Description

AI tools can assist with non-coding research tasks such as lay summaries, presentations, funding updates, email drafts, and report formatting. This seminar explores pitfalls (oversimplification, factual loss, tone mismatch, fabricated details), prompt strategies (role prompts, structured context input, prompt chaining, format templates), and basic agent concepts (reusable templates that transform scientific content through repeated stages).

---

## Binder

Binder is a free, cloud-based service that lets you launch interactive Jupyter notebooks and other environments directly from this repository, with no local installation required. Use the button below to launch a ready-to-use environment for this course.

No Binder environment selected for this course.

---

## Course Exercise

The following directories contain supporting materials (code and AI Agent instructions) for interactive class demos.

- *event_flyer_agent*: example command line agent (Python) that parses event details from PDF or image fliers and adds to a Goolge calendar
- *custom_gpts*: instructions for defining custom lightweight agents (ChatGPT Custom GPT)

 > For the `Project Description Rewriter` the following should work as acceptable input to test all modes:

### Requirements

To fully explore lightweight AI agents during the seminar, we will be using **ChatGPT**.  To be able to actively participate in demo activities, you will need to bring a laptop and have registered for either a ChatGPT or ChatGPT Edu account.  You can also following along with **Claude**, which offers similar functionality.  

### Event Flyer Agent

To run the `event_flyer_agent` (optional) you will also need the following:

- Python 3.10+
- (optional, but recommended) a Python [virtual env](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- git (desktop or cli)

See agent [README](./event_flyer_agent/README.md) for details and installation instructions

---

## Additional Resources

### No/low-code Agents
- [n8n](https://n8n.io)
- [Flowise](https://flowiseai.com)
- [Zapier](https://zapier.com)
- [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/)
- [LangFlow](https://langflow.org)
- [Microsoft Power Automate](https://powerautomate.microsoft.com)

### Coding Solutions

> Note: that coding solutions have primarily been developed in **Python**

#### SDKs

- [Langchain](https://www.langchain.com/)
- [Claude SDK](https://platform.claude.com/docs/en/agent-sdk/overview) - not open source
- [OpenAI SDK](https://openai.github.io/openai-agents-python/)
- [Haystack](https://haystack.deepset.ai/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)

#### Model Platforms or Frameworks w/wrapper libraries

#### Open / Community Driven
- [Hugging Face Model Hub](https://huggingface.co/models)
  
#### Commercial Platforms
- [OpenAI](https://developers.openai.com/)
- [Anthropic](https://platform.claude.com/docs/en/home)
- [Google DeepMind](https://ai.google.dev/) - Gemini models
- [Mistral AI](https://ai.google.dev/)

#### Open Ecosystems
- [Ollama](https://ollama.com/)
- [Hugging Face](https://huggingface.co)
- [NVIDIA NIM](https://docs.nvidia.com/nim/) *open source models, managed infrastructure
- [Together AI](https://docs.together.ai/) *open source models, managed infrastructure
