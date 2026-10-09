from .empleado_routes import empleado_bp
from .proveedor_routes import proveedor_bp
from .cliente_routes import cliente_bp
from .ordenes_routes import ordenes_bp
from .ubicaciones_routes import ubicaciones_bp
from .intervenciones_routes import intervencion_bp
from .clasificacion_ordenes_routes import clasificacion_ordenes_bp
from .compras_routes import compras_bp  
from .usuario_routes import usuario_bp
from .configuraciones_routes import configuraciones_bp
from .servicios_routes import servicios_bp
from .auth_routes import auth_bp

def register_blueprints(app):
    app.register_blueprint(empleado_bp)
    app.register_blueprint(proveedor_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(ubicaciones_bp)
    app.register_blueprint(intervencion_bp)
    app.register_blueprint(clasificacion_ordenes_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(configuraciones_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(auth_bp)
    