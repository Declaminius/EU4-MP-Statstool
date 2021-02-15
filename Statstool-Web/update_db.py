from statstool_web import create_app, db
from statstool_web.models import Savegame

app = create_app()
app.app_context().push()

for savegame in Savegame.query.all():
    savegame.parse_flag0 = True

db.session.commit()
