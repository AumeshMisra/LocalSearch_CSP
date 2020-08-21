# LocalSearch_IWCSP
This project contains a local search template, as well as local search algorithms to solve IWCSP (Incomplete Weighted Constraint Satisfaction Problems) and IWCSP + EC (IWCSP + Elicitation Cost), where there is an elicitation cost when eliciting unknown costs from the user.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python Version 3.6.4

### Installing

All you have to do is clone/download the repo

## Deployment

A default command line statement to run the program is:
python LocalSearch_IWCSP.py --iterations 100000 --flag 1 --budget 70 --filepath input_files/Rnd5-3-1.xml --strategy BW --original 0

Here are the different input parameters:
1) --iterations
  number of iterations
2) --flag
  a flag on whether to include a budget or no (switch to 1 to include a budget)
3) --budget
  the budget the elicitation cost should not exceed
4) --filepath
  takes a filepath
5) --strategy
  the elicitation strategy we should employ
6) --original
  switch to 1 to run the program as an (IWCSP) otherwise leave as 0
