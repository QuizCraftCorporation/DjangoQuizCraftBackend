from QuizGeneratorModel.quiz_craft_package.quiz_database import QuizDataBase


def singleton(cls):
    instances = {}

    def getinstance(path):
        if cls not in instances:
            instances[cls] = cls(path)
        return instances[cls]

    return getinstance


@singleton
class SearchDB(QuizDataBase):
    pass
