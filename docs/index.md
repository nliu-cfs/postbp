# Welcome to postbp


[![image](https://img.shields.io/pypi/v/postbp.svg)](https://pypi.python.org/pypi/postbp)


**A Python Library**

PostBP is an open-source Python package designed for post-processing the raw outputs of fire growth models — the ignition locations and perimeters of individual fires simulated over multiple stochastic iterations — into a matrix of fire spread likelihoods between all pairs of forest patches in a landscape. 


-   Free software: MIT License
-   Documentation: <https://nliu-cfs.github.io/postbp>
    

## Features

PostBP offers three post-processing options for analyzing FGM outputs.
 - Option 1 (“Direct overlay analysis”) generates maps of mean burn and ignition likelihoods for a user-defined set of forest landscape patches. 
 - Option 2 (“Directional fire spread analysis”) uses the ignition locations and final perimeters of individual fires to generate vectors of spread likelihoods between all pairs of forest patches in a landscape, along with a map of source-sink ratios and a fire spread rose diagram. 
 - Option 3 (“Daily directional fire spread analysis”) is similar to option 2 but generates fire spread likelihoods and summary outputs from sequences of daily fire perimeters instead of the final fire perimeters utilized in option 2.
