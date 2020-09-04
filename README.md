# LocalSearch_IWCSP
This project contains a local search template, as well as local search algorithms to solve IWCSP (Incomplete Weighted Constraint Satisfaction Problems) and IWCSP + EC (IWCSP + Elicitation Cost), where there is an elicitation cost when eliciting unknown costs from the user.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python Version 3.6.4

### Installing

All you have to do is clone/download the repo

## Deployment

These instructions will help you run and deploy the program

### Step1:

We use a randomly generated problem in xml format and use the following code (readInput.py) to convert it to an incomplete problem with some unknown constraint costs as follows:

 Input arguments in order of appearance: {xml file}, {1: is the command to assign a number of unknown costs to the whole problem or 2: every constraint will get some percentage of unknown costs}, {number of unknowns in total or percentage of unknown costs in every constraints}, {path to generate the output}, {name of the output file}

Example: python readInput.py Rnd5-7-1.xml 2 40 ./ 1

### Step2:

We run the local search algorithm on the problem using the generated files from the previous step

An example command line statement to run the local search program is: <br />

Example: python LocalSearch_IWCSP.py --iterations 100000 --flag 1 --budget 70 --filepath input_files/Rnd5-3-1.xml --strategy BW --original 0

Here are the different input parameters:
1) --iterations <br />
  number of iterations
2) --flag <br />
  a flag on whether to include a budget or no (switch to 1 to include a budget)
3) --budget <br />
  the budget the elicitation cost should not exceed
4) --filepath <br />
  takes a filepath
5) --strategy <br />
  the elicitation strategy we should employ
6) --original <br />
  switch to 1 to run the program as an (IWCSP) otherwise leave as 0

## Brief Overview

### Elicitation Strategies

There are multiple elicitation strategies that the user can choose from:
1) ALL: User elicits all missing values.
2) WW: User elicits the missing value that has the worst (highest) constraint cost. We do this until the constraint cost of the explored solution > optimal solution.
3) BB: User elicits the missing value that has the best (lowest) constraint cost. We do this until the constraint cost of the explored solution > optimal solution.
4) BW: User alternates between eliciting the missing value with best (lowest) constraint cost and worst (highest) constraint cost. We do this until the constraint cost of the explored solution > optimal solution.
5) WM: User elicits the missing value that has the worst (highest) constraint cost + elicitation cost. We do this until cost of the explored solution > optimal solution and if the elicitation cost of (missing values + cumulative elicitation cost) < budget.
6) BM: User elicits the missing value that has the best (lowest) constraint cost + elicitation cost. We do this until cost of the explored solution > optimal solution and if the elicitation cost of (missing values + cumulative elicitation cost) < budget.
7) MM: User elicits the missing value that has the best (lowest) elicitation cost only. We do this until cost of the explored solution > optimal solution and if the elicitation cost of (missing value + cumulative elicitation cost) < budget
