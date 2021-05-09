import pandas as pd
import numpy as np
from collections import Counter

# Read in data.
data = pd.read_excel("2019 Winter Data Science Intern Challenge Data Set.xlsx")

# Question 1a: Think about what could be going wrong with our calculation.
# Think about a better way to evaluate this data. 
#
# To ensure I'm looking at the right column, verify that AOV is $3145.13.
aov = np.mean(data['order_amount'])
print("AOV is ${0}.".format(aov))

# Now I know for sure I'm looking at the right data. I expect the true AOV
# to be less than the calculated AOV, so we're probably going to want to
# check the data first for potential outliers:

print("Checking data for potential outliers: ")
print(data.sort_values('order_amount', ascending=False).head(25))

# We can see that the user IDs are identical across a number of these high-value
# orders. (Also, who would ever buy 2000 things from a single shop?) I initially
# also wanted to include order total/amount as a way of rejecting suspiscious 
# orders (because why would there be so many high-value orders all at the same
# cost?), but then I remembered that each store only sells one type of shoe, making
# it very possible for two separate orders to land on the same total. Anyways,
# my guess is that there are some high-value sneakers being sold that are warping
# the original average (which could also be totally possible, given that some sneakers
# can fetch crazy prices-- also, some of the highest value orders were all placed
# at the same time, indicating the use of automated buying scripts). At any rate,
# we definitely need to clean out our data a little before using it to calcualte
# any hard numbers.

# Question 1b: What metric would you report for this dataset?
#
# We know that each shop sells one model of shoe. Thus, from any given order, we can
# find how much money a shop charges for a single pair of sneakers. Then, we can
# filter out shops that charge unusually high prices per pair. We can get an idea of
# what prices to consider "unusual" by examining a histogram or calculating the 5th
# and 95th percentiles (two standard deviations away from the mean), assuming the
# data is normally distributed. Then, we can calculate a new, adjusted average.
#
# Also, I should include order time (ie., does a single user place orders
# at the exact same time whenever they order?) as a criterion. You don't expect
# the same user to buy the same quantity of items from the same shop at the same
# time on different days (that's a sure sign of bot usage). As a result, some of
# the data seems particularly artifical, so I'd like to get rid of that.

# Question 1c: What is its value?
#
# First, we compile a list of unique user_ids in the data.
unique_ids = set(data.user_id)
bot_ids = unique_ids.copy()

# Then, we look for users that have been placing orders at the same exact time:
for ID in unique_ids:
      first_entry = True
      orders = data[data.user_id==ID]['created_at']
      order_indices = orders.index
      if len(order_indices) == 1: 
            # ie. they only placed an order once
            # probably not bots-- this lets us remove them
            bot_ids.remove(ID)

      for i in order_indices:
            if first_entry:
                  first_entry = False
                  reference_timestamp = orders[i].strftime("%H:%M:%S")
            else:
                  # note that you can have a different, more sophisticated method of identifying
                  # bots. for an instance, a user with 12 of the same order times and a 13th different
                  # order time would be able to slip past this detection.
                  
                  if orders[i].strftime("%H:%M:%S") != reference_timestamp:
                        # probably not a bot, because these orders are at different times
                        bot_ids.remove(ID)
                        break

# Then, we cut out data from our list of "bot IDs":
data_no_bots = data
for ID in bot_ids:
      data_no_bots = data_no_bots[data.user_id != ID]

# That got rid of the obvious bot who was placing the largest order amounts, but a lot of order
# amounts are still suspisciously high. Notice that these orders are all from the same shop.

# (Note that each shop only sells one model of shoe. We'll assume shops can be uniquely identified
# by their sneaker prices-- or at least the high-value ones, anyways.)
# Next, we examine unit price (price per pair of sneakers):

data_sneaker_prices = data_no_bots.copy()
data_sneaker_prices['sneaker_price'] = data_no_bots.order_amount / data_no_bots.total_items

# Anyways, let's make that histogram to see if anything's up with our sneaker prices:

data_sneaker_prices.hist(column='sneaker_price')

# There's a nasty outlier around 25,000. We can quickly confirm this by printing the max
# value of the sneaker_price column:

print("The max price of any of the sneakers is ${0}.".format(max(data_sneaker_prices.sneaker_price)))

# Compile a list of unit prices by shop:
unit_prices = []
for ID in list(set(data_sneaker_prices.shop_id)):
      orders_from_shop = data_sneaker_prices[data_sneaker_prices.shop_id == ID].sneaker_price

      # just need to append one price per shop
      unit_prices.append(orders_from_shop[orders_from_shop.index[0]])

# Figure out which "sneaker" unit prices (and shops, by extension) we should exclude from our data.
# We assume that sneaker prices are normally distributed.
sneaker_price_mean = np.mean(unit_prices)
sneaker_price_sd = np.std(unit_prices)

lower_bound = sneaker_price_mean - 2 * sneaker_price_sd
upper_bound = sneaker_price_mean + 2 * sneaker_price_sd

print("Our interval for non-unusual sneaker prices is (${0}, ${1})."
      .format(lower_bound, upper_bound))

# Well, that incredibly negative lower bound means nothing in the context of prices, so
# we can set that to zero. Effectively, we now only care about the upper bound on price.
# Also, this interval doesn't capture our outlier, so we can now formally kick it out
# (side note: you can see how much the outlier influenced the bounds):

data_no_price_outliers = data_sneaker_prices[data_sneaker_prices.sneaker_price <= upper_bound]

# Calculate the adjusted AOV:

adjusted_aov = np.mean(data_no_price_outliers.order_amount)
print("Adjusted AOV is ${0}.".format(adjusted_aov))

# An AOV of $302 seems much more reasonable.