from registration.forms import RegistrationFormUniqueEmail
from django.forms.fields import CharField
from hellouser.models import MyUser


class UpdatedRegistrationForm(RegistrationFormUniqueEmail):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=30)
    address = CharField(max_length=30)
    address_optional = CharField(max_length=30, required=False)
    country = CharField(max_length=30)
    city = CharField(max_length=30)
    zip = CharField(max_length=30)
    shipping_address = CharField(max_length=30, required=False)
    shipping_address_optional = CharField(max_length=30, required=False)
    shipping_country = CharField(max_length=30,required=False)
    shipping_city = CharField(max_length=30, required=False)
    shipping_zip = CharField(max_length=30, required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UpdatedRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.address = self.cleaned_data['address']
        user.address_optional = self.cleaned_data['address_optional']
        user.country = self.cleaned_data['country']
        user.city = self.cleaned_data['city']
        user.zip = self.cleaned_data['zip']
        user.shipping_address = self.cleaned_data['shipping_address']
        user.shipping_address_optional = self.cleaned_data['shipping_address_optional']
        user.shipping_country = self.cleaned_data['shipping_country']
        user.shipping_city = self.cleaned_data['shipping_city']
        user.shipping_zip = self.cleaned_data['shipping_zip']
        if commit:
            user.save()
            return user