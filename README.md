# Vidjest

This is yet another GTP YouTube video summarizer.

I built this to get expereince with Streamlit and utilizing the OpenAI API.
Feel free to extend for your own needs if you find it useful.

![](docs/img/vidgest%20ui.png)

## Usage


```shell
# Create a python environment with the following
python -m venv .venv 

# Or use Conda if that is your jam

# Install python packages
pip install -r requirements.txt


streamlit run app.py
```

Note: You can add your API keys to the environment rather then inputing them in the UI.
```shell
mv dist.env .env
```
Ensure your IDE has support for .env files, then add your api keys to `.env`. and restart Streamlit
