import random
import string


from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField

class RandomB64Field(CharField):
    
    def __init__(self, auto=False, *args, **kwargs):
        self.auto = auto
        # We store IDs in base64 format, which is fixed at 11 characters.
        kwargs['max_length'] = 11
        kwargs['blank'] = False

        if auto:
            # Do not let the user edit IDs if they are auto-assigned.
            kwargs['editable'] = False
            
            kwargs['unique'] = True  # if you want to be paranoid, set unique=True in your instantiation of the field.

        super(RandomB64Field, self).__init__(*args, **kwargs)

    def random_string_generator(self):
        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        result=''
        for i in range(0, 11):
            result += random.choice(characters)
        
        return result

    def pre_save(self, model_instance, add):
        """
        This is used to ensure that we auto-set values if required.
        See CharField.pre_save
        """
        value = super(RandomB64Field, self).pre_save(model_instance, add)
  
        
        if self.auto and not value:
            value = self.random_string_generator()
            mymodel =ContentType.objects.get_for_model(model_instance).model_class()

            if mymodel.objects.filter(id=value).exists():
                value = self.random_string_generator()
            
            setattr(model_instance, self.attname, value)
        return value



# def hi():
# from netizen.models import Meme
# from django.contrib.auth import get_user_model
# User = get_user_model()
# u = User.objects.all()[0]
# Meme.objects.create(id="-GaKMCD61cl",user=u)