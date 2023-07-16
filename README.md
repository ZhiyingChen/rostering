# Rostering
    
 **Problem**
 
This is a project to solve the following problem.
<img src="https://github.com/ZhiyingChen/Rostering/blob/master/image/Question.png" style="width:900px; height:400px">

The service area must have at least 1 vehicle serving locally every hour, and each vehicle must return after 6 hours of work in the service area. Each vehicle needs to be repaired for 40h after 80h of cumulative operation during working hours. Q: How many vehicles are needed at least in a month (30 days)? And draw the Gantt chart of the tasks of these cars.
(All parameters can be changed).

**Result Example**

This is a gantt plot.
<img src="https://github.com/ZhiyingChen/Rostering/blob/master/image/example.png" style="width:1000px; height:300px">

If we change two parameters, for instance, the service area must have at least 2 vehicles serving locally every hour, and each vehicle needs to be repaired for 40h after 200h of cumulative operation during working hours. Other parameters remain unchanged.
We get the following gantt plot of results.
<img src="https://github.com/ZhiyingChen/Rostering/blob/master/image/example2.png" style="width:1000px; height:300px">

**Environment Deployment**

 Install Python Executor (version >= 3.7.0), Anaconda IDE is recommanded


The required packages are listed in requirements.txt. you can install them using:

    pip install -r requirements.txt
 
 **Run**

To run project:

    1. put your input data in data.csv, you can adjust parameters.
    2. execute python main.py
    3. execute python gantt.py to draw gantt pics of of your result.

