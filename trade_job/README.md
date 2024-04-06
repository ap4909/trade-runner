# Trade Job

## Intro

This directory holds the code and configuration files that are responsible for receiving an API request containing
parameters related to trading a particular stock, retrieving and evaluating data regarding that stock, and then making
automated buy or sell orders based on defined conditions.

## Technical overview

The AWS infrastructure is defined in the `serverless.yaml` file. This defines a REST API endpoint which takes a POST
request and passes the data to a Step Function. The Step Function passes the parameters to a lambda function which
encapsulates the logic of retrieving the stock data, and processing and evaluating it to decide whether an order should
be placed. This execution of the lambda is referred to as a trade "run". Once the run is complete, the Step Function
resumes and schedules another run to start at the beginning of the next minute, and the process begins again. This will
continue until:

- The market closes - all positions are closed
- Either the stop-loss or take-profit limits are reached - at which point all positions are closed
- The Job is manually cancelled by the user - closing of positions is optional

The status of this process is tracked in a database entry. A flowchart of the process is shown below:

![Alt text here](images/workflow.svg)

More details on the steps in the process are explained below.

### Client device => API Gateway
A JSON payload is sent in the form of a POST request, and contains the information regarding a stock and the parameters to be used when evaluating whether to make a buy or sell order. The details on these parameters are given below:
```
symbol - Required, stock Symbol to be traded
offsetTime - Look back time in minutes of the evaluation window to set when retrieving data. Default 16
windowLength - evaluation window size, minutes. Default 5
minimumPoints - minimum points required to be in a window for the data to be evaluated. Default 3
stopLoss - Default null
takeProfit - Default null
```
Default values will be set in the Step Function if not defined.

### Step function
The Step Function first the default values for any parameter which has not been set. It then passes this to the Lambda function. The Lambda will complete it's run, which will evaluate the data and either make a buy, sell order or do nothing.

Once the Lambda has finished its run, the output is passed back to the step function which then either schedules the next run or stops the job.

### Lambda Function
The Lambda function:
- Retrieves the Stock bar data available for the defined window from the Alpaca API
- Evaluates the moving average over the time window and the last available price to it
  - if the last price is above the average, a buy market order is made 
  - if the last price is below the average, and a position is currently held, a sell market order is made
  - if none of these conditions are fulfilled, then no action will be taken

## Running the workflow
An example payload with all parameters is given below:

```
       {
        "symbol": "AAPL", // required
        "offsetTime": 16, // required, look back time in minutes of the evaluation window to set when retrieving data. 
        Defaults to 16 as Alpaca API free version has a 15 min delay on latest available data
        "windowLength": 5 // required, 
        "minimumPoints": 3, // minimum points required to be in a window for the data to be evaluated
        "stopLoss": null,
        "takeProfit": null
       }
```

