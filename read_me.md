# RayCi cmd 

Command Line Tool For Beam Profiler Software RayCi.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## Introduction

RayCi command line tool designed to automate laser beam measurements. It allows the user to manually adjust various camera settings, capture an image and generate a light intensity histogram.

## Features

- Camera adjustment: the user can adjust such properties as:
    - Exposure time
    - Gain
    - Reduce pixel clock
    - Flip the view vertically
    - Flip the view horizontally
    - Rotate the view to the left
    - Rotate the view to the right
- Capture an image: the user can capture an image, name it and save it to wanted directory. Also, a user has a choice of random file name generation and saving the image to a default directory.
- Histogram: the user can obtain a histogram for their picture. It is also possible to display Gaussian distribution.
- Help: run python cinogy.py --help to see all the available functions and their usage.

## Installation

This code requires the user to install RayCi software with SDK tools and python support (check the box for 'Python library & Examples'). Then open RayCi, go to Extras -> Global Settings -> XmlRpc and activate the XmlRpc-Server with a port 8080. In case the port is already taken, you need to choose another one and update this information in the source code (line 23). In general, it is required to configure the Firewall to allow network communication with RayCi.



## Usage

First, have the cinogy.py file in the same directory as the program that you are writing and import cinogy. To use this code for measurement automation it is best to utilise subprocess library. Thus, import subprocess and use this as a template: 

result = subprocess.run ( [ " python ", " cinogy.py ", " --help " ], capture_output = True, text = True)

print("Program output:", result.stdout)

print("Program error (if any):", result.stderr)

print("Program exit code:", result.returncode)

Note: currently to use this, you have to open RayCi and put it on LiveMode.

---

