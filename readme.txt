How to run the program for IWCSPs+EC

#Step1: We use a randomly generated problem in xml format and use the following code (readInput.py) to convert it to an incomplete problem with some unknown constraint costs as follows:

 Input arguments in order of appearance: {xml file}, {1: is the command to assign a number of unknown costs to the whole problem or 2: every constraint will get some percentage of unknown costs}, {number of unknowns in total or percentage of unknown costs in every constraints}, {path to generate the output}, {name of the output file} 

Example: python readInput.py Rnd5-7-1.xml 2 40 ./ 1

#Step2: Given the generated problem outputs with unknown constraint costs, we use the following code (GenerateTree.py) to solve the problem 
Input arguments in order of appearance: {weight}, {granularity}, {heuristic method}, {type of weight}, {with or without elicitation cost}, {path to read the output problem}, {name of the output file}   

{weight}: We use an additive weight or a relative weight, their default values are 0 and 1 respectively.
{granularity}: In case of additive and in case of relative: can be any positive number
{heuristic method}: pa, ps, sc  
{type of weight}: a for additive and r for relative
{with or without elicitation cost}: 0 for without elicitation cost and 1 for with elicitation cost
{path to read the output problem}: absolute path to the xml input file and generated outputs
{name of the output file}: name of the output 

Example: python GenerateTree.py Rnd5-7-1.xml 1 0 ps r 0 ./ 1


Output numbers shown after running the above command are as follows: lower bound on the cost tables , upper bound on the cost tables , the total solution costs (updated final upper bound), actual constraint cost before adding elicitation costs to it , accumulated elicited cost , number of elicited constraints , total number of unknown costs in the problem, runtime of solving the problem , elicitation costs of the optimal solution it self which is not cumulative

