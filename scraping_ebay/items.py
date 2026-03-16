# -*- coding: utf-8 -*-

import scrapy


class ProductItem(scrapy.Item):
    ID = scrapy.Field()
    Name = scrapy.Field()
    Seller_Name = scrapy.Field()
    Status = scrapy.Field()
    Price = scrapy.Field()
    URL = scrapy.Field()
    UPC = scrapy.Field()
    Item_Specifics = scrapy.Field()
    Store_Categories = scrapy.Field()
    Feedback_Topics_This_Item = scrapy.Field()
    Feedback_Topics_All_Items = scrapy.Field()
    Feedback_This_Item = scrapy.Field()
    Feedback_All_Items = scrapy.Field()
    You_May_Also_Like = scrapy.Field()
    Similar_Customers_Also_Bought = scrapy.Field()
    Sellers_Other_Items = scrapy.Field()
    Related_To_This_Item = scrapy.Field()
    Explore_Related_Items = scrapy.Field()
    People_Who_Viewed_Also_Viewed = scrapy.Field()


class SellerItem(scrapy.Item):
    Seller_Name = scrapy.Field()
    Seller_Feedback_Score = scrapy.Field()
    Seller_Positive_Feedback = scrapy.Field()
    Seller_Items_Sold = scrapy.Field()
    Seller_Detailed_Ratings = scrapy.Field()
    Feedback_Total = scrapy.Field()
