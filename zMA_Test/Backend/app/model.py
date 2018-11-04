from mongoengine import *


class session_practice(Document):
    #sessionID = StringField(required=True,max_length=50)
    words = ListField(required=True)
    idx = IntField()
    status = DictField()


class session_test(Document):
    words = ListField(required=True)
    idx = IntField()
    status = DictField()
    ques_multi = ListField()
    ques_blank = ListField()


class user_word_history(Document):
    username = StringField(required=True, primary_key=True)
    status = DictField()



# class Gre_data(Document):
#     username = StringField(required=True, primary_key=True)
#     history = DictField()
#     how_many_test = IntField()
#     best_score = FloatField()
#     avg_score = FloatField()
#     rating = FloatField()