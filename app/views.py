from app import grosus

@grosus.route('/')
@grosus.route('/index')
def index():
    return "Hello, grosus"
