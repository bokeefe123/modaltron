## Prerequisites 

Running on Modal requires installation and setup of the Modal client 

## Installation

__Clone the repository__

        git clone https://github.com/bokeefe123/modaltron.git
        cd modaltron

__Install dependencies__

        npm install
        bower install

__Build the game__

        npx gulp front-full

__Launch server__

        cd python_server
        modal deploy python_server/modal_app.py

__Play__

Navigate to the link returned from Modal

__Configure region__
Open modal_app.py

Change the deploy region options to preferred region.

```python
@app.function(
    image=image,
    scaledown_window=300,  # Keep warm for 5 minutes during active games
    region="us-west",
    experimental_options={"input_plane_region": "us-west"}
)
```