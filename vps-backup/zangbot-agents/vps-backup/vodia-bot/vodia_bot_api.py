"""
Vodia Bot - Web API Service
Provides REST API endpoints for bot operations
"""

import os
import json
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, make_response
from vodia_bot import VodiaBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """API error response."""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


def create_app():
    """Create and configure Flask app."""
    
    app = Flask(__name__)
    
    # Initialize bot
    bot = VodiaBot()
    
    # Middleware for error handling
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            'error': error.message,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(response), error.code
    
    @app.errorhandler(500)
    def handle_500(error):
        response = {
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(response), 500
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Metrics endpoint."""
        return jsonify(bot.get_status()), 200
    
    # Domain endpoints
    @app.route('/api/domains', methods=['GET'])
    def list_domains():
        """List all domains."""
        domains = bot.list_domains()
        if not domains:
            raise APIError('No domains found', 404)
        
        return jsonify({
            'count': len(domains),
            'domains': domains,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # Extension endpoints
    @app.route('/api/extensions', methods=['GET'])
    def list_extensions():
        """List extensions in domain."""
        domain = request.args.get('domain', bot.default_domain)
        
        extensions = bot.list_extensions(domain)
        if extensions is None:
            raise APIError(f'Domain not found: {domain}', 404)
        
        return jsonify({
            'domain': domain,
            'count': len(extensions),
            'extensions': extensions,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/extensions/<ext>', methods=['GET'])
    def get_extension(ext):
        """Get extension details."""
        domain = request.args.get('domain', bot.default_domain)
        
        account = bot.get_account(ext, domain)
        if not account:
            raise APIError(f'Extension not found: {ext}', 404)
        
        return jsonify({
            'extension': ext,
            'domain': domain,
            'details': account,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/extensions', methods=['POST'])
    def create_extension():
        """Create new extension."""
        data = request.get_json()
        
        if not data or 'ext' not in data:
            raise APIError('Missing required field: ext', 400)
        
        ext = data['ext']
        domain = data.get('domain', bot.default_domain)
        
        success = bot.create_ring_group(ext, domain)
        if not success:
            raise APIError(f'Failed to create extension: {ext}', 500)
        
        return jsonify({
            'extension': ext,
            'domain': domain,
            'created': True,
            'timestamp': datetime.now().isoformat()
        }), 201
    
    @app.route('/api/extensions/<ext>', methods=['PUT'])
    def update_extension(ext):
        """Update extension."""
        data = request.get_json()
        domain = request.args.get('domain', bot.default_domain)
        
        if not data:
            raise APIError('No data provided', 400)
        
        success = bot.update_account(ext, domain, **data)
        if not success:
            raise APIError(f'Failed to update extension: {ext}', 500)
        
        return jsonify({
            'extension': ext,
            'domain': domain,
            'updated': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/extensions/<ext>', methods=['DELETE'])
    def delete_extension(ext):
        """Delete extension."""
        domain = request.args.get('domain', bot.default_domain)
        
        success = bot.delete_account(ext, domain)
        if not success:
            raise APIError(f'Failed to delete extension: {ext}', 500)
        
        return jsonify({
            'extension': ext,
            'domain': domain,
            'deleted': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # Ring group endpoints
    @app.route('/api/ring-groups', methods=['GET'])
    def list_ring_groups():
        """List ring groups in domain."""
        domain = request.args.get('domain', bot.default_domain)
        
        groups = bot.list_ring_groups(domain)
        if groups is None:
            raise APIError(f'Domain not found: {domain}', 404)
        
        return jsonify({
            'domain': domain,
            'count': len(groups),
            'ring_groups': groups,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/ring-groups/<group_id>', methods=['GET'])
    def get_ring_group(group_id):
        """Get ring group details."""
        domain = request.args.get('domain', bot.default_domain)
        
        account = bot.get_account(group_id, domain)
        if not account:
            raise APIError(f'Ring group not found: {group_id}', 404)
        
        return jsonify({
            'ring_group': group_id,
            'domain': domain,
            'details': account,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/ring-groups', methods=['POST'])
    def create_ring_group():
        """Create new ring group."""
        data = request.get_json()
        
        if not data or 'ring_group' not in data:
            raise APIError('Missing required field: ring_group', 400)
        
        ring_group = data['ring_group']
        domain = data.get('domain', bot.default_domain)
        
        success = bot.create_ring_group(ring_group, domain)
        if not success:
            raise APIError(f'Failed to create ring group: {ring_group}', 500)
        
        return jsonify({
            'ring_group': ring_group,
            'domain': domain,
            'created': True,
            'timestamp': datetime.now().isoformat()
        }), 201
    
    @app.route('/api/ring-groups/<group_id>', methods=['PUT'])
    def update_ring_group(group_id):
        """Update ring group."""
        data = request.get_json()
        domain = request.args.get('domain', bot.default_domain)
        
        if not data:
            raise APIError('No data provided', 400)
        
        success = bot.update_account(group_id, domain, **data)
        if not success:
            raise APIError(f'Failed to update ring group: {group_id}', 500)
        
        return jsonify({
            'ring_group': group_id,
            'domain': domain,
            'updated': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/ring-groups/<group_id>', methods=['DELETE'])
    def delete_ring_group(group_id):
        """Delete ring group."""
        domain = request.args.get('domain', bot.default_domain)
        
        success = bot.delete_account(group_id, domain)
        if not success:
            raise APIError(f'Failed to delete ring group: {group_id}', 500)
        
        return jsonify({
            'ring_group': group_id,
            'domain': domain,
            'deleted': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # Webhook endpoints
    @app.route('/webhooks/unifi', methods=['POST'])
    def webhook_unifi():
        """Receive webhooks from UniFi Bot."""
        data = request.get_json()
        
        logger.info(f"Webhook received from UniFi: {data}")
        
        # Example: Device joined network → provision extension
        if data.get('event') == 'device_joined':
            device_id = data.get('device')
            logger.info(f"Device joined: {device_id}")
        
        return jsonify({
            'status': 'received',
            'timestamp': datetime.now().isoformat()
        }), 202
    
    @app.route('/webhooks/vodia', methods=['POST'])
    def webhook_vodia():
        """Receive webhooks from Vodia system."""
        data = request.get_json()
        
        logger.info(f"Webhook received from Vodia: {data}")
        
        return jsonify({
            'status': 'received',
            'timestamp': datetime.now().isoformat()
        }), 202
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Load configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("=" * 80)
    logger.info(f"Starting Vodia Bot Web API on {host}:{port}")
    logger.info("=" * 80)
    
    app.run(host=host, port=port, debug=debug)
