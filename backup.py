from flask import Blueprint, jsonify, request
from src.models.user import User, Backup, db
from src.routes.user import token_required
from datetime import datetime

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/backup', methods=['POST'])
@token_required
def save_backup(current_user):
    try:
        data = request.json
        backup_data = data.get('data')
        
        if not backup_data:
            return jsonify({'message': 'Dados de backup são obrigatórios'}), 400
        
        # Verificar se já existe um backup para este usuário
        existing_backup = Backup.query.filter_by(user_id=current_user.id).first()
        
        if existing_backup:
            # Atualizar backup existente
            existing_backup.set_data(backup_data)
            existing_backup.updated_at = datetime.utcnow()
        else:
            # Criar novo backup
            backup = Backup(user_id=current_user.id)
            backup.set_data(backup_data)
            db.session.add(backup)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Backup salvo com sucesso',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao salvar backup: {str(e)}'}), 500

@backup_bp.route('/backup', methods=['GET'])
@token_required
def get_backup(current_user):
    try:
        backup = Backup.query.filter_by(user_id=current_user.id).first()
        
        if not backup:
            return jsonify({
                'message': 'Nenhum backup encontrado',
                'data': None
            }), 404
        
        return jsonify({
            'message': 'Backup recuperado com sucesso',
            'data': backup.get_data(),
            'created_at': backup.created_at.isoformat() if backup.created_at else None,
            'updated_at': backup.updated_at.isoformat() if backup.updated_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao recuperar backup: {str(e)}'}), 500

@backup_bp.route('/backup', methods=['DELETE'])
@token_required
def delete_backup(current_user):
    try:
        backup = Backup.query.filter_by(user_id=current_user.id).first()
        
        if not backup:
            return jsonify({'message': 'Nenhum backup encontrado'}), 404
        
        db.session.delete(backup)
        db.session.commit()
        
        return jsonify({'message': 'Backup deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao deletar backup: {str(e)}'}), 500

@backup_bp.route('/backup/info', methods=['GET'])
@token_required
def get_backup_info(current_user):
    try:
        backup = Backup.query.filter_by(user_id=current_user.id).first()
        
        if not backup:
            return jsonify({
                'exists': False,
                'message': 'Nenhum backup encontrado'
            }), 200
        
        return jsonify({
            'exists': True,
            'created_at': backup.created_at.isoformat() if backup.created_at else None,
            'updated_at': backup.updated_at.isoformat() if backup.updated_at else None,
            'message': 'Backup encontrado'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao verificar backup: {str(e)}'}), 500

