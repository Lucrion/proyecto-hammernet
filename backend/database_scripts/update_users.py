from database import get_db
from models import UsuarioDB

def update_users():
    db = next(get_db())
    try:
        # Actualizar rol de jhan a administrador
        user = db.query(UsuarioDB).filter(UsuarioDB.username == 'jhan').first()
        if user:
            user.role = 'administrador'
            
        # Eliminar usuarios inválidos
        db.query(UsuarioDB).filter(UsuarioDB.username == '[value-3]').delete()
        
        db.commit()
        print('Usuarios actualizados correctamente')
        
        # Mostrar usuarios actualizados
        users = db.query(UsuarioDB).all()
        print('\nUsuarios en la base de datos:')
        for u in users:
            print(f'- {u.username} (rol: {u.role})')
            
    except Exception as e:
        print(f'Error al actualizar usuarios: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    update_users()