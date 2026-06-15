from datetime import datetime

class Meal:
    def __init__(self, data):
        self.id = str(data.get("_id"))
        self.title = data.get("title")
        self.servings = data.get("servings")
        self.ingredients = data.get("ingredients", [])
        self.steps = data.get("steps", [])
        self.heading = data.get("heading")
        self.main_image = data.get("main_image")
        self.energy = data.get("energy")
        self.type = data.get("type")
        self.tags = data.get("tags", [])
        self.allergens = data.get("allergens", [])
        self.price = data.get("price")
        self.createdAt = data.get("createdAt")

    def to_dict(self):
        return {
            "_id": self.id,
            "title": self.title,
            "servings": self.servings,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "heading": self.heading,
            "main_image": self.main_image,
            "energy": self.energy,
            "type": self.type,
            "tags": self.tags,
            "allergens": self.allergens,
            "price": self.price,
            "createdAt": self.createdAt or datetime.utcnow()
        }

def serialize_meal(meal_doc):
    return Meal(meal_doc).to_dict()
