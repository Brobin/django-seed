INSTALLED_APPS += (
    "mezzanine.blog",
    "mezzanine.forms",
    "mezzanine.pages",
    "mezzanine.galleries",
    "mezzanine.twitter",
    "mezzanine.mobile",
)

SECRET_KEY="akjdshfdsajhfsalkdjhflakjdshlkjfdsalkjhfaljdshflkjdsahflkjdsahflkjsah"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
  }
}