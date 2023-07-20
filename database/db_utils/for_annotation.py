query_dact = """Given the utterance, predict the relevant dialogue act: describe, sql, plan, analyze

describe - occurs when the user wants to know more about the available columns or other meta-data
sql - directly querying the table using SQL with an aggregation, filter, group or sort
plan - projects into possible futures that are not strictly based on information inside the table
analyze - perform exploratory analysis where table details are not well specified
unsure - means the utterance does not fit into any of the above four options

Predict 'unsure' when the dialogue act is ambiguous or unclear.
Otherwise, your response should only be a single token that is either describe, sql, plan, or analyze with no other words.

Utterance: What columnns are in the purchases table?
Prediction: describe

Utterance: Does the user column stand for users who signed up or users who paid?
Prediction: describe

Utterance: How many rows does the orders table have?
Prediction: describe

Utterance: Is viewer a string or number?
Prediction: describe

Utterance Show me the top ROI campaigns from each month
Prediction: sql
      
Utterance: Who are the top agents by sales region?
Prediction: sql

Utterance: How much money did we make in November?
Prediction: sql

Utterance: what was the highest selling shoe brand?
Prediction: sql

Utterance: which landing pages led to the highest conversions last week
Prediction: sql

Utterance: How does that compare to the previous month?
Prediction: sql

Utterance: Let's look at this by shape instead.
Prediction: sql

Utterance: What if I lowered spend by 10%
Prediction: plan

Utterance: How would it look if we increased the budget
Prediction: plan

Utterance: Given the current trend, what will next month look like?
Prediction: plan

Utterance: Suppose we had 10% more volume, how would that change things?
Prediction: plan

Utterance: what is the correlation between ad spend and roas for this campaign?
Prediction: analyze

Utterance: Anything in this email data you can tell me about that’s interesting?
Prediction: analyze

Utterance: Can you help me identify any trends about sales volume
Prediction: analyze

Utterance: What else can you tell me about this data?
Prediction: analyze

Utterance: {utterance}
Prediction:"""

operations_prompt = """Given the previous state and current utterance, first predict whether the dialogue is carried over from the prior turn.
Next, predict the aggregation type. The aggregation represents what final SQL function is applied to the key column.
It must start with sum, count, average, min, max, top, bottom, std_dev, median, percentile, or all.
If the utterance mentions the best or worst of a single item, the aggregation will be 'max' or 'min', respectively.
On the other hand, if best or worst does not have an associated value, assume the aggregation is 'top 7' or 'bottom 7', respectively.
If no aggregation function is applied, then return 'all' which is the equivalent of a SELECT *

Finally, predict any operations that are applied: filter, group, sort.
filter - limiting the rows returned to match a criteria or range of values
sort - sorting a column to establish order or ranking, frequently to find top values
group - segmenting or grouping the data in some fashion, including pivot tables
none - means the utterance does not fit into any combination of the above three options
Predict 'none' when there are no operations. Otherwise, your response should be a series of short phrases starting with either 'filter', 'group', or 'sort'

Previous state: None
User utterance: Which ad campaign has the highest engagement on social media?
Carry: False
Aggregation: max campaign
Operations: filter by social media, group by campaign, sort by engagement

Previous state:
* Tables: orders, transactions
* Columns: sign ups, channel from orders; date from transactions
* Aggregation: count of sign ups
* Operations: filter month is June, filter by newletter
* Agent utterance: 3,511 sign ups came from newsletters.
User utterance: How many came from email?
Carry: True
Aggregation: count of sign ups
Operations: filter month is June, filter by email

Previous state: None
User utterance: What was the total spend on GA for last week?
Carry: False
Aggregation: sum of spend
Operations: filter for last week, group by GA

Previous state:
* Tables: campaigns, orders
* Columns: revenue, name from campaigns; month, year from orders
* Aggregation: max campaign name
* Operations: group by quarter, sort by revenue
* Agent utterance: These are the best campaigns for each quarter.
User utterance: let's see the worst ones
Carry: True
Aggregation: min campaign name
Operations: group by quarter, sort by revenue

Previous state:
* Tables: sales
* Columns: month, revenue, brand in sales
* Aggregation: sum of revenue
* Operations: filter month is January, filter for Perry Ellis 
* Agent utterance: We generated $5,608 from Perry Ellis in January.
User utterance: What are the worst campaigns for each month.
Carry: False
Aggregation: bottom 7 campaigns
Operations: group by month, sort by revenue

Previous state:
* Tables: activities, orders
* Columns: clicks, impressions in activities; month, year in orders
* Aggregation: average click-through rate
* Operations: group by month
* Agent utterance: Here is the click-through rate broken down by month.
User utterance: What is the conversion rate?
Carry: True
Aggregation: average conversion rate
Operations: group by month

Previous state:
* Tables:
* Columns:
* Aggregation:
* Operations:
* Agent utterance: Ok, how does this look?
User utterance: Looks good!  What are the three best campaigns each week by CVR?
Carry: True
Aggregation: top 3 campaigns
Operations: group by week, sort by CVR

Previous state:
* Tables: orders, products
* Columns: month, year, price in August; brand in products
* Aggregation: sum of price
* Operations: filter month is August, filter for Adidas brand
* Agent utterance: We made $494 in revenue in August.
User utterance: How much did we make the month before?
Carry: True
Aggregation: sum of price
Operations: filter month is July, filter for Adidas brand

Previous state:
* Tables:
* Columns:
* Aggregation:
* Operations:
* Agent utterance:
User utterance: Display the records of employees with a salary over $50,000.
Carry: True
Aggregation: all employees
Operations: filter for salary > 50000

Previous state:
* Tables: campaigns, activities
* Columns: name in campaigns; day, channel, action in activities
* Aggregation: average of opens
* Operations: filter for Bountiful Harvest, filter channel is email, group by day
* Agent utterance: We have an average of 617 email opens from the Bountiful Harvest campaign each day.
User utterance: How many opens did we get on the Soft Touch drip campaign.
Carry: True
Aggregation: average of email opens
Operations: filter for Soft Touch, filter channel is email, group by day

Previous state:
* Tables: sales, customers
* Columns: year, order_amount in sales; first_name, last_name in customers
* Aggregation: max customer
* Operations: filter year is 2023, group by first_name and last_name, sort by order_amount
* Agent utterance: The customer who bought the most this year is Angela Davis, who has spent $2,533.
User utterance: What was her average order size?
Carry: True
Aggregation: average order_amount
Operations: filter year is 2023, filter first_name is Angela, filter last_name is Davis

Previous state: None
User utterance: Who are in the top 10 percent of sales agents by region?
Carry: False
Aggregation: percentile of sales
Operations: filter for top 10%, group by region, sort by sales

Previous state:
* Tables: orders, activities
* Columns: month, year, channel in orders; clicks, impressions in activities
* Aggregation: min channel
* Operations: filter year is 2022, filter month is January, group by channel, sort by CTR
* Agent utterance: affiliate_display had the lowest CTR this month.
User utterance: Which channel was the lowest last month?
Carry: True
Aggregation: min channel
Operations: filter year is 2021, filter month is December, group by channel, sort by CTR

Previous state:
* Tables: orders
* Columns: day, product_id, price in orders
* Aggregation: max price
* Operations: filter day is yesterday, sort by price
* Agent utterance: The most expensive shoe sold yesterday was $4270 with product_id 5972.
User utterance: Can you change the price for the shoe from $4270 to $42.70?
Carry: True
Aggregation: max price
Operations: filter day is yesterday, sort by price

Previous state:
* Tables: orders, activities
* Columns: day in orders; channel, conversion, clicks in activities
* Aggregation: bottom 7 channels
* Operations: filter for past few days, group by channel, sort by conversion rate
* Agent utterance: Bing, CJ and Tiktok have the worst conversion rates recently.
User utterance: Which channels have the best conversion rates?
Carry: True
Aggregation: top 7 channels
Operations: filter for past few days, group by channel, sort by conversion rate

{previous_state}
User utterance: {utterance}
Carry:"""

manipulate_dact = """Given the utterance, predict the dialogue act: clean, delete, or format.
clean - changing, updating or creating data, either from a direct command or based on values from other cells through a formula
delete - removing or hiding rows or columns, often based on some criteria
format - style the contents of the table, such as resizing column width, converting strings to numbers, or centering text
unsure - means the utterance does not fit into any of the above three options

Predict 'unsure' when the dialogue act is ambiguous or unclear.
Otherwise, your response should only be a single token that is either clean, delete, or format with no other words.

Utterance: Let's create a column that infers the country, given the state
Prediction: clean

Utterance: Add a formula for click thrus which is visits divided by impressions
Prediction: clean

Utterance: let's make them all lowercase
Prediction: clean

Utterance: Can you change all channels tagged ga into Google Analytics?
Prediction: clean

Utterance: There should be no spaces, let's change them to underscores
Prediction: clean

Utterance: Can you drop all rows that are empty?
Prediction: delete

Utterance: Please remove all users which don't have a last name.
Prediction: delete

Utterance: Please get rid of the Unnamed column.
Prediction: delete

Utterance: Bold the first row
Prediction: format

Utterance: The row is related to money, so there should be two decimals
Prediction: format

Utterance: Let's make the column centered
Prediction: format

Utterance: we can add a double border to the bottom
Prediction: format

Utterance: {utterance}
Prediction:"""

report_dact = """Given the utterance, predict the dialogue act: visualize, style, explain.
visualize - create a figure, chart or diagram from the data
style - any design or formatting elements to update an existing figure or chart
explain - write out any text, such as summarizing information presented within a figure
unsure - means the utterance does not fit into any of the above three options

Predict 'unsure' when the dialogue act is ambiguous or unclear.
Your response should only be a single token that is either visualize, style, or explain with no other words.

Utterance: Can you display the click through rate as a figure.
Prediction: visualize

Utterance: Show me a breakdown of the costs by shoe size.
Prediction: visualize

Utterance: Plot how many pairs were sold in March, broken down by shoe brand.
Prediction: visualize

Utterance: Create a bar chart of the number of sales by region.
Prediction: visualize

Utterance: Make the figure a line chart instead.
Prediction: style

Utterance: Let's change the title to something a bit shorter.
Prediction: style

Utterance: Can we rotate the X and Y axis?
Prediction: style

Utterance: Move the legend to the top left.
Prediction: style

Utterance: Can we create a report from all the visualizations?
Prediction: unsure

Utterance: Can you write a short description of the chart?
Prediction: explain

Utterance: What's a good summary of the figure?
Prediction: explain

Utterance: Let's write out the main insight below.
Prediction: explain

Utterance: {utterance}
Prediction:"""


converse_dact = """Given the utterance, predict the dialogue act: chat, help, or signal.
chat - talking about non-data related subjects, so the response does not need to query the table.  Answers may be based on opinion, and can change for one person to another.
help - getting a better understanding of what the service entails, answering questions found in a FAQ.  Unlike 'chat', the answers to 'help' questions are broadly applicable to all customers.
signal - represents when the user is backchanneling, such as acknowledging progress or expressing dissatisfaction. Also, any miscellaneous fragments that do not warrant a response.
unsure - means the utterance does not fit into any of the above three options

Predict 'unsure' if the dialogue act is ambiguous or unclear.
Otherwise, your response should only be a single token that is either chat, help, or signal with no other words.

Utterance: Hello! How are you?
Prediction: chat

Utterance: Did you read that article about data science?
Prediction: chat

Utterance: What can you tell me about industry trends?
Prediction: chat

Utterance: What's the most interesting insight you've found lately?
Prediction: chat

Utterance: Are you able to help me analyze my campains?
Prediction: help

Utterance: How much does this service cost?
Prediction: help

Utterance: What data sources do you support?
Prediction: help

Utterance: Can you help me clean my data?
Prediction: help

Utterance: Great, this is exactly what I was looking for
Prediction: signal

Utterance: Now that's interesting
Prediction: signal

Utterance: Hmm, that's not quite what I was looking for
Prediction: signal

Utterance: Ok, that works too
Prediction: signal

Utterance: {utterance}
Prediction:"""

intent_prompt = """Given the utterance, predict the intent: query, manipulate, display or converse.
'query' intent is to query the data, including describing tables, aggregation, filtering and grouping.
'manipulate' intent is to make changes to the underlying data, such as updating or removing rows.
'display' intent is to visualize data by creating a bar chart or figure.
'converse' intent is to talk about non-data related subjects, such as chit chat.

Your response should only be a single token that is either query, manipulate, display, or converse with no other words.

Utterance: How much money did we make in September?
Prediction: query

Utterance: How are the channels doing?
Prediction: query

Utterance: Can you change all channels tagged ga as Google Analytics?
Prediction: manipulate

Utterance: Please remove all user rows which don't have a last name.
Prediction: manipulate

Utterance: Can you display the click through rate as a figure.
Prediction: display

Utterance: Show me a breakdown of the costs by shoe size.
Prediction: display

Utterance: Plot how many pairs were sold in March, broken down by shoe brand.
Prediction: display

Utterance: Hello! How are you?
Prediction: converse

Utterance: Thanks, that's all I need
Prediction: converse

Utterance: What can you do?
Prediction: converse

Utterance: Are you a human?
Prediction: converse

Utterance: {utterance}
Prediction:"""


table_and_col_prompt = """Given the previous dialogue state and the current user utterance, construct a thought about what tables and columns are relevant.
Then output the answers to the following questions:
* Choosing from the existing tables, what table(s) do you need to query? If it is unclear what tables are being discussed, output 'unsure.'
* Choosing from the existing columns, what columns from these tables are being used or updated? Connect the different tables by a semicolon. If it is unclear what columns to use, output 'unsure.'
* If there is uncertainty in the table or columns, write a clarifying question that would help resolve the ambiguity. If there is no ambiguity, put 'N/A'.

Pay attention to the previous dialogue state, which includes the prior agent utterance, since the current user utterance may be referring to a previous request.
Think step by step, and take into account the dialogue history. You can sometimes infer ambiguous tables and columns from the history.

Previous state: None
User utterance: How much money did we make between April and June?
Thought: The orders table has a price column, which can be used to calculate revenue. Orders also has a month column, so I can filter it for months between April and June.
Output:
* Tables: orders
* Columns: price, month in orders
* Ambiguity: N/A

Previous state: None
User utterance: How are the channels doing in March?
Thought: The orders table has a channels column. However, the question is underspecified. If we are looking at order volume, we just need the channels column. If we are looking at revenue, we will also need the price column. To resolve this ambiguity, I should ask how the user wants to define performance.
Output:
* Tables: orders
* Columns: month, channel, price in orders
* Ambiguity: When it comes to performance, do you care about revenue or order volume?

Previous state:
* Tables: orders
* Columns: month, product_id in orders
* Aggregation: count of product_id
* Operations: group by month
* Agent utterance: Sure, how does this look?
User utterance: Looks great, can we show this as a bar chart instead.  Also limit to just 1995.
Thought: The user is changing her previous query, so I will carry over the tables and columns from the previous turn.  I will also need to add a year, which can be found in the orders table.
* Tables: orders
* Columns: month, year, product_id in orders
* Ambiguity: N/A

Previous state:
* Tables: orders, customers
* Columns: order_id, month, year in orders; state in customers
* Aggregation: top 7 of order_id
* Operations: filter month is between January and March, year is 2023, group by state, sort by count of order_id
* Agent utterance: These are the states which had the most orders this quarter.
User utterance: What state generated the most costs last quarter?
Thought: The customers table includes a state column, which is needed for grouping by state.  The products table has a cost column for determining costs. The orders table also has month and year columns, which can be used to infer the time period of a quarter.
Output:
* Tables: customers, products, orders
* Columns: state in customers; month, year in orders; cost in products
* Ambiguity: N/A

Previous state:
* Tables: orders, products
* Columns: price, month in orders; brand in products
* Aggregation: sum of price
* Operations: filter by November, filter brand is Gap, sort by price
* Agent utterance: We made $2,789 in November from Gap clothing.
User utterance: How much did we make the month before?
Thought: The orders table has a price column, which can be used to calculate amount made. I need to find a specific month, also in the orders table.  Since the user is making a comparison, I should carry over the brand column too.
Output:
* Tables: orders, products
* Columns: price, month in orders; brand in products
* Ambiguity: N/A

Previous state:
* Tables: orders, customers
* Columns: customer_id, month, year in orders; customer_id, first_name, last_name in customers
* Aggregation: max of customer_id
* Operations: filter by September, filter by 2022, group by first_name and last_name, sort by count of customer_id
* Agent utterance: Stephanie Adams bought the most shoes in September.
User utterance: What shoe brands did she buy?
Thought: The products table can tell me what brand of shoes were bought. I also need to filter by month and year, which I have in the previous state. I will also need to carry over the first_name and last_name columns to reference the same customer.
Output:
* Tables: products, orders, customers
* Columns: product_id, brand in products; product_id, customer_id, month, year in orders; customer_id, first_name, last_name in customers
* Ambiguity: N/A

Previous state: None
User utterance: The channel values with Google are wrong. Should be lowercase with the type in front, like search_google.
Thought: I should use the orders table, since it contains a channel column.
Output:
* Tables: orders
* Columns: channel in orders
* Ambiguity: N/A

Previous state:
* Tables: customers
* Columns: member in customers
* Aggregation: all
* Operations: filter for member is False
* Agent utterance: Ok, they have been removed.
User utterance: Let's remove all the small ones too.
Thought: The orders table has a size column, but we are currently discussing the customers table.  I will need to put 'unsure' for Table.  The values in orders.size are also nominal and not ordinal, so there is no 'small' size. To resolve this ambiguity, I should ask what the user means by 'small'.
Output:
* Tables: unsure
* Columns: size in orders, member in customers
* Ambiguity: What do you mean by small here? The sizes in the Orders table are numbers.

Previous state:
* Tables: orders
* Columns: product_id, price in orders
* Aggregation: max of price
* Operations: sort by price
* Agent utterance: The most expensive shoe was $4270 with order_id 1120972.
User utterance: Can you change the price for the shoe from $4270 to $42.70?
Thought: The user is updating a row from the previous query, so I will carry over the tables and columns from the previous turn.
Output:
* Tables: orders
* Columns: product_id, price in orders
* Ambiguity: N/A

Previous state:
* Tables: orders
* Columns: channel in orders
* Aggregation: None
* Operations: None
* Agent utterance: There are 29 distinct marketing channels.
User utterance: What about the ones with the most orders?
Thought: We want to find the top channels with the most orders, so I will need to carry over the orders table.  I will also need to carry over the channel column, since we are still discussing channels.
Output:
* Tables: orders
* Columns: channel in orders
* Ambiguity: N/A

Previous state:
* Tables: orders
* Columns: month, year, price in orders
* Aggregation: average over prices
* Operations: filter for month is September, filter for 2022
* Agent utterance: The average price of shoes sold in September was $84.
User utterance: Can you plot that for every month in the year?
Thought: The user is creating a visualization of the previous query, so the same columns will still apply.
Output:
* Tables: orders
* Columns: month, year, price in orders
* Ambiguity: N/A

Previous state:
* Tables: orders
* Columns: * in orders
* Aggregation: None
* Operations: None
* Agent utterance: The orders table contains order_id, product_id, customer_id, date, channel, price, and size.
User utterance: What about the customers table?
Thought: The user is following up to the previous question, so she want to know what columns are in the customers table.  I will need all the columns, which is represented by '*'.
Output:
* Tables: customers
* Columns: * in customers
* Ambiguity: N/A

{previous_state}
User utterance: {utterance}
Thought:"""

fake_tab_col = """Given a short conversation spoken between a Marketing Manager and a Data Analyst, consider what columns and tables are needed.
Generate a list of possible columns that were used answer the question, followed by the tables they belong to. Column-table pairings should be seperated by semi-colons.

For example,
#############
Manager: How much did we make the month before?
Analyst: We made $2,789 in November from Gap clothing.
Columns: retailer in vendors; revenue in orders; month in activities; year in activities

#############
Manager: Which marketing channel had the most orders?
Analyst: The Tiktok channel had the most orders.
Columns: order_id in orders; channel in orders

#############
Manager: Did the discount boost sales at all?
Analyst: Yes, the discount boosted sales for the cohort by 8.34%.
Columns: discount_applied in orders; total_sales in orders; month in orders; day in orders; cohort_id in orders; cohort in ab_tests

#############
Manager: The referrer values with Google are wrong. Should be lowercase with the type in front, like search_google.
Analyst: Ok, they have been removed.
Columns: referrer in traffic

#############
Manager: What was the largest purchase in October?
Analyst: The most expensive purchase was $896 with order_id 1120972.
Columns: month in transactions; transaction_id in orders; order_id in orders; order_amount in orders

#############
Manager: Can you change the price for the shirt from $5611 to $56.11?
Analyst: Sure, it's been updated.
Columns: product_type in products; price in products

#############
Manager: What was the average price of shoes sold in September?
Analyst: The average price of shoes sold in September was $84.
Columns: month in orders; year in orders; price in products

#############
Manager: Let's filter to just the sign-ups between Friday and Sunday of last week.
Analyst: OK, these are the email sign-ups in that time period.
Columns: day_of_week in campaigns; month in campaigns; signed_up in campaigns; source in campaigns

#############
{chat}"""


# 1) standard query - filter
# 2) query with ambiguity - filter
# 3) query with carryover - filter, group
# 4) calculating time - filter, group, sort
# 5) carryover and time calculation - filter, sort
# 6) carryover of user - filter, sort
# 7) standard manipulate - clean
# 8) manipulate with ambiguity - delete
# 9) manipulate with carryover - clean
# 10) Without agg and operations
# 11) sarndard report - visualize
# 12) standard direct - describe