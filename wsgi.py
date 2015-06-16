from alveare import create_app
from alveare.common.database import DB

app = create_app(DB)
app_context = app.app_context()
app_context.push()
DB.create_all()
DB.session.commit()
